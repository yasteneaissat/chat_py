import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from typing import Any
from datetime import datetime
from models.utilisateur import Utilisateur
from models.conv_privee import ConvPrivee
from db.database import get_connection

BG        = "#1e1e2e"
SIDEBAR   = "#181825"
CARD      = "#313244"
ACCENT    = "#89b4fa"
TEXT      = "#cdd6f4"
TEXT_DIM  = "#6c7086"
BTN_SEC   = "#45475a"
BORDER    = "#45475a"
EPH_CLR   = "#f9e2af"

F_TITLE = ("Segoe UI", 11, "bold")
F_BODY  = ("Segoe UI", 10)
F_SMALL = ("Segoe UI", 9)
F_BTN   = ("Segoe UI", 9, "bold")
F_MSG   = ("Segoe UI", 10)


class FenetreChat(tk.Tk):
    """Fenetre principale de messagerie."""

    def __init__(self, utilisateur: Utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self.conversation_active = None
        self._convs_data = []
        self._ephemere_timers = []
        self.title(f"Messagerie Securisee  —  {utilisateur.username}")
        self.geometry("1100x700")
        self.minsize(860, 560)
        self.configure(bg=BG)
        self._construire_ui()

    def _construire_ui(self):
        sidebar = tk.Frame(self, bg=SIDEBAR, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        badge = tk.Frame(sidebar, bg=SIDEBAR, pady=12, padx=12)
        badge.pack(fill="x")
        tk.Label(badge,
                 text=self.utilisateur.username[0].upper(),
                 font=("Segoe UI", 13, "bold"),
                 bg=ACCENT, fg="#1e1e2e",
                 width=3).pack(side="left")
        tk.Label(badge,
                 text=self.utilisateur.username,
                 font=("Segoe UI", 10, "bold"),
                 bg=SIDEBAR, fg=TEXT).pack(side="left", padx=10)

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x")

        tk.Label(sidebar, text="Conversations",
                 font=F_SMALL, bg=SIDEBAR, fg=TEXT_DIM).pack(
                     anchor="w", padx=12, pady=(10, 4))

        self.liste_convs = tk.Listbox(
            sidebar,
            bg=SIDEBAR, fg=TEXT,
            selectbackground=CARD, selectforeground=TEXT,
            font=F_BODY, relief="flat", bd=0,
            highlightthickness=0,
            activestyle="none")
        self.liste_convs.pack(fill="both", expand=True, padx=6)
        self.liste_convs.bind("<<ListboxSelect>>", self._selectionner_conv)

        tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x")
        btn_bar = tk.Frame(sidebar, bg=SIDEBAR, pady=6)
        btn_bar.pack(fill="x")
        for txt, cmd in [
            ("+ Nouveau message", self._nouvelle_conv),
            ("+ Creer un groupe", self._nouveau_groupe),
            ("  Rafraichir",      self._charger_conversations),
        ]:
            lbl = tk.Label(btn_bar, text=txt,
                           font=F_BTN, bg=SIDEBAR, fg=TEXT_DIM,
                           cursor="hand2", anchor="w",
                           padx=12, pady=6,
                           highlightthickness=0, bd=0)
            lbl.bind("<Button-1>", lambda e, c=cmd: c())
            lbl.bind("<Enter>",    lambda e, l=lbl: l.config(bg=CARD, fg=TEXT))
            lbl.bind("<Leave>",    lambda e, l=lbl: l.config(bg=SIDEBAR, fg=TEXT_DIM))
            lbl.pack(fill="x", pady=1, padx=6)

        right = tk.Frame(self, bg=BG)
        right.pack(side="right", fill="both", expand=True)

        self.header_conv = tk.Label(
            right,
            text="Selectionnez une conversation",
            font=F_TITLE, bg=CARD, fg=TEXT,
            anchor="w", padx=16, pady=12)
        self.header_conv.pack(fill="x")
        tk.Frame(right, bg=BORDER, height=1).pack(fill="x")

        self.zone_messages = scrolledtext.ScrolledText(
            right, state="disabled", wrap="word",
            bg=BG, fg=TEXT, font=F_MSG,
            relief="flat", bd=0,
            highlightthickness=0,
            padx=14, pady=10,
            insertbackground=TEXT)
        self.zone_messages.pack(fill="both", expand=True)
        self.zone_messages.tag_config(
            "expediteur", foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        self.zone_messages.tag_config(
            "horodatage", foreground=TEXT_DIM, font=("Segoe UI", 8))
        self.zone_messages.tag_config(
            "expire", foreground=EPH_CLR, font=("Segoe UI", 10, "italic"))
        self.zone_messages.tag_config(
            "eph_exp", foreground=EPH_CLR, font=("Segoe UI", 10, "bold"))
        self.zone_messages.tag_config(
            "eph_ts", foreground=EPH_CLR, font=("Segoe UI", 8))
        self.zone_messages.tag_config(
            "eph_txt", foreground=EPH_CLR, font=("Segoe UI", 10))

        tk.Frame(right, bg=BORDER, height=1).pack(fill="x")
        input_bar = tk.Frame(right, bg=CARD, padx=10, pady=8)
        input_bar.pack(fill="x")

        self.mode_ephemere = tk.BooleanVar(value=False)
        tk.Checkbutton(input_bar,
                       text="Ephemere (180s)",
                       variable=self.mode_ephemere,
                       bg=CARD, fg=EPH_CLR,
                       selectcolor=CARD,
                       activebackground=CARD,
                       font=F_SMALL,
                       cursor="hand2").pack(side="right", padx=(4, 0))

        btn_envoyer = tk.Label(
            input_bar, text="Envoyer",
            font=F_BTN, bg=ACCENT, fg="#1e1e2e",
            cursor="hand2", padx=14, pady=7,
            highlightthickness=0, bd=0)
        btn_envoyer.pack(side="right", padx=(6, 0))
        btn_envoyer.bind("<Button-1>", lambda e: self._envoyer())
        btn_envoyer.bind("<Enter>", lambda e: btn_envoyer.config(bg="#74c7ec"))
        btn_envoyer.bind("<Leave>", lambda e: btn_envoyer.config(bg=ACCENT))

        self.entry_msg = tk.Entry(
            input_bar, font=F_BODY,
            bg="#1e1e2e", fg=TEXT, insertbackground=TEXT,
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT)
        self.entry_msg.pack(side="left", fill="x", expand=True, ipady=6)
        self.entry_msg.bind("<Return>", lambda e: self._envoyer())

        self._charger_conversations()

    def _charger_conversations(self):
        self.liste_convs.delete(0, tk.END)
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT c.id, c.type, c.nom,
                   (SELECT username FROM utilisateurs u
                    JOIN participants p2
                      ON p2.conv_id = c.id AND p2.user_id = u.id
                    WHERE u.id != %s LIMIT 1) as autre
            FROM conversations c
            JOIN participants p ON p.conv_id = c.id AND p.user_id = %s
        """, (self.utilisateur.id, self.utilisateur.id))
        rows: Any = cur.fetchall()
        cur.close()
        conn.close()
        self._convs_data = []
        for row in rows:
            label = (row["nom"] if row["type"] == "groupe"
                     else (row["autre"] or "?"))
            prefix = "[G]" if row["type"] == "groupe" else "[P]"
            self.liste_convs.insert(tk.END, f"  {prefix}  {label}")
            self._convs_data.append(dict(row))

    def _selectionner_conv(self, event):
        sel = self.liste_convs.curselection()
        if not sel:
            return
        data = self._convs_data[sel[0]]
        if data["type"] == "privee":
            autre_id = self._get_autre_id(data["id"])
            if autre_id is None:
                return
            autre = Utilisateur.get_par_id(autre_id)
            if autre:
                self.conversation_active = ConvPrivee.charger_ou_creer(
                    self.utilisateur, autre)
                self.header_conv.config(text=f"[P]  {autre.username}")
        elif data["type"] == "groupe":
            from models.groupe import Groupe
            self.conversation_active = Groupe.charger(data["id"])
            self.header_conv.config(text=f"[G]  {data['nom']}")
        self._afficher_messages()

    def _get_autre_id(self, conv_id: int):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT user_id FROM participants WHERE conv_id = %s AND user_id != %s",
            (conv_id, self.utilisateur.id)
        )
        row: Any = cur.fetchone()
        cur.close()
        conn.close()
        return row["user_id"] if row else None

    def _afficher_messages(self):
        if not self.conversation_active:
            return
        for timer_id in self._ephemere_timers:
            self.after_cancel(timer_id)
        self._ephemere_timers.clear()

        rows = self.conversation_active.get_messages(self.utilisateur)
        self.zone_messages.config(state="normal")
        self.zone_messages.delete("1.0", tk.END)
        for row in rows:
            tag = f"msg_{row['id']}"
            try:
                texte = self.utilisateur._chiffreur.dechiffrer(row["contenu_chiffre"])
                exp = Utilisateur.get_par_id(row["expediteur_id"])
                nom = exp.username if exp else "?"

                if row["expire_at"]:
                    expire = row["expire_at"] if isinstance(row["expire_at"], datetime) else datetime.fromisoformat(str(row["expire_at"]))
                    restant_ms = int((expire - datetime.now()).total_seconds() * 1000)
                    if restant_ms <= 0:
                        self.zone_messages.insert(
                            tk.END, "T trop lent c'est trop tard !\n\n",
                            ("expire", tag))
                        continue
                    tid = self.after(restant_ms,
                                     lambda t=tag: self._expirer_message(t))
                    self._ephemere_timers.append(tid)
                    ts = row["horodatage"] or ""
                    self.zone_messages.insert(tk.END, f"⏱ {nom}  ", ("eph_exp", tag))
                    self.zone_messages.insert(tk.END, f"{ts}\n", ("eph_ts", tag))
                    self.zone_messages.insert(tk.END, f"{texte}\n\n", ("eph_txt", tag))
                    continue

                ts = row["horodatage"] or ""
                self.zone_messages.insert(tk.END, f"{nom}  ", ("expediteur", tag))
                self.zone_messages.insert(tk.END, f"{ts}\n", ("horodatage", tag))
                self.zone_messages.insert(tk.END, f"{texte}\n\n", tag)
            except Exception:
                self.zone_messages.insert(tk.END, "[Message illisible]\n\n", tag)
        self.zone_messages.config(state="disabled")
        self.zone_messages.see(tk.END)

    def _expirer_message(self, tag: str):
        try:
            self.zone_messages.config(state="normal")
            ranges = self.zone_messages.tag_ranges(tag)
            if ranges:
                self.zone_messages.delete(ranges[0], ranges[1])
                self.zone_messages.insert(
                    ranges[0],
                    "T trop lent c'est trop tard !\n\n",
                    ("expire", tag))
            self.zone_messages.config(state="disabled")
        except Exception:
            pass

    def _envoyer(self):
        texte = self.entry_msg.get().strip()
        if not texte or not self.conversation_active:
            return
        try:
            time_eph = 180 if self.mode_ephemere.get() else None
            self.conversation_active.envoyer_message(
                self.utilisateur, texte, time_ephemere=time_eph)
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
        if not dest:
            return
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
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id FROM utilisateurs WHERE username = %s", (username,))
        row: Any = cur.fetchone()
        cur.close()
        conn.close()
        return row["id"] if row else None
