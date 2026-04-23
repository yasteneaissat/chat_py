from __future__ import annotations
from models.message import Message
from db.database import get_connection


class MessageGroupe(Message):
    """
    Message de groupe : une version chiffree par destinataire.
    Herite de Message et etend sauvegarder() pour gerer le multi-chiffrement.
    """

    def __init__(self, expediteur, texte: str, groupe, ttl_secondes=None):
        super().__init__(expediteur, texte, conv_id=groupe.id,
                         ttl_secondes=ttl_secondes)
        self.groupe = groupe
        self.versions_chiffrees = {}  # {user_id: bytes}

    def chiffrer_pour_tous(self) -> None:
        """
        Produit une version chiffree pour chaque membre du groupe
        (sauf l'expediteur lui-meme).
        """
        for membre in self.groupe.participants:
            if membre.id == self.expediteur.id:
                continue
            cipher = self.expediteur._chiffreur.chiffrer(
                self.texte_clair, membre.cle_publique
            )
            self.versions_chiffrees[membre.id] = cipher

    def sauvegarder(self) -> None:
        """Insere une ligne par destinataire dans la table messages."""
        from datetime import datetime, timedelta
        expire_at = None
        if self.ttl_secondes:
            expire_at = (datetime.now() + timedelta(seconds=self.ttl_secondes)).isoformat()

        conn = get_connection()
        cur = conn.cursor()
        for dest_id, cipher in self.versions_chiffrees.items():
            cur.execute(
                "INSERT INTO messages "
                "(conv_id, expediteur_id, dest_id, contenu_chiffre, expire_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (self.groupe.id, self.expediteur.id, dest_id, cipher, expire_at),
            )
        conn.commit()
        conn.close()

    def dechiffrer_pour(self, utilisateur) -> str:
        """Dechiffre la version destinee a cet utilisateur."""
        cipher = self.versions_chiffrees.get(utilisateur.id)
        if not cipher:
            raise PermissionError("Ce message ne vous est pas destine.")
        return utilisateur._chiffreur.dechiffrer(cipher)
