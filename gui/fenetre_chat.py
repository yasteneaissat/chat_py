import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from models.utilisateur import Utilisateur
from models.conv_privee import ConvPrivee
from db.database import get_connection


class FenetreChat(tk.Tk):
    """Fenetre principale de messagerie."""

    def __init__(self, utilisateur: Utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self.conversation_active = None
        self._convs_data = []
        self.title(f"Messagerie Securisee - {utilisateur.username}")
        self.geometry("700x500")
        self._construire_ui()

    def _construire_ui(self):
        # Panneau gauche : liste des conversations
        left = tk.Frame(self, width=180, bd=1, relief="sunken")
        left.pack(side="left", fill="y")
        tk.Label(left, text="Conversations", font=("Arial", 10, "bold")).pack(pady=6)
        self.liste_convs = tk.Listbox(left, width=22)
        self.liste_convs.pack(fill="both", expand=True, padx=4)
        self.liste_convs.bind("<<ListboxSelect>>", self._selectionner_conv)
        tk.Button(left, text="+ Nouveau message",
                  command=self._nouvelle_conv).pack(pady=4, fill="x", padx=4)
        tk.Button(left, text="+ Creer un groupe",
                  command=self._nouveau_groupe).pack(pady=2, fill="x", padx=4)
        tk.Button(left, text=" Rafraichir",
                  command=self._charger_conversations).pack(pady=2, fill="x", padx=4)

        # Panneau droit : zone de chat
        right = tk.Frame(self)
        right.pack(side="right", fill="both", expand=True)
        self.zone_messages = scrolledtext.ScrolledText(
            right, state="disabled", wrap="word")
        self.zone_messages.pack(fill="both", expand=True, padx=8, pady=8)

        bottom = tk.Frame(right)
        bottom.pack(fill="x", padx=8, pady=4)
        self.entry_msg = tk.Entry(bottom)
        self.entry_msg.pack(side="left", fill="x", expand=True)
        self.entry_msg.bind("<Return>", lambda e: self._envoyer())
        tk.Button(bottom, text="Envoyer",
                  command=self._envoyer).pack(side="right", padx=4)

        self._charger_conversations()

    def _charger_conversations(self):
        self.liste_convs.delete(0, tk.END)
        conn = get_connection()
        rows = conn.execute("""
            SELECT c.id, c.type, c.nom,
                   (SELECT username FROM utilisateurs u
                    JOIN participants p2
                      ON p2.conv_id = c.id AND p2.user_id = u.id
                    WHERE u.id != ? LIMIT 1) as autre
            FROM conversations c
            JOIN participants p ON p.conv_id = c.id AND p.user_id = ?
        """, (self.utilisateur.id, self.utilisateur.id)).fetchall()
        conn.close()
        self._convs_data = []
        for row in rows:
            label = (row["nom"] if row["type"] == "groupe"
                     else (row["autre"] or "?"))
            prefix = "[G]" if row["type"] == "groupe" else "[P]"
            self.liste_convs.insert(tk.END, f"{prefix} {label}")
            self._convs_data.append(dict(row))

    def _selectionner_conv(self, event):
        sel = self.liste_convs.curselection()
        if not sel:
            return
        data = self._convs_data[sel[0]]
        if data["type"] == "privee":
            autre_id = self._get_autre_id(data["id"])
            autre = Utilisateur.get_par_id(autre_id)
            if autre:
                self.conversation_active = ConvPrivee.charger_ou_creer(
                    self.utilisateur, autre)
        elif data["type"] == "groupe":
            from models.groupe import Groupe
            self.conversation_active = Groupe.charger(data["id"])
        self._afficher_messages()

    def _get_autre_id(self, conv_id: int):
        conn = get_connection()
        row = conn.execute(
            "SELECT user_id FROM participants WHERE conv_id = ? AND user_id != ?",
            (conv_id, self.utilisateur.id)
        ).fetchone()
        conn.close()
        return row["user_id"] if row else None

    def _afficher_messages(self):
        if not self.conversation_active:
            return
        rows = self.conversation_active.get_messages(self.utilisateur)
        self.zone_messages.config(state="normal")
        self.zone_messages.delete("1.0", tk.END)
        for row in rows:
            try:
                texte = self.utilisateur._chiffreur.dechiffrer(row["contenu_chiffre"])
                exp = Utilisateur.get_par_id(row["expediteur_id"])
                nom = exp.username if exp else "?"
                self.zone_messages.insert(
                    tk.END, f"[{row['horodatage']}] {nom}: {texte}\n")
            except Exception:
                self.zone_messages.insert(tk.END, "[Message illisible]\n")
        self.zone_messages.config(state="disabled")
        self.zone_messages.see(tk.END)

    def _envoyer(self):
        texte = self.entry_msg.get().strip()
        if not texte or not self.conversation_active:
            return
        try:
            self.conversation_active.envoyer_message(self.utilisateur, texte)
            self.entry_msg.delete(0, tk.END)
            self._afficher_messages()
        except Exception as e:
            messagebox.showerror("Erreur d'envoi", str(e))

    def _nouvelle_conv(self):
        dest_name = simpledialog.askstring(
            "Nouveau message", "Nom d'utilisateur du destinataire :")
        if not dest_name:
            return
        dest_id = self._get_id_par_username(dest_name)
        if not dest_id:
            messagebox.showerror("Erreur", f"Utilisateur '{dest_name}' introuvable.")
            return
        dest = Utilisateur.get_par_id(dest_id)
        self.conversation_active = ConvPrivee.charger_ou_creer(self.utilisateur, dest)
        self._charger_conversations()
        self._afficher_messages()

    def _nouveau_groupe(self):
        from gui.fenetre_groupe import FenetreGroupe
        fg = FenetreGroupe(self, self.utilisateur)
        self.wait_window(fg)
        self._charger_conversations()

    def _get_id_par_username(self, username: str):
        conn = get_connection()
        row = conn.execute(
            "SELECT id FROM utilisateurs WHERE username = ?", (username,)).fetchone()
        conn.close()
        return row["id"] if row else None
