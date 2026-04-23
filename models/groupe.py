from __future__ import annotations
from models.conversation import Conversation
from models.message_groupe import MessageGroupe
from db.database import get_connection


class Groupe(Conversation):
    """Conversation de groupe avec chiffrement individuel par membre."""

    def __init__(self, nom: str, participants: list):
        super().__init__(participants)
        self.nom = nom

    @classmethod
    def creer(cls, nom: str, participants: list) -> Groupe:
        """Cree le groupe en BDD."""
        g = cls(nom, participants)
        g._creer_en_db("groupe", nom=nom)
        return g

    @classmethod
    def charger(cls, groupe_id: int):
        """Charge un groupe depuis la BDD avec ses participants."""
        from models.utilisateur import Utilisateur
        conn = get_connection()
        row = conn.execute(
            "SELECT id, nom FROM conversations WHERE id = ? AND type = 'groupe'",
            (groupe_id,)
        ).fetchone()
        if not row:
            conn.close()
            return None
        membres_rows = conn.execute(
            "SELECT user_id FROM participants WHERE conv_id = ?", (groupe_id,)
        ).fetchall()
        conn.close()

        membres = [Utilisateur.get_par_id(r["user_id"]) for r in membres_rows]
        membres = [m for m in membres if m]
        g = cls(row["nom"], membres)
        g.id = row["id"]
        return g

    def envoyer_message(self, expediteur, texte: str) -> MessageGroupe:
        """Chiffre le message pour chaque membre et le sauvegarde."""
        msg = MessageGroupe(expediteur=expediteur, texte=texte, groupe=self)
        msg.chiffrer_pour_tous()
        msg.sauvegarder()
        return msg

    def __repr__(self):
        return f"<Groupe '{self.nom}' (id={self.id}, membres={len(self.participants)})>"
