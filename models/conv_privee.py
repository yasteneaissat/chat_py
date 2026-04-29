from __future__ import annotations
from typing import Any
from models.conversation import Conversation
from models.message import Message
from db.database import get_connection


class ConvPrivee(Conversation):
    """Conversation a deux participants avec chiffrement E2EE."""

    def __init__(self, expediteur, destinataire):
        super().__init__([expediteur, destinataire])
        self.expediteur = expediteur
        self.destinataire = destinataire

    @classmethod
    def creer(cls, expediteur, destinataire) -> ConvPrivee:
        """Cree la conversation en BDD et retourne l'objet."""
        conv = cls(expediteur, destinataire)
        conv._creer_en_db("privee")
        return conv

    @classmethod
    def charger_ou_creer(cls, expediteur, destinataire) -> ConvPrivee:
        """Retourne la conversation existante entre les deux, ou en cree une."""
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT c.id FROM conversations c
            JOIN participants p1 ON p1.conv_id = c.id AND p1.user_id = %s
            JOIN participants p2 ON p2.conv_id = c.id AND p2.user_id = %s
            WHERE c.type = 'privee'
            LIMIT 1
        """, (expediteur.id, destinataire.id))
        row: Any = cur.fetchone()
        cur.close()
        conn.close()

        conv = cls(expediteur, destinataire)
        if row:
            conv.id = row["id"]
        else:
            conv._creer_en_db("privee")
        return conv

    def envoyer_message(self, expediteur, texte: str, time_ephemere=None) -> Message:
        """Chiffre et envoie le message au destinataire."""
        dest = (self.destinataire
                if expediteur.id == self.expediteur.id
                else self.expediteur)
        msg = Message(expediteur=expediteur, texte=texte, conv_id = self.id,
                      time_ephemere=time_ephemere)
        msg.chiffrer_pour(dest)
        msg.sauvegarder()
        return msg
