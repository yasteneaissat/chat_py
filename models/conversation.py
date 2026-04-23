from __future__ import annotations
from abc import ABC, abstractmethod
from db.database import get_connection


class Conversation(ABC):
    """Classe abstraite representant une conversation (privee ou groupe)."""

    def __init__(self, participants: list):
        self.id = None
        self.participants = participants  # liste d'Utilisateur

    @abstractmethod
    def envoyer_message(self, expediteur, texte: str):
        pass

    def get_messages(self, pour_user) -> list:
        """Recupere les messages destines a un utilisateur dans cette conversation."""
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM messages WHERE conv_id = ? AND dest_id = ? "
            "ORDER BY horodatage ASC",
            (self.id, pour_user.id),
        ).fetchall()
        conn.close()
        return rows

    def ajouter_participant(self, utilisateur) -> None:
        conn = get_connection()
        conn.execute(
            "INSERT OR IGNORE INTO participants (conv_id, user_id) VALUES (?, ?)",
            (self.id, utilisateur.id),
        )
        conn.commit()
        conn.close()
        if utilisateur not in self.participants:
            self.participants.append(utilisateur)

    def _creer_en_db(self, type_conv: str, nom=None) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO conversations (type, nom) VALUES (?, ?)",
            (type_conv, nom),
        )
        self.id = cur.lastrowid
        for p in self.participants:
            cur.execute(
                "INSERT INTO participants (conv_id, user_id) VALUES (?, ?)",
                (self.id, p.id),
            )
        conn.commit()
        conn.close()
