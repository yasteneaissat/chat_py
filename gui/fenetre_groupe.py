import tkinter as tk
from tkinter import messagebox
from models.utilisateur import Utilisateur
from models.groupe import Groupe
from db.database import get_connection


class FenetreGroupe(tk.Toplevel):
    """Fenetre de creation de groupe."""

    def __init__(self, parent, utilisateur: Utilisateur):
        super().__init__(parent)
        self.utilisateur = utilisateur
        self.title("Creer un groupe")
        self.geometry("320x280")
        self.resizable(False, False)
        self._construire_ui()

    def _construire_ui(self):
        tk.Label(self, text="Nom du groupe :").pack(pady=(16, 2))
        self.entry_nom = tk.Entry(self, width=30)
        self.entry_nom.pack()

        tk.Label(self, text="Membres (separes par des virgules) :").pack(pady=(12, 2))
        self.entry_membres = tk.Entry(self, width=30)
        self.entry_membres.pack()
        tk.Label(self,
                 text="(vous etes automatiquement ajoute)",
                 fg="gray",
                 font=("Arial", 8)).pack()

        tk.Button(self, text="Creer le groupe", command=self._creer).pack(pady=16)

    def _creer(self):
        nom = self.entry_nom.get().strip()
        membres_str = self.entry_membres.get().strip()
        if not nom:
            messagebox.showwarning("Champ vide", "Donnez un nom au groupe.")
            return

        membres = [self.utilisateur]
        if membres_str:
            for username in membres_str.split(","):
                username = username.strip()
                if not username:
                    continue
                conn = get_connection()
                row = conn.execute(
                    "SELECT id, username, email, cle_publique "
                    "FROM utilisateurs WHERE username = ?",
                    (username,)
                ).fetchone()
                conn.close()
                if row:
                    u = Utilisateur(row["username"], row["email"])
                    u.id = row["id"]
                    u.cle_publique = row["cle_publique"]
                    membres.append(u)
                else:
                    messagebox.showwarning(
                        "Introuvable", f"Utilisateur '{username}' non trouve.")
                    return

        try:
            Groupe.creer(nom, membres)
            messagebox.showinfo(
                "Succes", f"Groupe '{nom}' cree avec {len(membres)} membres.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
