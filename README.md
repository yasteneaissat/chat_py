# Trello : 
https://trello.com/b/GIiRPrZU/projet-transversal-conception-dune-solution-applicative-securisee-en-langage-objet


# Messagerie Sécurisée E2EE

---

## Objectif

Développer une application de messagerie instantanée avec chiffrement de bout en bout (E2EE) en Python, dans le cadre d'un projet BTS SIO SLAM.

---

## Stack

| Composant | Technologie |
|---|---|
| Interface | Tkinter (thème sombre custom) |
| Base de données | MySQL (WAMP) |
| Chiffrement | RSA-2048 / OAEP-SHA256 (`cryptography`) |
| Hachage MDP | SHA-256 + sel 16 octets |

---

## Comment le lancer

1. Importer la base de données (voir section **Importer la base de données** ci-dessous)
2. Installer les dépendances et lancer :

```bash
pip install -r requirements.txt
python main.py
```

---

## Importer la base de données

Pré-requis : **WAMP** démarré, MySQL accessible sur `localhost:3306` (user `root`, pas de mot de passe).

**Via phpMyAdmin :**
1. Ouvrir `http://localhost/phpmyadmin`
2. Créer une base nommée `messagerie`
3. Aller dans l'onglet **Importer**
4. Sélectionner le fichier `.sql` fourni, puis cliquer **Exécuter**
5. Vérifier paramètre de connexion dans le fichier 'database.py'
   ```
   DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "messagerie",
    }
   ```
   Les modifiers si besoins.

> Les tables sont également créées automatiquement au premier lancement (`CREATE TABLE IF NOT EXISTS`) si la base `messagerie` existe déjà.

---

## Architecture

```
├── main.py
├── db/
│   └── database.py          # Schéma MySQL + connexion
├── models/
│   ├── conversation.py      # Classe abstraite
│   ├── conv_privee.py       # Conversation 1-to-1
│   ├── groupe.py            # Conversation de groupe
│   ├── message.py           # Message chiffré (1 destinataire)
│   ├── message_groupe.py    # Message groupe (N destinataires)
│   └── ephemere.py          # MessageEphemere (time_ephemere=180)
├── security/
│   └── chiffrement.py       # GestionnaireChiffrement
├── gui/
│   ├── fenetre_login.py
│   ├── fenetre_chat.py
│   └── fenetre_groupe.py
└── clients/                 # Clés privées locales (non versionné)
    └── {username}/
        └── cle_privee.pem
```

---

## Architecture BDD

```
utilisateurs ──< participants >── conversations
                                       │
                                    messages
                          (conv_id, expediteur_id, dest_id,
                           contenu_chiffre BLOB, expire_at)
```

Une ligne par destinataire — garantit que seul le destinataire peut déchiffrer son message.

---

## Fonctionnalités

- Inscription et connexion avec validation du mot de passe (longueur, majuscule, chiffre)
- Messagerie privée chiffrée entre deux utilisateurs (E2EE)
- Groupes : chiffrement individuel pour chaque membre
- Clés privées stockées localement dans `clients/{username}/` — jamais transmises au serveur

---

## Fonctionnalité Supplémentaire

**Messages éphémères** : chaque message peut avoir un délai d'expiration (`time_ephemere`, défaut 180 s). Une fois le délai écoulé, le contenu est remplacé côté interface par `"T trop lent c'est trop tard !"`. Les messages éphémères s'affichent en jaune avec une icône ⏱ pour les distinguer visuellement.

---

## Tests & Test Unitaires


Nous avons egalement fais des tests humain dans le sans essayer de faire remplir les formulaires de facon humaines sans savoir.


Fichier : `tests/test_chiffrement.py`  
Lancer : `py -m pytest tests/ -v`

| Test | Description | Résultat attendu |
|---|---|---|
| `test_mdp_trop_court` | MDP de moins de 8 caractères | Invalide |
| `test_mdp_sans_majuscule` | MDP sans lettre majuscule | Invalide |
| `test_mdp_sans_chiffre` | MDP sans chiffre | Invalide |
| `test_mdp_valide` | MDP conforme aux 3 règles | Valide, retourne `"OK"` |
| `test_hachage_deterministe` | Même MDP + même sel → même hash | Les deux hashs sont identiques |
| `test_hachage_sel_different` | Même MDP + sels différents → hashs différents | Les deux hashs diffèrent |
| `test_sel_unique` | Deux appels à `generer_sel()` | Les deux sels sont différents |
| `test_email_valide` | Email au format standard | Valide |
| `test_email_sans_arobase` | Email sans `@` | Invalide |
| `test_email_sans_domaine` | Email avec `@` mais sans domaine | Invalide |
| `test_email_sans_extension` | Email sans extension (`.com`, etc.) | Invalide |
| `test_chiffrement_retourne_bytes` | Chiffrement d'un message | Retourne un objet `bytes` |
| `test_chiffrement_different_du_clair` | Le chiffré ≠ le message clair | Les deux valeurs diffèrent |
| `test_chiffrement_dechiffrement` | Chiffrement puis déchiffrement | Texte récupéré identique à l'original |
| `test_deux_chiffrements_differents` | Chiffrer deux fois le même message | Les deux chiffrés sont différents (OAEP probabiliste) |
