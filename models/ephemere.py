from __future__ import annotations
from models.message import Message

DUREE_DEFAUT = 180 


class MessageEphemere(Message):
    """Message éphémère : expire après time_ephemere secondes (défaut : 180)."""

    def __init__(self, expediteur, texte: str, conv_id: int,
                 time_ephemere: int = DUREE_DEFAUT):
        super().__init__(expediteur, texte, conv_id,
                         time_ephemere=time_ephemere)
