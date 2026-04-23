from __future__ import annotations
from datetime import datetime, timedelta
from db.database import get_connection


class Message:
    """Message chiffre pour un destinataire unique."""

    def __init__(self, expediteur, texte: str, conv_id: int | None,
                 time_ephemere=None):
        self.id = None
        self.expediteur = expediteur
        self.texte_clair = texte
        self.conv_id = conv_id
        self.contenu_chiffre = None
        self.dest_id = None
        self.horodatage = None
        self.time_ephemere = time_ephemere

    def chiffrer_pour(self, destinataire) -> None:
        """Chiffre le message avec la cle publique du destinataire."""
        self.contenu_chiffre = self.expediteur._chiffreur.chiffrer(
            self.texte_clair, destinataire.cle_publique
        )
        self.dest_id = destinataire.id

    def sauvegarder(self) -> None:
        """Insere le message chiffre en base de donnees."""
        expire_at = None
        if self.time_ephemere:
            expire_at = (datetime.now() + timedelta(seconds=self.time_ephemere)).isoformat()

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages "
            "(conv_id, expediteur_id, dest_id, contenu_chiffre, expire_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (self.conv_id, self.expediteur.id, self.dest_id,
             self.contenu_chiffre, expire_at),
        )
        self.id = cur.lastrowid
        conn.commit()
        conn.close()

    def dechiffrer_pour(self, utilisateur) -> str:
        """Dechiffre le message avec la cle privee de l'utilisateur."""
        return utilisateur._chiffreur.dechiffrer(self.contenu_chiffre)

    def __repr__(self):
        return f"<Message id={self.id} de {self.expediteur.username}>"
