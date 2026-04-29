import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from security.chiffrement import GestionnaireChiffrement


class TestMotDePasse(unittest.TestCase):

    def test_mdp_trop_court(self):
        valide, _ = GestionnaireChiffrement.mdp_est_robuste("Ab1")
        self.assertFalse(valide)

    def test_mdp_sans_majuscule(self):
        valide, _ = GestionnaireChiffrement.mdp_est_robuste("abcdef1!")
        self.assertFalse(valide)

    def test_mdp_sans_chiffre(self):
        valide, _ = GestionnaireChiffrement.mdp_est_robuste("Abcdefgh")
        self.assertFalse(valide)

    def test_mdp_valide(self):
        valide, msg = GestionnaireChiffrement.mdp_est_robuste("Secure1x")
        self.assertTrue(valide)
        self.assertEqual(msg, "OK")

    def test_hachage_deterministe(self):
        sel = GestionnaireChiffrement.generer_sel()
        h1 = GestionnaireChiffrement.hacher_mdp("Secure1x", sel)
        h2 = GestionnaireChiffrement.hacher_mdp("Secure1x", sel)
        self.assertEqual(h1, h2)

    def test_hachage_sel_different(self):
        h1 = GestionnaireChiffrement.hacher_mdp("Secure1x", "sel_a")
        h2 = GestionnaireChiffrement.hacher_mdp("Secure1x", "sel_b")
        self.assertNotEqual(h1, h2)

    def test_sel_unique(self):
        self.assertNotEqual(
            GestionnaireChiffrement.generer_sel(),
            GestionnaireChiffrement.generer_sel()
        )


class TestEmail(unittest.TestCase):

    def test_email_valide(self):
        self.assertTrue(GestionnaireChiffrement.email_est_valide("user@example.com"))

    def test_email_sans_arobase(self):
        self.assertFalse(GestionnaireChiffrement.email_est_valide("userexample.com"))

    def test_email_sans_domaine(self):
        self.assertFalse(GestionnaireChiffrement.email_est_valide("user@"))

    def test_email_sans_extension(self):
        self.assertFalse(GestionnaireChiffrement.email_est_valide("user@example"))


class TestChiffrementRSA(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.chiffreur = GestionnaireChiffrement("__test_rsa__")
        cls.cle_publique_pem = cls.chiffreur.generer_paire_cles()

    @classmethod
    def tearDownClass(cls):
        chemin = cls.chiffreur.chemin_cle_privee
        if os.path.exists(chemin):
            os.remove(chemin)
        dossier = os.path.dirname(chemin)
        if os.path.isdir(dossier):
            os.rmdir(dossier)

    def test_chiffrement_retourne_bytes(self):
        cipher = self.chiffreur.chiffrer("bonjour", self.cle_publique_pem)
        self.assertIsInstance(cipher, bytes)

    def test_chiffrement_different_du_clair(self):
        cipher = self.chiffreur.chiffrer("bonjour", self.cle_publique_pem)
        self.assertNotEqual(cipher, b"bonjour")

    def test_chiffrement_dechiffrement(self):
        message = "message secret"
        cipher = self.chiffreur.chiffrer(message, self.cle_publique_pem)
        clair = self.chiffreur.dechiffrer(cipher)
        self.assertEqual(clair, message)

    def test_deux_chiffrements_differents(self):
        c1 = self.chiffreur.chiffrer("test", self.cle_publique_pem)
        c2 = self.chiffreur.chiffrer("test", self.cle_publique_pem)
        self.assertNotEqual(c1, c2)


if __name__ == "__main__":
    unittest.main()
