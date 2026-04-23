import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "messagerie.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialiser_db():
    """Crée toutes les tables si elles n'existent pas."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT    UNIQUE NOT NULL,
            email        TEXT    UNIQUE NOT NULL,
            mdp_hash     TEXT    NOT NULL,
            sel          TEXT    NOT NULL,
            cle_publique TEXT    NOT NULL,
            cree_le      DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS conversations (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            type    TEXT    NOT NULL CHECK(type IN ('privee','groupe')),
            nom     TEXT,
            cree_le DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS participants (
            conv_id INTEGER REFERENCES conversations(id),
            user_id INTEGER REFERENCES utilisateurs(id),
            PRIMARY KEY (conv_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            conv_id         INTEGER REFERENCES conversations(id),
            expediteur_id   INTEGER REFERENCES utilisateurs(id),
            dest_id         INTEGER REFERENCES utilisateurs(id),
            contenu_chiffre BLOB,
            expire_at       DATETIME,
            horodatage      DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
