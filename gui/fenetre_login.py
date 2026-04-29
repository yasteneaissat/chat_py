import tkinter as tk
from tkinter import messagebox
from models.utilisateur import Utilisateur

BG       = "#1e1e2e"
CARD     = "#313244"
ACCENT   = "#89b4fa"
TEXT     = "#cdd6f4"
TEXT_DIM = "#6c7086"
BTN_SEC  = "#45475a"
BORDER   = "#45475a"

F_TITLE = ("Segoe UI", 15, "bold")
F_BODY  = ("Segoe UI", 10)
F_SMALL = ("Segoe UI", 9)
F_BTN   = ("Segoe UI", 10, "bold")


class FenetreLogin(tk.Tk):
    """Fenetre d'authentification (connexion / inscription)."""

    def __init__(self):
        super().__init__()
        self.title("Messagerie Securisee")
        self.geometry("520x480")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.utilisateur_connecte = None
        self._construire_ui()

    def _construire_ui(self):
        tk.Label(self, text="Messagerie Securisee",
                 font=F_TITLE, bg=BG, fg=ACCENT).pack(pady=(28, 4))
        tk.Label(self, text="Connexion ou creation de compte",
                 font=F_SMALL, bg=BG, fg=TEXT_DIM).pack(pady=(0, 16))

        card = tk.Frame(self, bg=CARD, padx=22, pady=18)
        card.pack(padx=28, fill="x")

        tk.Label(card, text="Nom d'utilisateur",
                 font=F_SMALL, bg=CARD, fg=TEXT_DIM).pack(anchor="w")
        self.entry_username = self._entry(card)

        tk.Label(card, text="Email  (inscription uniquement)",
                 font=F_SMALL, bg=CARD, fg=TEXT_DIM).pack(anchor="w", pady=(10, 0))
        self.entry_email = self._entry(card)

        tk.Label(card, text="Mot de passe",
                 font=F_SMALL, bg=CARD, fg=TEXT_DIM).pack(anchor="w", pady=(10, 0))
        self.entry_mdp = self._entry(card, show="*")
        self.entry_mdp.bind("<Return>", lambda e: self._connexion())

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=3, padx=28, fill="x")

        self._bouton(btn_frame, "Se connecter",
                     self._connexion, bg=ACCENT, fg="#1e1e2e",
                     hover=ACCENT).pack(side="left", expand=True, fill="x",
                                        padx=(0, 6))
        self._bouton(btn_frame, "S'inscrire",
                     self._inscription, bg=BTN_SEC, fg=TEXT,
                     hover="#585b70").pack(side="left", expand=True, fill="x")

    def _bouton(self, parent, texte, commande, bg, fg, hover):
        lbl = tk.Label(parent, text=texte, font=F_BTN,
                       bg=bg, fg=fg, cursor="hand2",
                       padx=10, pady=9,
                       highlightthickness=0, bd=0)
        lbl.bind("<Button-1>", lambda e: commande())
        lbl.bind("<Enter>",    lambda e: lbl.config(bg=hover))
        lbl.bind("<Leave>",    lambda e: lbl.config(bg=bg))
        return lbl

    def _entry(self, parent: tk.Frame, show: str = "") -> tk.Entry:
        e = tk.Entry(parent, font=F_BODY,
                     bg="#1e1e2e", fg=TEXT, insertbackground=TEXT,
                     relief="flat", bd=0, show=show,
                     highlightthickness=1,
                     highlightbackground=BORDER,
                     highlightcolor=ACCENT)
        e.pack(fill="x", ipady=6, pady=(2, 0))
        return e

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
        email    = self.entry_email.get().strip()
        mdp      = self.entry_mdp.get()
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
