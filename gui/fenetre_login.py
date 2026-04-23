import tkinter as tk
from tkinter import messagebox
from models.utilisateur import Utilisateur


class FenetreLogin(tk.Tk):
    """Fenetre d'authentification (connexion / inscription)."""

    def __init__(self):
        super().__init__()
        self.title("Messagerie Securisee - Connexion")
        self.geometry("360x300")
        self.resizable(False, False)
        self.utilisateur_connecte = None
        self._construire_ui()

    def _construire_ui(self):
        tk.Label(self, text="Messagerie Securisee", font=("Arial", 14, "bold")).pack(pady=16)

        frame = tk.Frame(self)
        frame.pack(padx=30, fill="x")

        tk.Label(frame, text="Nom d'utilisateur").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_username = tk.Entry(frame, width=28)
        self.entry_username.grid(row=0, column=1, pady=4)

        tk.Label(frame, text="Email (inscription)").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_email = tk.Entry(frame, width=28)
        self.entry_email.grid(row=1, column=1, pady=4)

        tk.Label(frame, text="Mot de passe").grid(row=2, column=0, sticky="w", pady=4)
        self.entry_mdp = tk.Entry(frame, width=28, show="*")
        self.entry_mdp.grid(row=2, column=1, pady=4)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=16)
        tk.Button(btn_frame, text="Se connecter", width=14,
                  command=self._connexion).pack(side="left", padx=6)
        tk.Button(btn_frame, text="S'inscrire", width=14,
                  command=self._inscription).pack(side="left", padx=6)

    def _connexion(self):
        username = self.entry_username.get().strip()
        mdp = self.entry_mdp.get()
        if not username or not mdp:
            messagebox.showwarning("Champs vides",
                                   "Remplissez le nom d'utilisateur et le mot de passe.")
            return
        u = Utilisateur.se_connecter(username, mdp)
        if u:
            self.utilisateur_connecte = u
            self.destroy()
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects.")

    def _inscription(self):
        username = self.entry_username.get().strip()
        email = self.entry_email.get().strip()
        mdp = self.entry_mdp.get()
        if not username or not email or not mdp:
            messagebox.showwarning("Champs vides", "Remplissez tous les champs.")
            return
        try:
            u = Utilisateur(username, email)
            u.s_inscrire(mdp)
            messagebox.showinfo("Succes", f"Compte cree pour {username} !")
        except ValueError as e:
            messagebox.showerror("Mot de passe faible", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
