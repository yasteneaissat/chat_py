import tkinter as tk
from tkinter import messagebox
from typing import Any
from models.utilisateur import Utilisateur
from models.groupe import Groupe
from db.database import get_connection

BG       = "#1e1e2e"
CARD     = "#313244"
ACCENT   = "#89b4fa"
TEXT     = "#cdd6f4"
TEXT_DIM = "#6c7086"
BORDER   = "#45475a"

F_TITLE = ("Segoe UI", 12, "bold")
F_BODY  = ("Segoe UI", 10)
F_SMALL = ("Segoe UI", 9)
F_BTN   = ("Segoe UI", 10, "bold")


class FenetreGroupe(tk.Toplevel):
    """Fenetre de creation de groupe."""

    def __init__(self, parent, utilisateur: Utilisateur):
        super().__init__(parent)
        self.utilisateur = utilisateur
        self.title("Creer un groupe")
        self.geometry("460x380")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.grab_set()
        self._construire_ui()

    def _construire_ui(self):
        tk.Label(self, text="Creer un groupe",
                 font=F_TITLE, bg=BG, fg=ACCENT).pack(pady=(22, 16))

        card = tk.Frame(self, bg=CARD, padx=22, pady=18)
        card.pack(padx=24, fill="x")

        tk.Label(card, text="Nom du groupe",
                 font=F_SMALL, bg=CARD, fg=TEXT_DIM).pack(anchor="w")
        self.entry_nom = self._entry(card)

        tk.Label(card, text="Membres (separes par des virgules)",
                 font=F_SMALL, bg=CARD, fg=TEXT_DIM).pack(anchor="w", pady=(12, 0))
        self.entry_membres = self._entry(card)
        tk.Label(card, text="Vous etes automatiquement ajoute",
                 font=("Segoe UI", 8), bg=CARD, fg=TEXT_DIM).pack(
                     anchor="w", pady=(3, 0))

        btn = tk.Label(self, text="Creer le groupe",
                       font=F_BTN, bg=ACCENT, fg="#1e1e2e",
                       cursor="hand2", padx=12, pady=9,
                       highlightthickness=0, bd=0)
        btn.pack(pady=18, padx=24, fill="x")
        btn.bind("<Button-1>", lambda e: self._creer())
        btn.bind("<Enter>", lambda e: btn.config(bg="#74c7ec"))
        btn.bind("<Leave>", lambda e: btn.config(bg=ACCENT))

    def _entry(self, parent: tk.Frame) -> tk.Entry:
        e = tk.Entry(parent, font=F_BODY,
                     bg="#1e1e2e", fg=TEXT, insertbackground=TEXT,
                     relief="flat", bd=0,
                     highlightthickness=1,
                     highlightbackground=BORDER,
                     highlightcolor=ACCENT)
        e.pack(fill="x", ipady=6, pady=(2, 0))
        return e

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
                cur = conn.cursor(dictionary=True)
                cur.execute(
                    "SELECT id, username, email, cle_publique "
                    "FROM utilisateurs WHERE username = %s",
                    (username,)
                )
                row: Any = cur.fetchone()
                cur.close()
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
