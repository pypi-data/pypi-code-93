"""Ce module teste avec unittest la classe Tableau."""

import unittest
import os
import sys

#On change le dossier de travail (cwd) pour pouvoir appeler les fichiers via des chemins relatifs
os.chdir(os.path.dirname(__file__))#On change le dossier de travail en appellant le nom du dossier qui contient ce fichier (le dossier tests)
os.chdir("..")#On rechange le dossier de travail en prenant le dossier parent du dossier tests (le dossier conteneurs)
sys.path.append(os.getcwd())#ligne nécessaire à l'importation du module controle_arguments

from conteneurs.tableau import *

class TestsTableau(unittest.TestCase) :
    """Cette classe teste la classe DictionnaireOrdonné grâce à Unittest."""
    
    def assertEqualTableau(self, tableau, _tableau=[[None,None],[None,None]], en_tetes_h=False, en_tetes_v=False) :
        """Cette méthode vérifie si deux objets Tableau sont égaux.

        Cette methode compare chaque attribut à la valeur fournie.
        """
        if tableau._tableau == _tableau and tableau.en_tetes_h == en_tetes_h and tableau.en_tetes_v == en_tetes_v :
            return self.assertEqual(0,0)#l'objet verificateur est égal à la valeur théorique
        else :
            raise AssertionError(repr(tableau) + " != " + repr(Tableau(tableau=_tableau, en_tetes_h = en_tetes_h, en_tetes_v = en_tetes_v)))

    def setUp(self) :
        """Crée des variable utile pour plusieurs tests.
        
        Crée quatre tableau pour ensuite les tester.
        """
        self.T1 = Tableau()#on crée un tableau vide

        self._tableau_T2 = [[287, "Nom erreur", "Type d'erreur", "Jour", "Mois", "Année", "Heure"],[54, "Le tableau n'est pas une liste", "TypeError", 17,1,2021,15], [381, "Le tableau est trop petit", "ValueError", 19,1,2021,10], [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", "NotImplementedError", 20,1,2021,8], [382, "Le tableau a trop de colonnes", "ValueError", 22,1,2021,19], [383, "Le tableau a trop de lignes", "ValueError", 22,1,2021,20], [380, "Le tableau n'a pas assez de colonnes", "ValueError", 23,1,2021,7]]
        self.T2 = Tableau(tableau=self._tableau_T2, en_tetes_h=True, en_tetes_v=True)#création Tableau à l'aide d'une structure tableau
        
        self._tableau_T3 = [[None]*4]*10#une ligne de plus pour les en-têtes h et une colonne de plus pour les en-têtes v
        self.T3 = Tableau(dimensions=(3, 9), en_tetes_v=True)#cration d'un tableau vide avec des dimensions

        self._tableau_T4 = [[None, "Année", "Mois", "Jour", "Nb visites", "Nb pages visitées"], [None, 2020, 12, 30, 5, 14], [None, 2020, 12, 31, 5, 18], [None, 2021, 1, 1, 6, 10], [None, 2021, 1, 2, 11, 106]]
        self.T4 = Tableau(fichier_csv="./tests/T4.csv", en_tetes_h=True)#création depuis fichier csv

        self._tableau_T5 = [[None, "Année", "Mois", "Jour", "Nb visites", "Nb visites deuxième site"], [None, 2021, 1, 3, 9, 3], [None, 2021, 1, 4, 8, 5]]
        self.T5 = Tableau(tableau=self._tableau_T5, en_tetes_h=True)

    def tearDown(self) :
        del self.T1
        del self.T2
        del self.T3
        del self.T4
        del self.T5

    def test_init(self) :
        """Cette méthode teste la créaction de tableaux."""
        self.assertEqualTableau(self.T1)
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        self.assertEqualTableau(self.T3, _tableau=self._tableau_T3, en_tetes_h=False, en_tetes_v=True)
        self.assertEqualTableau(self.T4, _tableau=self._tableau_T4, en_tetes_h=True)
        self.assertEqualTableau(self.T5, _tableau=self._tableau_T5, en_tetes_h=True)
    
    def test_repr(self) :
        """Méthode testant la méthode __repr__ de la classe testée."""
        repr_theorique = "conteneurs.Tableau(tableau="
        repr_theorique += repr(self._tableau_T2)
        repr_theorique += ", en_tetes_h=True, en_tetes_v=True)"
        
        self.assertEqual(repr(self.T2), repr_theorique)
    
    def test_str(self) :
        """Méthode testant la méthode __str__ de la classe testée."""
        str_theorique = """      287      |   Nom erreur  | Type d'erreur |      Jour     |      Mois     |     Année     |     Heure     |\n       54      | Le tableau n'»|   TypeError   |       17      |       1       |      2021     |       15      |\n      381      | Le tableau es»|   ValueError  |       19      |       1       |      2021     |       10      |\n      215      | Cette méthode»| NotImplemente»|       20      |       1       |      2021     |       8       |\n      382      | Le tableau a »|   ValueError  |       22      |       1       |      2021     |       19      |\n      383      | Le tableau a »|   ValueError  |       22      |       1       |      2021     |       20      |\n      380      | Le tableau n'»|   ValueError  |       23      |       1       |      2021     |       7       |\n"""
        self.assertEqual(str(self.T2), str_theorique)

    def test_eq(self) :
        """Méthode testant la méthode spéciale __eq__ de la classe testée."""
        T4_bis = Tableau(tableau=self._tableau_T4, en_tetes_h=True)
        bool1 = False
        if self.T4 == T4_bis :
            bool1 = True
        self.assertTrue(bool1)
        T2_bis = Tableau(tableau=self._tableau_T2)
        bool2 = False
        if self.T2 == T2_bis :
            bool2 = True
        self.assertFalse(bool2)#car il n' y pas les mêmes attributs pour les en-tetes 
        T2_ter = Tableau(tableau=self._tableau_T4, en_tetes_h=True, en_tetes_v=True)
        bool3 = self.T2.__eq__(T2_ter)
        self.assertFalse(bool3)#car il n' y pas le même attribut pour le tableau
        bool4 = False
        if self.T2 == self._tableau_T2 :
            bool4 = True
        self.assertTrue(bool4)

    def test_ne(self) :
        """Méthode testant la méthode spéciale __ne__ de la classe testée."""
        T4_bis = Tableau(tableau=self._tableau_T4, en_tetes_h=True)
        bool1 = False
        if self.T4 != T4_bis :
            bool1 = True
        self.assertFalse(bool1)
        T2_bis = Tableau(tableau=self._tableau_T2)
        bool2 = False
        if self.T2 != T2_bis :
            bool2 = True
        self.assertTrue(bool2)#car il n' y pas les mêmes attributs pour les en-tetes 
        T2_ter = Tableau(tableau=self._tableau_T4, en_tetes_h=True, en_tetes_v=True)
        bool3 = self.T2.__ne__(T2_ter)
        self.assertTrue(bool3)#car il n' y pas le même attribut pour le tableau
        bool4 = False
        if self.T2 != self._tableau_T2 :
            bool4 = True
        self.assertFalse(bool4)

    def test_getitem(self) :
        """Cette méthode teste la méthode spéciale __getitem__.
        
        Teste l'affichage de lignes, colonnes et cases en exécutant l'instruction tableau[index].
        """
        #lignes
        ligne_theorique1 = [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", "NotImplementedError", 20,1,2021,8]
        self.assertEqual(self.T2[3], ligne_theorique1)
        ligne_theorique2 = ["Année", "Mois", "Jour", "Nb visites", "Nb pages visitées"]
        self.assertEqual(self.T4[0], ligne_theorique2)
        #colonnes
        colonne_theorique1 = ["Jour", 17, 19, 20, 22, 22, 23]
        self.assertEqual(self.T2["C"], colonne_theorique1)
        colonne_theorique2 = [54, 381, 215, 382, 383, 380]
        self.assertEqual(self.T2["@"], colonne_theorique2)
        #cases
        case_theorique = "NotImplementedError"
        self.assertEqual(self.T2["B3"], case_theorique)
        self.assertEqual(self.T2["@2"], 381)#en-tête vertical
        self.assertEqual(self.T4["D0"], "Nb visites")#en-tête horizontal
        self.assertEqual(self.T2["@0"], 287)#nom du tableau

    def test_setitem_lignes(self) :
        """Cette méthode teste la méthode spéciale __setitem__.
        
        Teste la modification de lignes en exécutant l'instruction tableau[index_ligne]=valeur.
        """
        nouvelle_valeur_ligne = [381, "Le tableau est trop petit", "ValueError", 18,2,2021,10]
        self.T2[2] = nouvelle_valeur_ligne
        self._tableau_T2[2] = nouvelle_valeur_ligne
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        self._tableau_T4[0] = [None, "Year", "Month", "Day", "View's number", "Viewing slide's number"]
        self.T4[0] = ["Year", "Month", "Day", "View's number", "Viewing slide's number"]
        self.assertEqualTableau(self.T4, self._tableau_T4, True)

    def test_setitem_colonnes(self) :
        """Cette méthode teste la méthode spéciale __setitem__.
        
        Teste la modification de colonnes en exécutant l'instruction tableau[index_colonne]=valeur.
        """
        self.T4["D"] = ["Nombre visites", 6, 5, 9, 14]
        _tableau_T4 = [[None, "Année", "Mois", "Jour", "Nombre visites", "Nb pages visitées"], [None, 2020, 12, 30, 6, 14], [None, 2020, 12, 31, 5, 18], [None, 2021, 1, 1, 9, 10], [None, 2021, 1, 2, 14, 106]]
        self.assertEqualTableau(self.T4, _tableau_T4, True)
        self._tableau_T2[1][0] = 52
        self._tableau_T2[2][0] = 481
        self._tableau_T2[3][0] = 315
        self._tableau_T2[4][0] = 482
        self._tableau_T2[5][0] = 483
        self._tableau_T2[6][0] = 480
        self.T2["@"] = [52, 481, 315, 482, 483, 480]
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)

    def test_setitem_cases(self) :
        """Cette méthode teste la méthode spéciale __setitem__.
        
        Teste la modification de cases en exécutant l'instruction tableau[index_case]=valeur.
        """
        self.T2["C5"] = "IndexError"
        self._tableau_T2[5][3] = "IndexError"
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        self.T4.__setitem__("B3", 2)
        self._tableau_T4[3][2] = 2
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.T2["@2"] = 1025#modification en-tête vertical
        self._tableau_T2[2][0] = 1025
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        self.T4["D0"] = "Nombre de visites"#modification en-tête horizontal
        self._tableau_T4[0][4] = "Nombre de visites"
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.T4["@0"] = "Tableau n°1"
        self._tableau_T4[0][0] = "Tableau n°1"
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        
    
    def test_delitem_lignes(self) :
        """Cette méthode teste la méthode spéciale __delitem__.
        
        Teste la suppression de lignes grâce à l'instruction : del tableau[index_ligne].
        """
        del self.T2[1]
        _tableau_T2 = [[287, "Nom erreur", "Type d'erreur", "Jour", "Mois", "Année", "Heure"], [381, "Le tableau est trop petit", "ValueError", 19,1,2021,10], [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", "NotImplementedError", 20,1,2021,8], [382, "Le tableau a trop de colonnes", "ValueError", 22,1,2021,19], [383, "Le tableau a trop de lignes", "ValueError", 22,1,2021,20], [380, "Le tableau n'a pas assez de colonnes", "ValueError", 23,1,2021,7]]
        self.assertEqualTableau(self.T2, _tableau_T2, True, True)
        del self.T4[0]
        self.assertEqualTableau(self.T4, self._tableau_T4)

    def test_delitem_colonnes(self) :
        """Cette méthode teste la méthode spéciale __delitem__.
        
        Teste la suppression de colonnes grâce à l'instruction : del tableau[index_colonne].
        """
        del self.T2["B"]
        _tableau_T2 = [[287, "Nom erreur", "Jour", "Mois", "Année", "Heure"],[54, "Le tableau n'est pas une liste", 17,1,2021,15], [381, "Le tableau est trop petit", 19,1,2021,10], [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", 20,1,2021,8], [382, "Le tableau a trop de colonnes", 22,1,2021,19], [383, "Le tableau a trop de lignes", 22,1,2021,20], [380, "Le tableau n'a pas assez de colonnes", 23,1,2021,7]]
        self.assertEqualTableau(self.T2, _tableau_T2, True, True)
        del self.T2["@"]
        self.assertEqualTableau(self.T2, _tableau_T2, True)

    def test_delitem_cases(self) :
        """Cette méthode teste la méthode spéciale __delitem__.
        
        Teste la suppression de cases grâce à l'instruction : del tableau[index_case].
        """
        del self.T2["B5"]
        self._tableau_T2[5][2] = None
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        self.T4.__delitem__("E2")
        self._tableau_T4[2][5] = None
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        del self.T2["@2"]#supression en-tête vertical
        self._tableau_T2[2][0] = None
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        del self.T4["C0"]#suppression en-tête horizontal
        self._tableau_T4[0][3] = None
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        del self.T2["@0"]
        self._tableau_T2[0][0] = None
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)

    def test_contains(self) :
        """Teste la méthode spéciale __contains__ de la classe testée."""
        bool1 = False
        if "ValueError" in self.T2 :
            bool1 = True
        self.assertEqual(bool1, True)
        bool2 = False
        if 1026 in self.T2 :
            bool2 = True
        self.assertEqual(bool2, False)
        bool3 = self.T4.__contains__("Mois")#on recherche aussi dans les en-têtes
        self.assertEqual(bool3, True)

    def test_len(self) :
        """Cette méthode teste la méthode spéciale __len__ de la classe testée.
        
        Vérifie que les dimmensions du tableau qui sont renvoyés par la fonction len sont correctes.
        """
        len_theorique1 = 36
        self.assertEqual(len(self.T2), len_theorique1)

    def test_iter(self) :
        """Teste la méthode spéciale __iter__ de la classe testée."""
        liste_valeurs = []
        for valeur in self.T4 :
            liste_valeurs.append(valeur)
        liste_valeurs_theorique = ["Année", "Mois", "Jour", "Nb visites", "Nb pages visitées", 2020, 12, 30, 5, 14, 2020, 12, 31, 5, 18, 2021, 1, 1, 6, 10, 2021, 1, 2, 11, 106]
        self.assertEqual(liste_valeurs, liste_valeurs_theorique)

    def test__add(self) :
        """Teste la méthode spéciale __add__ de la classe testée."""
        #test d'addition avec deux tableaux
        _tableau_addition = [[None, "Année", "Mois", "Jour", "Nb visites", "Nb pages visitées", "Nb visites deuxième site"], [None, 2020,12, 30, 5, 14, None], [None, 2020, 12, 31, 5, 18, None], [None, 2021, 1, 1, 6, 10, None], [None, 2021, 1, 2, 11, 106, None], [None, 2021, 1, 3, 9, None, 3], [None, 2021, 1, 4, 8, None, 5]]
        resultat1 = self.T4 + self.T5
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.assertEqualTableau(resultat1, _tableau_addition, True)
        
        #test avec une structure tableau
        resultat2 = self.T4 + self._tableau_T5
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.assertEqualTableau(resultat2, _tableau_addition, True)
    
    def test_radd(self) :
        """teste la méthode spéciale __radd__ de la classe testée.
        
        __radd__ est appelée quand obj1 + obj2 est impossible pour faire obj2+obj1.
        """
        #test d'addition avec deux tableaux
        _tableau_addition = [[None, "Année", "Mois", "Jour", "Nb visites", "Nb visites deuxième site", "Nb pages visitées"], [None, 2021, 1, 3, 9, 3, None], [None, 2021, 1, 4, 8, 5, None], [None, 2020,12, 30, 5, None, 14], [None, 2020, 12, 31, 5, None, 18], [None, 2021, 1, 1, 6, None, 10], [None, 2021, 1, 2, 11, None, 106]]
        resultat1 = self.T4.__radd__(self.T5)
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.assertEqualTableau(resultat1, _tableau_addition, True)
        
        #test avec une structure tableau
        resultat2 =  self._tableau_T5 + self.T4
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.assertEqualTableau(resultat2, _tableau_addition, True, True)

    def test_iadd(self) :
        """Teste la méthode spéciale __iadd__ de la classe testée.
        
        Ajoute à self un autre tableau. On vérifie que ce tableau a bien changé après l'addition.
        """
        #test d'addition avec deux tableaux
        _tableau_addition = [[None, "Année", "Mois", "Jour", "Nb visites", "Nb pages visitées", "Nb visites deuxième site"], [None, 2020,12, 30, 5, 14, None], [None, 2020, 12, 31, 5, 18, None], [None, 2021, 1, 1, 6, 10, None], [None, 2021, 1, 2, 11, 106, None], [None, 2021, 1, 3, 9, None, 3], [None, 2021, 1, 4, 8, None, 5]]
        self.T4 += self.T5
        self.assertEqualTableau(self.T4, _tableau_addition, True)

        #test avec une structure tableau
        self.T4._tableau = self._tableau_T4
        self.T4 += self._tableau_T5
        self.assertEqualTableau(self.T4, _tableau_addition, True)

    def test_get_tableau(self) :
        """Teste la méthode get_tableau de la classe testée."""
        self.assertEqual(self.T2.get_tableau(), self._tableau_T2)
        tableau_T4 = [["Année", "Mois", "Jour", "Nb visites", "Nb pages visitées"], [2020, 12, 30, 5, 14], [2020, 12, 31, 5, 18], [2021, 1, 1, 6, 10], [2021, 1, 2, 11, 106]]
        self.assertEqual(self.T4.tableau, tableau_T4)
        self.assertEqualTableau(self.T4, self._tableau_T4, True)

    def test_get_en_tetes_h(self) :
        """Teste la méthode get_en_tetes_h."""
        self.assertEqual(self.T2.get_en_tetes_h(), True)
        self.assertEqual(self.T3.en_tetes_h, False)

    def test_set_en_tetes_h(self) :
        """Teste la méthode set_en_tetes_h de la classe testée."""
        self.T2.set_en_tetes_h(False)
        self.assertEqualTableau(self.T2, self._tableau_T2, False, True)
        self.T3.en_tetes_h = True
        self.assertEqualTableau(self.T3, self._tableau_T3, True, True)

    def test_get_en_tetes_v(self) :
        """Teste la méthode get_en_tetes_v."""
        self.assertEqual(self.T2.get_en_tetes_v(), True)
        self.assertEqual(self.T4.en_tetes_v, False)

    def test_set_en_tetes_v(self) :
        """Teste la méthode set_en_tetes_h de la classe testée."""
        self.T2.set_en_tetes_v(False)
        self.assertEqualTableau(self.T2, self._tableau_T2, True)
        self.T4.en_tetes_v = True
        self.assertEqualTableau(self.T4, self._tableau_T4, True, True)

    def test_get_nom_tableau(self) :
        """Teste la méthode get_nom_tableau de la classe testée."""
        self.assertEqual(self.T2.nom_tableau, 287)
        self.assertEqual(self.T2.get_nom_tableau(), 287)

    def test_set_nom_tableau(self) :
        """Teste la méthode set_nom_tableau de la classe testée."""
        self.T2.set_nom_tableau(288)
        self._tableau_T2[0][0] = 288
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        self.T4.nom_tableau = "Tableau de statistiques"
        self._tableau_T4[0][0] = "Tableau de statistiques"
        self.assertEqualTableau(self.T4, self._tableau_T4, True)

    def test_del_nom_tableau(self) :
        """Teste la méthode del_nom_tableau de la classe testée."""
        del self.T2.nom_tableau
        del self._tableau_T2[0][0]
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)

    def test_get_dimensions(self) :
        """Teste la méthode get_dimensions de la classe testée."""
        dimensions_theoriques1 = (6,6)
        self.assertEqual(self.T2.get_dimensions(), dimensions_theoriques1)
        dimensions_theoriques2 = (5, 4)
        self.assertEqual(self.T4.dimensions, dimensions_theoriques2)

    def test_set_dimensions(self) :
        """Méthode testant la méthode set_dimensions de la classe testée."""
        self.T4.set_dimensions((5,3))#supprime une ligne
        del self._tableau_T4[4]
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.T2.dimensions = (10, 20)
        self.assertEqualTableau(self.T1)
    
    def test_del_dimensions(self) :
        with self.assertRaises(NotImplementedError) :
            self.T3.del_dimensions()

    def test_get_ligne(self) :
        """Teste la méthode get_ligne de la classe testée."""
        ligne_theorique1 = [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", "NotImplementedError", 20,1,2021,8]
        self.assertEqual(self.T2.get_ligne(3), ligne_theorique1)
        ligne_theorique2 = ["Année", "Mois", "Jour", "Nb visites", "Nb pages visitées"]
        self.assertEqual(self.T4.get_ligne(0), ligne_theorique2)

    def test_set_ligne(self) :
        nouvelle_valeur_ligne = [381, "Le tableau est trop petit", "ValueError", 18,2,2021,10]
        self.T2.set_ligne(2, nouvelle_valeur_ligne)
        self._tableau_T2[2] = nouvelle_valeur_ligne
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        self._tableau_T4[0] = [None, "Year", "Month", "Day", "View's number", "Viewing slide's number"]
        self.T4.set_ligne(0, ["Year", "Month", "Day", "View's number", "Viewing slide's number"])
        self.assertEqualTableau(self.T4, self._tableau_T4, True)

    def test_del_ligne(self) :
        self.T2.del_ligne(1)
        _tableau_T2 = [[287, "Nom erreur", "Type d'erreur", "Jour", "Mois", "Année", "Heure"], [381, "Le tableau est trop petit", "ValueError", 19,1,2021,10], [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", "NotImplementedError", 20,1,2021,8], [382, "Le tableau a trop de colonnes", "ValueError", 22,1,2021,19], [383, "Le tableau a trop de lignes", "ValueError", 22,1,2021,20], [380, "Le tableau n'a pas assez de colonnes", "ValueError", 23,1,2021,7]]
        self.assertEqualTableau(self.T2, _tableau_T2, True, True)
        self.T4.del_ligne(0)
        self.assertEqualTableau(self.T4, self._tableau_T4)

    def test_append_ligne(self) :
        self.T2.append_ligne()
        _tableau_T2 = [[287, "Nom erreur", "Type d'erreur", "Jour", "Mois", "Année", "Heure"],[54, "Le tableau n'est pas une liste", "TypeError", 17,1,2021,15], [381, "Le tableau est trop petit", "ValueError", 19,1,2021,10], [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", "NotImplementedError", 20,1,2021,8], [382, "Le tableau a trop de colonnes", "ValueError", 22,1,2021,19], [383, "Le tableau a trop de lignes", "ValueError", 22,1,2021,20], [380, "Le tableau n'a pas assez de colonnes", "ValueError", 23,1,2021,7], [None, None, None, None, None, None, None]]
        self.assertEqualTableau(self.T2, _tableau_T2, True, True)
        self.T4.append_ligne(2)
        _tableau_T4 = [[None, "Année", "Mois", "Jour", "Nb visites", "Nb pages visitées"], [None, 2020, 12, 30, 5, 14], [None, 2020, 12, 31, 5, 18],[None, 2021, 1, 1, 6, 10], [None, 2021, 1, 2, 11, 106], [None, None, None, None, None, None], [None, None, None, None, None, None]]
        self.assertEqualTableau(self.T4, _tableau_T4, True)
        self.assertEqualTableau(self.T1)

    def test_insert_ligne(self) :
        """Méthode testant la méthode insert_ligne de la classe testée."""
        self.T4.insert_ligne(3)
        _tableau_T4 = [[None, "Année", "Mois", "Jour", "Nb visites", "Nb pages visitées"], [None, 2020, 12, 30, 5, 14], [None, 2020, 12, 31, 5, 18], [None, None, None, None, None, None], [None, 2021, 1, 1, 6, 10], [None, 2021, 1, 2, 11, 106]]
        self.assertEqualTableau(self.T4, _tableau_T4, True)
        self.T2.insert_ligne(4, 2)
        _tableau_T2 = [[287, "Nom erreur", "Type d'erreur", "Jour", "Mois", "Année", "Heure"],[54, "Le tableau n'est pas une liste", "TypeError", 17,1,2021,15], [381, "Le tableau est trop petit", "ValueError", 19,1,2021,10], [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", "NotImplementedError", 20,1,2021,8], [None, None, None, None, None, None, None], [None, None, None, None, None, None, None], [382, "Le tableau a trop de colonnes", "ValueError", 22,1,2021,19], [383, "Le tableau a trop de lignes", "ValueError", 22,1,2021,20], [380, "Le tableau n'a pas assez de colonnes", "ValueError", 23,1,2021,7]]
        self.assertEqualTableau(self.T2, _tableau_T2, True, True)      

    def test_get_colonne(self) :
        """Méthode testant la méthode get_colonne de la classe testée."""
        colonne_theorique1 = ["Jour", 17, 19, 20, 22, 22, 23]
        self.assertEqual(self.T2.get_colonne("C"), colonne_theorique1)
        colonne_theorique2 = [54, 381, 215, 382, 383, 380]
        self.assertEqual(self.T2.get_colonne("@"), colonne_theorique2)

    def test_set_colonne(self) :
        """Méthode testant la méthode set_colonne de la classe testée."""
        self.T4.set_colonne("D", ["Nombre visites", 6, 5, 9, 14])
        _tableau_T4 = [[None, "Année", "Mois", "Jour", "Nombre visites", "Nb pages visitées"], [None, 2020, 12, 30, 6, 14], [None, 2020, 12, 31, 5, 18], [None, 2021, 1, 1, 9, 10], [None, 2021, 1, 2, 14, 106]]
        self.assertEqualTableau(self.T4, _tableau_T4, True)
        self._tableau_T2[1][0] = 52
        self._tableau_T2[2][0] = 481
        self._tableau_T2[3][0] = 315
        self._tableau_T2[4][0] = 482
        self._tableau_T2[5][0] = 483
        self._tableau_T2[6][0] = 480
        self.T2.set_colonne("@", [52, 481, 315, 482, 483, 480])
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)

    def test_del_colonne(self) :
        """Méthode testant la méthode del_colonne de la classe testée."""
        self.T2.del_colonne("B")
        _tableau_T2 = [[287, "Nom erreur", "Jour", "Mois", "Année", "Heure"],[54, "Le tableau n'est pas une liste", 17,1,2021,15], [381, "Le tableau est trop petit", 19,1,2021,10], [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", 20,1,2021,8], [382, "Le tableau a trop de colonnes", 22,1,2021,19], [383, "Le tableau a trop de lignes", 22,1,2021,20], [380, "Le tableau n'a pas assez de colonnes", 23,1,2021,7]]
        self.assertEqualTableau(self.T2, _tableau_T2, True, True)
        self.T2.del_colonne("@")
        self.assertEqualTableau(self.T2, _tableau_T2, True)

    def test_append_colonne(self) :
        """Méthode testant la méthode append_colonne de la classe testée."""
        self.T2.append_colonne()
        _tableau_T2 = [[287, "Nom erreur", "Type d'erreur", "Jour", "Mois", "Année", "Heure", None],[54, "Le tableau n'est pas une liste", "TypeError", 17,1,2021,15, None], [381, "Le tableau est trop petit", "ValueError", 19,1,2021,10, None], [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", "NotImplementedError", 20,1,2021,8, None], [382, "Le tableau a trop de colonnes", "ValueError", 22,1,2021,19, None], [383, "Le tableau a trop de lignes", "ValueError", 22,1,2021,20, None], [380, "Le tableau n'a pas assez de colonnes", "ValueError", 23,1,2021,7, None]]
        self.assertEqualTableau(self.T2, _tableau_T2, True, True)
        self.T4.append_colonne(4)
        _tableau_T4 = [[None, "Année", "Mois", "Jour", "Nb visites", "Nb pages visitées", None, None, None, None], [None, 2020, 12, 30, 5, 14, None, None, None, None], [None, 2020, 12, 31, 5, 18, None, None, None, None], [None, 2021, 1, 1, 6, 10, None, None, None, None], [None, 2021, 1, 2, 11, 106, None, None, None, None]]
        self.assertEqualTableau(self.T4, _tableau_T4, True)
        self.assertEqualTableau(self.T1)

    def test_insert_colonne(self) :
        """Méthode testant la méthode insert_colonne de la classe testée."""
        self.T2.insert_colonne("C")
        _tableau_T2 = [[287, "Nom erreur", "Type d'erreur", None, "Jour", "Mois", "Année", "Heure"],[54, "Le tableau n'est pas une liste", "TypeError", None, 17,1,2021,15], [381, "Le tableau est trop petit", "ValueError", None, 19,1,2021,10], [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", "NotImplementedError", None, 20,1,2021,8], [382, "Le tableau a trop de colonnes", "ValueError", None, 22,1,2021,19], [383, "Le tableau a trop de lignes", "ValueError", None, 22,1,2021,20], [380, "Le tableau n'a pas assez de colonnes", "ValueError", None, 23,1,2021,7]]
        self.assertEqualTableau(self.T2, _tableau_T2, True, True)
        self.T4.insert_colonne("D", 2)
        _tableau_T4 = [[None, "Année", "Mois", "Jour", None, None, "Nb visites", "Nb pages visitées"], [None, 2020, 12, 30, None, None, 5, 14], [None, 2020, 12, 31, None, None, 5, 18], [None, 2021, 1, 1, None, None, 6, 10], [None, 2021, 1, 2, None, None, 11, 106]]
        self.assertEqualTableau(self.T4, _tableau_T4, True)

    def test_get_case(self) :
        """Méthode testant la méthode get_case de la méthode testée."""
        case_theorique = "NotImplementedError"
        self.assertEqual(self.T2.get_case("B3"), case_theorique)
        self.assertEqual(self.T2.get_case("@2"), 381)#en-tête vertical
        self.assertEqual(self.T4.get_case("D0"), "Nb visites")#en-tête horizontal
        self.assertEqual(self.T2.get_case("@0"), 287)#nom du tableau

    def test_set_case(self) :
        """Méthode testant la méthode set_case de la méthode testée."""
        self.T2.set_case("C5", "IndexError")
        self._tableau_T2[5][3] = "IndexError"
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        self.T4.set_case("B3", 2)
        self._tableau_T4[3][2] = 2
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.T2.set_case("@2", 1025)#modification en-tête vertical
        self._tableau_T2[2][0] = 1025
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        self.T4.set_case("D0", "Nombre de visites")#modification en-tête horizontal
        self._tableau_T4[0][4] = "Nombre de visites"
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.T4.set_case("@0", "Tableau n°1")
        self._tableau_T4[0][0] = "Tableau n°1"
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)

    def test_del_case(self) :
        """Méthode testant la méthode del_case de la classe testée."""
        self.T2.del_case("B5")
        self._tableau_T2[5][2] = None
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        self.T4.del_case("E2")
        self._tableau_T4[2][5] = None
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.T2.del_case("@2")#supression en-tête vertical
        self._tableau_T2[2][0] = None
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        self.T4.del_case("C0")#suppression en-tête horizontal
        self._tableau_T4[0][3] = None
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.T2.del_case("@0")
        self._tableau_T2[0][0] = None
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)

    def test_get_nom_ligne(self) :
        """Méthode testant la méthode get_nom_ligne de la classe testée."""
        nom_ligne = self.T2.get_nom_ligne(4)
        nom_ligne_theorique = 382
        self.assertEqual(nom_ligne, nom_ligne_theorique)
        with self.assertRaises(IndexError) :
            self.T1.get_nom_ligne(0)

    def test_set_nom_ligne(self) :
        """Méthode testant la méthode set_nom_ligne de la classe testée."""
        self.T3.set_nom_ligne(5, "test")
        self._tableau_T3[5][0] = "test"
        self.assertEqualTableau(self.T3, self._tableau_T3, en_tetes_v = True)
        with self.assertRaises(IndexError) :
            self.T1.set_nom_ligne(0, "tableau")

    def test_del_nom_ligne(self) :
        """Méthode testant la méthode del_nom_ligne de la classe testée."""
        self.T2.del_nom_ligne(2)
        self._tableau_T2[2][0] = None
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        with self.assertRaises(IndexError) :
            self.T1.del_nom_ligne(0)

    def test_get_nom_colonne(self) :
        """Méthode testant la méthode get_nom_colonne de la classe testée."""
        nom_colonne = self.T4.get_nom_colonne("B")
        nom_colonne_theorique = "Mois"
        self.assertEqual(nom_colonne, nom_colonne_theorique)
        with self.assertRaises(IndexError) :
            self.T1.get_nom_colonne("@")

    def test_set_nom_colonne(self) :
        """Méthode testant la méthode set_nom_colonne de la classe testée."""
        self.T2.set_nom_colonne("D", 2506)
        self._tableau_T2[0][4] = 2506
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)
        with self.assertRaises(IndexError) :
            self.T1.set_nom_colonne("@", "b a ba ...")

    def test_del_nom_colonne(self) :
        """Méthode testant la méthode del_nom_colonne de la classe testée."""
        self.T4.del_nom_colonne("C")
        self._tableau_T4[0][3] = None
        self.assertEqualTableau(self.T4, _tableau=self._tableau_T4, en_tetes_h=True)
        with self.assertRaises(IndexError) :
            self.T1.del_nom_colonne("@")

    def test_self_clear(self) :
        """Cette méthode teste la méthode clear de la classe testée.
        
        On vérifie que toutes les cases et en-têtes du tableaux valent None après l'appel de la méthode clear.
        """
        self.T4.clear()
        for i in range(len(self._tableau_T4)) :
            for j in range(len(self._tableau_T4[i])) :
                self._tableau_T4[i][j] = None
        self.assertEqualTableau(self.T4, self._tableau_T4, True)

    def test_reverse(self) :
        """Méthode testant la méthode reverse de la classe testée."""
        self.T2.reverse()
        _tableau_T2_reverse = [[287, "Nom erreur", "Type d'erreur", "Jour","Mois", "Année", "Heure"], [380, "Le tableau n'a pas assez de colonnes", 'ValueError', 23,1, 2021, 7], [383, "Le tableau a trop de lignes", 'ValueError', 22, 1, 2021, 20], [382, "Le tableau a trop de colonnes", 'ValueError', 22, 1, 2021, 19], [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", 'NotImplementedError', 20, 1, 2021, 8], [381, "Le tableau est trop petit", 'ValueError', 19, 1, 2021, 10], [54, "Le tableau n'est pas une liste", 'TypeError', 17, 1, 2021, 15]]
        self.assertEqualTableau(self.T2, _tableau_T2_reverse, True, True)

    def test_renversement_tableau(self) :
        """Méthode testant la méthode renversemen_tableau de la classe testée.
        
        Vérifie que le tableau est transformé correctement et qu'au bout de deux transformation le tableau ets identique à celui de départ.
        """
        self.T4.renversement_tableau()
        _tableau_T4_renversé = [[None, None, None, None,None], ["Année", 2020, 2020, 2021, 2021], ["Mois", 12, 12, 1, 1], ["Jour", 30, 31, 1, 2], ["Nb visites", 5, 5, 6, 11], ["Nb pages visitées", 14, 18, 10, 106]]
        self.assertEqualTableau(self.T4, _tableau_T4_renversé, False, True)
        self.T2.renversement_tableau()
        self.T2.renversement_tableau()
        self.assertEqualTableau(self.T2, self._tableau_T2, True, True)

    def test_sort_colonne(self) :
        """Méthode testant la méthode sort de la classe testée.
        
        Vérifie notamment que l'on peut trier le tableau selon le contenu d'une colonne.
        """
        self.T4.sort("E")#tri en fonction du nombre de pages visitées
        self.T4.sort("D")#tri en fonction du nombre de visites
        _tableau_T4_trié = [[None, "Année", "Mois", "Jour", "Nb visites", "Nb pages visitées"], [None, 2020, 12, 30, 5, 14], [None, 2020, 12, 31, 5, 18], [None, 2021, 1, 1, 6, 10], [None, 2021, 1, 2, 11, 106]]
        self.assertEqualTableau(self.T4, _tableau_T4_trié, True)
        self.T2.sort(key=lambda string: len(string))#index="A"
        colonne_A_theorique = ['Nom erreur', 'Le tableau est trop petit', 'Le tableau a trop de lignes', 'Le tableau a trop de colonnes', "Le tableau n'est pas une liste", "Le tableau n'a pas assez de colonnes", "Cette méthode n'est pas définie pour cette classe (classe virtuelle)."]#par ordre croissant de longueur de chaine
        self.assertEqual(self.T2["A"], colonne_A_theorique)
        self.T2.sort("C", reverse=True)#tri par date avec la date la plus récente au début
        _tableau_T2_trié = [[287, "Nom erreur",  "Type d'erreur", "Jour", "Mois", "Année", "Heure"], [380, "Le tableau n'a pas assez de colonnes", 'ValueError', 23, 1, 2021, 7], [382, "Le tableau a trop de colonnes", 'ValueError', 22, 1, 2021, 19], [383, "Le tableau a trop de lignes", 'ValueError', 22, 1, 2021, 20], [215, "Cette méthode n'est pas définie pour cette classe (classe virtuelle).", "NotImplementedError", 20, 1, 2021, 8], [381, "Le tableau est trop petit", 'ValueError', 19, 1, 2021, 10], [54, "Le tableau n'est pas une liste", 'TypeError', 17, 1, 2021, 15]]
        self.assertEqualTableau(self.T2, _tableau_T2_trié, True, True)
    
    def test_sort_ligne(self) :
        """Méthode testant la méthode sort de la classe testée.
        
        Vérifie notamment que l'on peut trier le tableau selon le contenu d'une ligne.
        """
        self.T3[1] = ["Nom du modèle", "C-min", "Kangourou", "Dieu"]
        self.T3[2] = ["Nom de la marque", "O.F.R.D.", "Nault & Re", "Citron-Haine"]
        self.T3[3] = ["Prix", 29000, 43000, 43000]
        self.T3[4] = ["Nombre de places", 5, 3, 5]
        self.T3[5] = ["Année de construction", 2018, 2017, 2020]
        self.T3[6] = ["Climatisation", True, False, True]
        self.T3[7] = ["Poids marchandise maximum", 750, 1500, 620]
        self.T3.sort(7, reverse=True)
        ligne_7_theorique = ["Poids marchandise maximum", 1500, 750, 620]
        self.assertEqual(self.T3[7], ligne_7_theorique)
        self.T3.sort("5", reverse=True)
        ligne_5_theorique = ["Année de construction", 2020, 2018, 2017]
        self.assertEqual(self.T3[5], ligne_5_theorique)
        self.T3.sort(3)
        _tableau_T3_trié = [[None, None, None, None], ["Nom du modèle", "C-min", "Dieu", "Kangourou"], ["Nom de la marque", "O.F.R.D.", "Citron-Haine", "Nault & Re"], ["Prix", 29000, 43000, 43000], ["Nombre de places", 5, 5, 3], ["Année de construction", 2018, 2020, 2017], ["Climatisation", True, True, False], ["Poids marchandise maximum", 750, 620, 1500], [None, None, None, None], [None, None, None, None]]
        self.assertEqualTableau(self.T3, _tableau_T3_trié, False, True)

    def test_import_csv(self) :
        """Méthode testant la méthode import_csv de la classe testée.
        
        Crée un tableau vide. Puis importe les données d'un fichier csv.
        """
        T_csv = Tableau(en_tetes_h=True)
        T_csv.import_csv("./tests/T4.csv")
        self.assertEqualTableau(T_csv, self._tableau_T4, en_tetes_h=True)

    def test_export_csv(self) :
        """Méthode testant la méthode import_csv de la classe testée."""
        self.T2.export_csv("./tests/T2.csv")
        with open("./tests/T2.csv", "r") as fichier_csv :
            T2_csv = fichier_csv.read()
        with open("./tests/T2_theorique.csv", "r") as fichier_csv_theorique :
            T2_csv_theorique = fichier_csv_theorique.read()
        self.assertEqual(T2_csv, T2_csv_theorique)
        os.remove("./tests/T2.csv")

    def test_lignes(self) :
        """Teste la méthode lignes de la classe testée."""
        resultat = self.T2.lignes()
        del self._tableau_T2[0]
        self.assertEqual(resultat, self._tableau_T2)

    def test_colonnes(self) :
        """Teste la méthode colonnes de la classe testée."""
        resultat = self.T4.colonnes()
        resultats_theorique = [["Année", 2020, 2020, 2021, 2021], ["Mois", 12, 12, 1, 1], ["Jour", 30, 31, 1, 2], ["Nb visites", 5, 5, 6, 11], ["Nb pages visitées", 14, 18, 10, 106]]
        self.assertEqual(resultat, resultats_theorique)

    def test_affichage(self) :
        """Teste la méthode affichage de la classe testée."""
        str_theorique1 = """      287      |   Nom erreur  | Type d'erreur |      Jour     |      Mois     |     Année     |     Heure     |\n       54      | Le tableau n'»|   TypeError   |       17      |       1       |      2021     |       15      |\n      381      | Le tableau es»|   ValueError  |       19      |       1       |      2021     |       10      |\n      215      | Cette méthode»| NotImplemente»|       20      |       1       |      2021     |       8       |\n      382      | Le tableau a »|   ValueError  |       22      |       1       |      2021     |       19      |\n      383      | Le tableau a »|   ValueError  |       22      |       1       |      2021     |       20      |\n      380      | Le tableau n'»|   ValueError  |       23      |       1       |      2021     |       7       |\n"""
        self.assertEqual(self.T2.affichage(print=False), str_theorique1)
        str_theorique2 = """  Année   |   Mois   |   Jour   |Nb visit» |Nb pages» |\n   2020   |    12    |    30    |    5     |    14    |\n   2020   |    12    |    31    |    5     |    18    |\n   2021   |    1     |    1     |    6     |    10    |\n   2021   |    1     |    2     |    11    |   106    |\n"""
        self.assertEqual(self.T4.affichage(largeur_colonne=10, print=False), str_theorique2)

    def test_index(self) :
        """Teste la méthode index de la classe testée.
        
        Teste que index revoie bien la première valeur trouvée, que l'index de la case qui est renvoyé est correct même lorsqu'il s'agit d'un en-tête.
        """
        index1 = self.T4.index(106)
        self.assertEqual(index1, "E4")
        index2 = self.T2.index("ValueError")
        self.assertEqual(index2, "B2")#B2 pour la première valeur car ValueError se retrouve plusieurs fois dans le tableau
        index3 = self.T2.index(54)
        self.assertEqual(index3, "@1")#@ pour signifier que c'est un en tete vertical 
        index4 = self.T4.index("Mois")
        self.assertEqual(index4, "B0")#0 pour signifier que c'est un en tete horizontal
        with self.assertRaises(ValueError) :
            self.T2.index("Je n'existe pas")

    def test_str_ligne(self) :
        """Méthode testant la méthode interne _str_ligne de la classe testée"""
        str_theorique1 = """      381      | Le tableau es»|   ValueError  |       19      |       1       |      2021     |       10      |"""
        self.assertEqual(self.T2._str_ligne(2), str_theorique1)
        str_theorique2 = """      287      |   Nom erreur  | Type d'erreur |      Jour     |      Mois     |     Année     |     Heure     |"""
        self.assertEqual(self.T2._str_ligne(0), str_theorique2)

    def test_str_case(self) :
        """Méthode testant la méthode interne _str_case de la classe testée."""
        str_theorique_1 = """   TypeError   """
        self.assertEqual(self.T2._str_case(1, 2), str_theorique_1)
        str_theorique_2 = """ Le tableau es»"""
        self.assertEqual(self.T2._str_case(2, 1), str_theorique_2)

    def test_index_colonne_int(self) :
        """Teste la méthode _index_colonne_int de la classe testée.
        
        Vérifie que l'entier retourné par cette méthode correspond bien à l'index passé en paramètre.
        """
        self.assertEqual(self.T1._index_colonne_int("@"), 0)#en tête vertical
        self.assertEqual(self.T1._index_colonne_int("M"), 13)
        self.assertEqual(self.T2._index_colonne_int("DX"), 128)
        self.assertEqual(self.T4._index_colonne_int("AJM"), 949)

    def test_index_colonne_str(self) :
        """Teste la méthode _index_colonne_str de la classe testée.
        
        Vérifie que la chaine retournée par cette méthode correspond bien à l'index passé en paramètre.
        """
        self.assertEqual(self.T1._index_colonne_str(0), "@")
        self.assertEqual(self.T1._index_colonne_str(13), "M")
        self.assertEqual(self.T2._index_colonne_str(128), "DX")
        self.assertEqual(self.T4._index_colonne_str(949), "AJM")

    def test_index_case_int(self) :
        """Teste la méthode _index_case_int de la méthode testée.
        
        Vérifie que cette méthode renvoie bien un tuple avec deux entiers correspondant aux index de la case.
        """
        index_case1 = self.T1._index_case_int("AD3")
        self.assertEqual(index_case1, (30,3))
        index_case2 = self.T2._index_case_int("F7")
        self.assertEqual(index_case2, (6, 7))
        index_case3 = self.T1._index_case_int("@0")
        self.assertEqual(index_case3, (0, 0))

    def test_conversion_nombres(self) :
        """Teste la méthode _conversion_nombre de la classe testée."""
        _tableau_T4_str = [[None, "Année", "Mois", "Jour", "Nb visites", "Nb pages visitées"], [None, '2020', "12", "30", "5", "14"], [None, '2020', '12', '31', '5', "18"], [None, "2021", "1.0", "1", "6", "10"], [None, "2021", "1", "2", "11", """106"""]]
        
        T4_str = Tableau(tableau=_tableau_T4_str, en_tetes_h=True)
        T4_str._conversion_nombres()
        self.assertEqualTableau(T4_str, self._tableau_T4, en_tetes_h=True)

    def Vtest_clé_ligne(self) :
        """Méthode qui teste la méthode _clé_ligne utilisée afin de trier l'objet.
        
        Vérifie que _clé_ligne renvoie bien les bonnes valeurs.
        """
        retour1 = []
        for i in range(len(self.T4._tableau)) :
            retour1.append(self.T4._clé_ligne(self.T4._tableau[i], 1))
        print(retour1)
        retour_theorique1 = [-1, 1, 0]
        self.assertEqual(retour1, retour_theorique1)
        retour2 = []
        for i in range(len(self.VC3._liste_verificateurs)) :
            retour2.append(self.VC3.clé(self.VC3._liste_verificateurs[i], 1))
        retour_theorique2 = ["Nombre de notes", "Bon élève", "Note maximale"]
        self.assertEqual(retour2, retour_theorique2)

    def test_clé_colonne(self) :
        """Teste la méthode _clé_colonne utilisée afin de trier l'objet.
        
        Vérifie que _clé_colonne renvoie bien les bonnes valeurs.
        """
        retour1 = []
        for i in range(len(self.T4._tableau)) :
            retour1.append(self.T4._clé_colonne(self.T4._tableau[i], "A"))
        retour_theorique1 = [2020, 2020, 2020, 2021, 2021]
        self.assertEqual(retour1, retour_theorique1)
        retour2 = []
        for i in range(len(self.T4._tableau)) :
            retour2.append(self.T4._clé_colonne(self.T4._tableau[i], "D"))
        retour_theorique2 = [5, 5, 5, 6, 11]
        self.assertEqual(retour2, retour_theorique2)
        retour3 = []
        for i in range(len(self.T2._tableau)) :
            retour3.append(self.T2._clé_colonne(self.T2._tableau[i], "A", key=lambda colonne :len(colonne)))
        retour_theorique3 = [25, 30, 25, 69, 29, 27, 36]
        self.assertEqual(retour3, retour_theorique3)

    def test_add(self) :
        """Teste la méthode interne _add de la classe testée.
        
        Vérifie que _add peut renvoyer un nouveau tableau regroupant les données de deux autres tableaux. vérifie aussi qu'elle peut modifier l'objet lui-même.
        """
        #test d'addition avec deux tableaux
        _tableau_addition = [[None, "Année", "Mois", "Jour", "Nb visites", "Nb pages visitées", "Nb visites deuxième site"], [None, 2020,12, 30, 5, 14, None], [None, 2020, 12, 31, 5, 18, None], [None, 2021, 1, 1, 6, 10, None], [None, 2021, 1, 2, 11, 106, None], [None, 2021, 1, 3, 9, None, 3], [None, 2021, 1, 4, 8, None, 5]]
        resultat1 = self.T4._add(self.T5)
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.assertEqualTableau(resultat1, _tableau_addition, True)
        
        #test avec une structure tableau
        resultat2 = self.T4._add(self._tableau_T5)
        self.assertEqualTableau(self.T4, self._tableau_T4, True)
        self.assertEqualTableau(resultat2, _tableau_addition, True)

        #test d'addition avec deux tableaux modifiant l'objet
        self.T4._add(self.T5, self.T4)
        self.assertEqualTableau(self.T4, _tableau_addition, True)

        #test avec une structure tableau modifiant l'objet
        self.T4._tableau = self._tableau_T4
        self.T4._add(self._tableau_T5, self.T4)
        self.assertEqualTableau(self.T4, _tableau_addition, True)


if __name__ == """__main__""" :
    unittest.main()
