# Messagerie Sécurisée E2EE 🔐

Application de messagerie instantanée avec chiffrement de bout en bout (E2EE), développée en Python dans le cadre d'un projet BTS SIO SLAM.

## Fonctionnalités

- **Chiffrement E2EE** : RSA-2048 + OAEP-SHA256
- **Authentification** : mots de passe hachés SHA-256 + sel aléatoire
- **Messagerie privée** : conversation chiffrée entre deux utilisateurs
- **Groupes** : chiffrement individuel pour chaque membre
- **Messages éphémères** : TTL optionnel (suppression automatique)
- **Interface graphique** : Tkinter

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Architecture

```
messagerie_securisee/
├── main.py                  # Point d'entrée
├── db/
│   └── database.py          # SQLite – création des tables
├── models/
│   ├── utilisateur.py       # Classe Utilisateur
│   ├── conversation.py      # Classe abstraite Conversation
│   ├── conv_privee.py       # Conversation privée (hérite Conversation)
│   ├── groupe.py            # Groupe (hérite Conversation)
│   ├── message.py           # Message chiffré (1 destinataire)
│   └── message_groupe.py    # Message groupe (N destinataires, hérite Message)
├── security/
│   └── chiffrement.py       # GestionnaireChiffrement (RSA + hash)
├── gui/
│   ├── fenetre_login.py     # Connexion / inscription
│   ├── fenetre_chat.py      # Interface principale
│   └── fenetre_groupe.py    # Création de groupes
└── clients/                 # Clés privées locales (NON versionné)
    └── {username}/
        └── cle_privee.pem
```

## Sécurité

| Mécanisme | Choix technique | Raison |
|---|---|---|
| Chiffrement asymétrique | RSA-2048, OAEP-SHA256 | Standard robuste, bibliothèque `cryptography` |
| Hachage MDP | SHA-256 + sel 16 octets | Résistance aux attaques par dictionnaire |
| Clé privée | Fichier PEM local (clients/) | Simule l'isolation par poste client |
| BDD | SQLite | Zéro config, migration PostgreSQL facile |

## Fonctionnalité supplémentaire : Messages éphémères

Chaque message accepte un `ttl_secondes` optionnel. Après ce délai, le contenu chiffré est supprimé de la BDD. Implémentation : champ `expire_at` dans la table `messages`.

## Tests

Créer deux utilisateurs via l'interface, envoyer un message, vérifier en base que le contenu est bien en bytes (illisible sans la clé privée).
