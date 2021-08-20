"""Ce module teste avec unittest la classe DictionnaireOrdonné."""

import unittest
import os
import sys

#On change le dossier de travail (cwd) pour pouvoir appeler les fichiers via des chemins relatifs
os.chdir(os.path.dirname(__file__))#On change le dossier de travail en appellant le nom du dossier qui contient ce fichier (le dossier tests)
os.chdir("..")#On rechange le dossier de travail en prenant le dossier parent du dossier tests (le dossier conteneurs)
sys.path.append(os.getcwd())#ligne nécessaire à l'importation du module controle_arguments

from conteneurs.dictionnaire_ordonné import *

#enregistrement des valeurs d'entrée/sortie/erreur par défaut
default_stdin = sys.stdin
default_stdout = sys.stdout
default_stderr = sys.stderr

class TestsDictionnaireOrdonné(unittest.TestCase) :
    """Cette classe teste la classe DictionnaireOrdonné grâce à Unittest."""
    
    def setUp(self) :
        self.path_sortie = """./tests/stdout_test_DO"""

    def test_creation_DOvide(self) : #DO = dictinnaireOrdonné
        """Cette méthode teste la créaction d'un DO vide."""
        #on crée un DO vide : (on teste en même temps la méthode __str__)
        DO = DictionnaireOrdonné()
        self.flux_std(stdout=self.path_sortie)
        print(DO)
        self.flux_std()
        self.sortie.close()
        with open(self.path_sortie, "r") as fichier :
            résultat = fichier.read()
        os.remove(self.path_sortie)
        résultat_théorique = "{}\n"
        self.assertEqual(résultat, résultat_théorique)
    
    def test_creation_DOcopie_dico(self) :
        """Cette méthode teste la création d'un DO par copie d'un dico."""
        #Dico : un dictionnaire normal et DO : un dictionnaire ordonné
        Dico = {"clé1":1,"clé2":2,"clé3":3}
        DO = DictionnaireOrdonné(Dico)
        DO_théorique = DictionnaireOrdonné(clé1=1,clé2=2, clé3=3)
        self.assertCountEqual(DO, DO_théorique)

    def test_création_DOarguments(self) :
        """Cette méthode teste le passage d'arguments au constructeur du DO."""
        DO = DictionnaireOrdonné(clé1=1,clé2=2, clé3=3)
        self.flux_std(stdout = self.path_sortie)
        print(DO)
        self.flux_std()
        self.sortie.close()
        with open(self.path_sortie, "r") as fichier :
            résultat = fichier.read()
        os.remove(self.path_sortie)
        résultat_théorique = "{'clé1': 1, 'clé2': 2, 'clé3': 3}\n"
        self.assertEqual(résultat, résultat_théorique)
    
    def test_getitem(self) :
        """Cette méthode teste la méthode spéciale __getitem__.
        
        Teste l'affichage de d'une valeur par l'appel de DO[clé].
        """
        DO = DictionnaireOrdonné(clé1=1,clé2=2, clé3=3)
        self.flux_std(stdout = self.path_sortie)
        print(DO["clé2"])
        self.sortie.close()
        with open(self.path_sortie, "r") as fichier :
            résultat = fichier.read()
        os.remove(self.path_sortie)
        résultat_théorique = "2\n"
        self.assertEqual(résultat, résultat_théorique)

    def test_ajout_valeur(self) :
        """Cette méthode teste l'ajout d'un coupe clé valeur.

        Teste l'execution de DO[clé] = valeur (le couple clé-valeur doit être ajouté à la fin du DO).
        """
        DO = DictionnaireOrdonné(clé1=1,clé2=2, clé4=4)
        DO["clé3"] = 3
        DO_théorique = DictionnaireOrdonné(clé1=1, clé2=2, clé4=4, clé3=3)
        self.assertEqual(DO, DO_théorique)

    def test_setitem(self) :
        """Cette méthode teste la modification d'une valeur par __setitem__.
        
        Teste l'exécution de DO[clé] = nouvelle_valeur.
        """
        DO = DictionnaireOrdonné(clé1=1,clé2=2, clé4=4)
        DO["clé4"] = 5
        DO_théorique = DictionnaireOrdonné(clé1=1, clé2=2, clé4=5)
        self.assertEqual(DO, DO_théorique)
    
    def test_delitem(self) :
        """Cette méthode teste la suppression d'une valeur par __delitem__.

        Teste l'exécution de del DO[clé] (pour supprimer le couple clé-valeur).
        """
        DO = DictionnaireOrdonné(clé1=1,clé2=2, clé3=3, clé4=4)
        del DO["clé3"]
        DO_théorique = DictionnaireOrdonné(clé1=1, clé2=2, clé4=4)
        self.assertEqual(DO, DO_théorique)

    def test_contains(self) :
        """Cette méthode teste la recherche d'une clé dans un DO.
        
        Teste l'exécution de "clé in DO" pour rechercher la clé dans le dictionnaire. Cela appelle la méthode spéciale __contains__ qui est testée par cette méthode.
        """
        DO = DictionnaireOrdonné(clé1=1,clé2=2, clé3=3, clé4=4)
        Résultat1 = "clé2" in DO
        Résultat_théorique1 = True
        self.assertEqual(Résultat1, Résultat_théorique1)
        Résultat2 = "clé6" in DO
        Résultat_théorique2 = False
        self.assertEqual(Résultat2, Résultat_théorique2)
    
    
    def test_insert(self) :
        """Cette méthode teste la méthode insert de la classe DO.
        
        Vérifie que si l'index est supérieur à len(DO)+1 est levé et que si ce n'est pas le cas la paire clé/valeur est inséré au bon endroit du dictionnaire ordonné. 
        """
        DO = DictionnaireOrdonné(clé1=1,clé2=2, clé3=3, clé4=4)
        with self.assertRaises(IndexError) :
            DO.insert(5, "clé6", 6)
        DO.insert(4, "clé5", 5)
        self.assertEqual(DO, DictionnaireOrdonné(clé1=1,clé2=2, clé3=3, clé4=4,clé5=5))
        DO.insert(3, "newKey", 66)
        self.assertEqual(DO, DictionnaireOrdonné(clé1=1,clé2=2, clé3=3, newKey=66, clé4=4,clé5=5))

    
    def test_len(self) :
        """Cette méthode teste la métode len de la classe DO.

        Teste la méthode len qui renvoie la longueur (le nombre de clés) du DO.
        """
        DO1 = DictionnaireOrdonné()
        Résultat1 = len(DO1)
        Résultat_théorique1 = 0
        self.assertEqual(Résultat1, Résultat_théorique1)
        DO2 = DictionnaireOrdonné(clé1=1,clé2=2, clé3=3, clé4=4)
        Résultat2 = len(DO2)
        Résultat_théorique2 = 4
        self.assertEqual(Résultat2,Résultat_théorique2)

    def test_sort(self) :
        """Cette méthode teste la méthode sort de la classe DO.

        teste que la méthode sort trie bien le dictionnaire en fonction de ses clés.
        """
        #test de clé str à trier par ordre alphabétique
        DO1 = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        DO1.sort()
        DO_théorique1 = DictionnaireOrdonné(A=457, Ca=44, Ce=list(), G=1,U="a", Z=4)
        self.assertEqual(DO1, DO_théorique1)
        #test de clé int et float à trier par ordre croissant
        DO2 = DictionnaireOrdonné()
        DO2[44] = [5,4,99]
        DO2[2.66] = "c"
        DO2[0] = "b"
        DO2[2] = 5
        DO2[101.568] = "a"
        DO2[-5.2] = {}
        DO2[0.5] = "e"
        DO2.sort()#tri
        #création et remplissage du DO théorique
        DO_théorique2 = DictionnaireOrdonné()
        DO_théorique2[-5.2] = {}
        DO_théorique2[0] = "b"
        DO_théorique2[0.5] = "e"
        DO_théorique2[2] = 5
        DO_théorique2[2.66] = "c"
        DO_théorique2[44] = [5,4,99]
        DO_théorique2[101.568] = "a"
        self.assertEqual(DO2, DO_théorique2)

    def test_reverse(self) : 
        """Cette méthode teste la méthode reverse de la classe DO.
        
        Cette méthode vérifie que reverse inverse bien l'ordre du dictionnaire.Et que "sort(reverse=True)" trie selon les clé et inverse le dictionnaire. ("sort(reverse=True)" appelle inplicitement la méthode reverse.)
        """ 
        DO1 = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        DO1.reverse()
        DO_théorique1 = DictionnaireOrdonné(U="a", Z=4, Ce=list(), A=457,Ca=44, G=1)
        self.assertEqual(DO1, DO_théorique1)
        DO2 = DictionnaireOrdonné()
        DO2[44] = [5,4,99]
        DO2[2.66] = "c"
        DO2[0] = "b"
        DO2[2] = 5
        DO2[101.568] = "a"
        DO2[-5.2] = {}
        DO2[0.5] = "e"
        DO2.sort(reverse=True)
        #création et remplissage du DO théorique
        DO_théorique2 = DictionnaireOrdonné()
        DO_théorique2[101.568] = "a"
        DO_théorique2[44] = [5,4,99]
        DO_théorique2[2.66] = "c"
        DO_théorique2[2] = 5
        DO_théorique2[0.5] = "e"
        DO_théorique2[0] = "b"
        DO_théorique2[-5.2] = {}
        self.assertEqual(DO2, DO_théorique2)

    def test_iter(self) :
        """Cette méthode teste la méthode spéciale __iter__ de la classe DO.
        
        Cette méthode teste la méthode __iter__ qui parcourt l'objet (DO) et renvoie la liste des clés. Test effectué par l'exécution de "for clé in DO :".
        """
        DO = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        self.flux_std(stdout = self.path_sortie)
        for clé in DO :
            print(clé)
        self.flux_std()
        self.sortie.close()
        with open(self.path_sortie, "r") as fichier :
            résultat = fichier.read()
        os.remove(self.path_sortie)
        résultat_théorique = """G\nCa\nA\nCe\nZ\nU\n"""
        self.assertEqual(résultat, résultat_théorique)

    def test_keys(self) :
        """Cette méthode teste la méthode keys de la classe DO.
        
        Vérifie que la méthode keys renvoie bien la liste des clés.
        """
        DO = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        résultat = DO.keys()
        résultat_théorique = ["G", "Ca", "A", "Ce", "Z", "U"]
        self.assertEqual(résultat, résultat_théorique)
    
    def test_values(self) :
        """Cette méthode teste la méthode values de la classe DO.
        
        Vérifie que la méthode values renvoie bien la liste des valeurs.
        """
        DO = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        résultat = DO.values()
        résultat_théorique = [1, 44, 457, [], 4, "a"]
        self.assertEqual(résultat, résultat_théorique)
    
    def test_items(self) :
        """Cette méthode teste la méthode items de la classe DO.
        
        Vérifie que la méthode items renvoie bien un dictionnaire avec les couples clé-valeur.
        """
        DO = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        self.flux_std(stdout = self.path_sortie)
        for clé, valeur in DO.items() :
            print(clé, ":", valeur)
        self.flux_std()
        self.sortie.close()
        with open(self.path_sortie, "r") as fichier :
            résultat = fichier.read()
        os.remove(self.path_sortie)
        résultat_théorique = """G : 1\nCa : 44\nA : 457\nCe : []\nZ : 4\nU : a\n"""
        self.assertEqual(résultat, résultat_théorique)

    def test_add(self) :
        """Cette méthode teste la méthode spécialle __add__ de la clase DO.

        Vérifie qu'une addition entre deux DO se fait correctement (appel implicite de __add__). Vérifie aussi que l'on peut faire DictionnaireOrdonné + DictionnaireUsuel.
        """
        DO1 = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        DO2 = DictionnaireOrdonné(H=2, Db=66, B=500, Dm=[3,5], Y=7, V="i")
        DO3 = DO1+DO2
        DO_théorique3 = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a", H=2, Db=66, B=500, Dm=[3,5], Y=7, V="i")
        self.assertEqual(DO3, DO_théorique3)
        D = dict(H=2, Db=66, B=500, Dm=[3,5], Y=7, V="i")
        DO4 = DO1 + D
        DO_théorique4 = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a", H=2, Db=66, B=500, Dm=[3,5], Y=7, V="i")
        self.assertEqual(DO4, DO_théorique4)

    
    def test_radd(self) :
        """Cette méthode teste la méthode spéciale __radd__ de la classe DO.
        
        Vérifie qu'une addition telle que DictionnaireUsuel + DictionnaireOrdonné est possible (appel implicite de __radd__).
        """
        D = dict(H=2, Db=66, B=500, Dm=[3,5], Y=7, V="i")
        DO1 = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        DO2 = D + DO1
        DO_théorique2 = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a", H=2, Db=66, B=500, Dm=[3,5], Y=7, V="i")
        self.assertEqual(DO2, DO_théorique2)

    def test_eq(self) :
        """Cette méthode teste la méthode spéciale __eq__ de la classe DO.
        
        Vérifie que deux dictionnaires sont bien reconnu égaux quand ils ont les mêmes clé et les mêmes valeurs dans le même ordre (appel implicite de __eq__ par la condition utilisant ==). Vérifie aussi que deux DO avec les mêmes clé et les mêmes valeurs mais dans un ordre différents ne sont pas égaux (l'ordre est important).
        """
        DO1 = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        DO2 = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        E1 = False#égalité 1 False : pas égaux
        if DO1==DO2 :
            E1 = True
        self.assertTrue(E1)
        DO3 = DictionnaireOrdonné(U="a", Z=4, Ce=list(), A=457,Ca=44, G=1)
        E2 = False
        if DO1==DO3 :
            E2 = True
        self.assertFalse(E2)
    
    def test_ne(self) :
        """Cette méthode teste la méthode spéciale __ne__ de la classe DO.
        
        Vérifie que deux dictionnaires ne sont pas reconnu diférents quand ils ont les mêmes clé et les mêmes valeurs dans le même ordre (appel implicite de __ne__ par la condition utilisant !=). Vérifie aussi que deux DO avec les mêmes clé et les mêmes valeurs mais dans un ordre différents sont différents (l'ordre est important). Vérifie que deux DO sans clés identiques ni valeur identiques sont bien différents.
        """
        DO1 = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        DO2 = DictionnaireOrdonné(G=1, Ca=44, A=457, Ce=list(), Z=4, U="a")
        NE1 = False#non égalité 1 False : pas différents
        if DO1!=DO2 :
            NE1 = True
        self.assertFalse(NE1)
        DO3 = DictionnaireOrdonné(U="a", Z=4, Ce=list(), A=457,Ca=44, G=1)
        NE2 = False
        if DO1!=DO3 :
            NE2 = True
        self.assertTrue(NE2)
        DO4 = DictionnaireOrdonné()
        DO4[44] = [5,4,99]
        DO4[2.66] = "c"
        DO4[0] = "b"
        DO4[2] = 5
        DO4[101.568] = "a"
        DO4[-5.2] = {}
        DO4[0.5] = "e"
        NE3 = False
        if DO1!=DO3 :
            NE3 = True
        self.assertTrue(NE3)


    def flux_std(self, stdin=None, text="", stdout=None, stderr=None) :
        """Cette fonction modifie les flux standarts (entrée, sortie et/ou erreur).

        La fonction crée des fichiers au(x) chemin(s) précisé(s) et modifie les flux. Si un paramètre pour un flux vaut None, le flux est mis à la valeur par défaut. On passe en paramètre de texte le contenu à mettre dans le fichier d'entrée (c'est les instuctions à donner au programme).
        """
        #pour l'entrée :
        if stdin and text != "" :
            with open(stdin, "w") as f_stdin_w :
                f_stdin_w.write(text)
        if stdin :
            self.entrée = open(stdin, "r")
            sys.stdin = self.entrée
        else :
            sys.stdin =default_stdin
        #pour la sortie :
        if stdout :
            self.sortie = open(stdout, "w")
            sys.stdout = self.sortie
        else :
            sys.stdout =default_stdout
        #pour l'erreur
        if stderr :
            self.erreur = open(stderr, "w")
            sys.stderr = self.erreur
        else :
            sys.stderr =default_stderr

if __name__ == """__main__""" :
    unittest.main()
