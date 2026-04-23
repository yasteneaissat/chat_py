from __future__ import annotations
from db.database import get_connection
from security.chiffrement import GestionnaireChiffrement


class Utilisateur:
    def __init__(self, username: str, email: str):
        self.id = None
        self.username = username
        self.email = email
        self.cle_publique = None
        self._chiffreur = GestionnaireChiffrement(chemin_client=username)

    # ── Inscription ──────────────────────────────────────────────────────────

    def s_inscrire(self, mot_de_passe: str) -> None:
        """
        Verifie la robustesse du MDP, genere les cles RSA, hache le MDP
        et insere l'utilisateur en base.
        """
        valide, msg = GestionnaireChiffrement.mdp_est_robuste(mot_de_passe)
        if not valide:
            raise ValueError(msg)

        sel = GestionnaireChiffrement.generer_sel()
        mdp_hash = GestionnaireChiffrement.hacher_mdp(mot_de_passe, sel)
        self.cle_publique = self._chiffreur.generer_paire_cles()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO utilisateurs (username, email, mdp_hash, sel, cle_publique) "
            "VALUES (?, ?, ?, ?, ?)",
            (self.username, self.email, mdp_hash, sel, self.cle_publique),
        )
        self.id = cur.lastrowid
        conn.commit()
        conn.close()

    # ── Connexion ────────────────────────────────────────────────────────────

    @staticmethod
    def se_connecter(username: str, mot_de_passe: str):
        """
        Verifie les identifiants. Retourne l'Utilisateur connecte ou None.
        Charge la cle privee depuis le disque local en cas de succes.
        """
        conn = get_connection()
        row = conn.execute(
            "SELECT id, email, mdp_hash, sel, cle_publique "
            "FROM utilisateurs WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()

        if not row:
            return None

        hash_attendu = GestionnaireChiffrement.hacher_mdp(mot_de_passe, row["sel"])
        if hash_attendu != row["mdp_hash"]:
            return None

        u = Utilisateur(username, row["email"])
        u.id = row["id"]
        u.cle_publique = row["cle_publique"]
        u._chiffreur.charger_cle_privee()
        return u

    # ── Utilitaires ──────────────────────────────────────────────────────────

    @staticmethod
    def get_par_id(user_id: int):
        conn = get_connection()
        row = conn.execute(
            "SELECT id, username, email, cle_publique FROM utilisateurs WHERE id = ?",
            (user_id,),
        ).fetchone()
        conn.close()
        if not row:
            return None
        u = Utilisateur(row["username"], row["email"])
        u.id = row["id"]
        u.cle_publique = row["cle_publique"]
        return u

    def __repr__(self):
        return f"<Utilisateur {self.username} (id={self.id})>"
