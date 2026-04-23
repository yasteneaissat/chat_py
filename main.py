"""
Point d'entrée de l'application de messagerie sécurisée E2EE.
Lance la fenêtre de login, puis la fenêtre principale si la connexion réussit.
"""
import sys
import os

# Ajoute le dossier racine au PYTHONPATH pour les imports relatifs
sys.path.insert(0, os.path.dirname(__file__))

from db.database import initialiser_db
from gui.fenetre_login import FenetreLogin
from gui.fenetre_chat import FenetreChat


def main():
    # 1. Initialiser la base de données (crée les tables si nécessaire)
    initialiser_db()

    # 2. Fenêtre de login
    login = FenetreLogin()
    login.mainloop()

    # 3. Si l'utilisateur s'est connecté, ouvrir le chat
    if login.utilisateur_connecte:
        chat = FenetreChat(login.utilisateur_connecte)
        chat.mainloop()


if __name__ == "__main__":
    main()
