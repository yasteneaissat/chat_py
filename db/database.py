import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "messagerie",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def initialiser_db():
    """Crée toutes les tables si elles n'existent pas."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id           INT AUTO_INCREMENT PRIMARY KEY,
            username     VARCHAR(100) UNIQUE NOT NULL,
            email        VARCHAR(255) UNIQUE NOT NULL,
            mdp_hash     VARCHAR(64)  NOT NULL,
            sel          VARCHAR(32)  NOT NULL,
            cle_publique TEXT         NOT NULL,
            cree_le      DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id      INT AUTO_INCREMENT PRIMARY KEY,
            type    VARCHAR(10) NOT NULL,
            nom     VARCHAR(255),
            cree_le DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            conv_id INT NOT NULL,
            user_id INT NOT NULL,
            PRIMARY KEY (conv_id, user_id),
            FOREIGN KEY (conv_id) REFERENCES conversations(id),
            FOREIGN KEY (user_id) REFERENCES utilisateurs(id)
        ) ENGINE=InnoDB
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            conv_id         INT,
            expediteur_id   INT,
            dest_id         INT,
            contenu_chiffre BLOB,
            expire_at       DATETIME,
            horodatage      DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conv_id)       REFERENCES conversations(id),
            FOREIGN KEY (expediteur_id) REFERENCES utilisateurs(id),
            FOREIGN KEY (dest_id)       REFERENCES utilisateurs(id)
        ) ENGINE=InnoDB
    """)

    conn.commit()
    cur.close()
    conn.close()
