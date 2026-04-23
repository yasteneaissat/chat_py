"""
GestionnaireChiffrement
-----------------------
Gere la generation de paires de cles RSA-2048, le chiffrement OAEP-SHA256,
le dechiffrement et le hachage SHA-256 des mots de passe.
"""
import hashlib
import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


CLIENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "clients")


class GestionnaireChiffrement:
    def __init__(self, chemin_client: str):
        self.chemin_cle_privee = os.path.join(CLIENTS_DIR, chemin_client, "cle_privee.pem")
        self.cle_privee = None
        self.cle_publique = None

    # ── Generation ──────────────────────────────────────────────────────────

    def generer_paire_cles(self) -> str:
        """Genere une paire RSA-2048. Sauvegarde la cle privee localement.
        Retourne la cle publique en PEM (a stocker en BDD)."""
        self.cle_privee = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.cle_publique = self.cle_privee.public_key()
        self._sauver_cle_privee()
        return self._exporter_cle_publique()

    def _sauver_cle_privee(self):
        """Sauvegarde la cle privee sur le poste client simule (dossier clients/)."""
        os.makedirs(os.path.dirname(self.chemin_cle_privee), exist_ok=True)
        pem = self.cle_privee.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            # En production : utiliser BestAvailableEncryption(passphrase)
            encryption_algorithm=serialization.NoEncryption(),
        )
        with open(self.chemin_cle_privee, "wb") as f:
            f.write(pem)

    def charger_cle_privee(self):
        """Charge la cle privee depuis le disque au moment de la connexion."""
        with open(self.chemin_cle_privee, "rb") as f:
            self.cle_privee = serialization.load_pem_private_key(f.read(), password=None)
        self.cle_publique = self.cle_privee.public_key()

    def _exporter_cle_publique(self) -> str:
        return self.cle_publique.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()

    # ── Chiffrement / Dechiffrement ──────────────────────────────────────────

    def chiffrer(self, message: str, cle_publique_pem: str) -> bytes:
        """Chiffre un message en clair avec la cle publique RSA d'un destinataire."""
        cle_pub = serialization.load_pem_public_key(cle_publique_pem.encode())
        return cle_pub.encrypt(
            message.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def dechiffrer(self, message_chiffre: bytes) -> str:
        """Dechiffre un message avec la cle privee locale."""
        if not self.cle_privee:
            self.charger_cle_privee()
        return self.cle_privee.decrypt(
            message_chiffre,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        ).decode("utf-8")

    # ── Authentification ─────────────────────────────────────────────────────

    @staticmethod
    def generer_sel() -> str:
        """Genere un sel aleatoire de 16 octets sous forme hexadecimale."""
        return os.urandom(16).hex()

    @staticmethod
    def hacher_mdp(mot_de_passe: str, sel: str) -> str:
        """Hache le mot de passe avec sel (SHA-256). Retourne le hash hex."""
        return hashlib.sha256((mot_de_passe + sel).encode("utf-8")).hexdigest()

    @staticmethod
    def mdp_est_robuste(mot_de_passe: str):
        """Verifie la robustesse du mot de passe. Retourne (valide, message)."""
        if len(mot_de_passe) < 8:
            return False, "Le mot de passe doit contenir au moins 8 caracteres."
        if not any(c.isupper() for c in mot_de_passe):
            return False, "Le mot de passe doit contenir au moins une majuscule."
        if not any(c.isdigit() for c in mot_de_passe):
            return False, "Le mot de passe doit contenir au moins un chiffre."
        return True, "OK"
