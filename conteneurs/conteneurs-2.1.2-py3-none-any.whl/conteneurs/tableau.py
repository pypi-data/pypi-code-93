"""Ce module contient la classe Tableau."""

import re
import csv
import math
import copy

from outils_de_controles.controle_arguments import *
from outils_de_controles.verificateur import *
from outils_de_controles.verificateur_str import *
from outils_de_controles.verificateur_arguments import *
from outils_de_controles.verificateur_listes import *
from outils_de_controles.verificateur_tableaux import *

#constantes
max_lignes = 2**20#nombre maximal de ligne = longueur maximale d'une colonne
max_colonnes = 2**10#nombre maximal de colonnes = longueur maximale du tableau

# définition des expressions régulières couralmment utilisés
re_index = re.compile(r"^([A-Z@][A-Z]{0,2})?([0-9]{1,7})?$")#un index valide correspond toujours à cette re
re_index_ligne = re.compile(r"^[0-9]{1,7}$")#index correspondant à une ligne
re_index_colonne = re.compile(r"^[A-Z@][A-Z]{0,2}$")#index correspondant à une colonne
re_index_case = re.compile(r"^([A-Z@][A-Z]{0,2})([0-9]{1,7})$")#index corresondant à une case
re_index_partie_ligne = re.compile(r"[0-9]{1,7}$")
re_index_partie_colonne = re.compile(r"^[A-Z@][A-Z]{0,2}")
re_index_ligne_ou_colonne = re.compile(r"^([A-Z@][A-Z]{0,2})|[0-9]{1,7}$")

#définition du VerificateurTableaux
VTtableau = VerificateurTableaux(maximum=(max_colonnes,max_lignes), nom_tableau=Verificateur())
VTtableau.append(1, max_colonnes, Verificateur())#on ne controle pas le contenu des cases du tableau

#définition des vérificateurs souvant utilisés
VSfichier_csv = VerificateurStr(minimum=5, regex=r"[A-Za-z0-9-]+.csv$")#le fichier doit avoir l'extension .csv
VSindex = VerificateurStr(1, regex=re_index)
Vindex_ligne = Verificateur(int, 0)
VSindex_colonne = VerificateurStr(minimum=1, maximum=3, regex=re_index_colonne)
Vlargeur_colonne = Verificateur(int, 3, 100)
VLdimensions = VerificateurListes(types=(list, tuple), minimum=2, maximum=2)
VLdimensions.append(0, None, Verificateur(int, 1, max_colonnes))
VLdimensions.append(1, None, Verificateur(int, 1, max_lignes))
VSindex_ligne_ou_colonne = VerificateurStr(regex=re_index_ligne_ou_colonne)
VSsep = VerificateurStr(0, 1)#pour les séparateurs de colonnes

# définition des VerificateurArguments
VAinit = VerificateurArguments()
VAinit.append(0, verificateur=Verificateur())#correspond à l'argument self
VAinit.append(None, "tableau", VTtableau)
VAinit.append(None, "dimensions", VLdimensions)
VAinit.append(None, "fichier_csv", VSfichier_csv)
VAinit.append(None, "en_tetes_h", Verificateur(types=bool))
VAinit.append(None, "en_tetes_v", Verificateur(types=bool))

VAgetitem = VerificateurArguments()
VAgetitem.append(0,verificateur=Verificateur())
VAgetitem.append(1, "index", VSindex)

VAsetitem = VerificateurArguments()
VAsetitem.append(0,verificateur=Verificateur())
VAsetitem.append(1, "index", VSindex)
VAsetitem.append(2, "nouvelle_valeur", Verificateur())

VAadd = VerificateurArguments()
VAadd.append(0, "self", Verificateur())
VAadd.append(1, "tableau_ajout", Verificateur())

VAset_nom_tableau = VerificateurArguments()
VAset_nom_tableau.append(0, verificateur=Verificateur())
VAset_nom_tableau.append(1, "nouveau_nom", Verificateur())

VAset_en_tetes = VerificateurArguments()
VAset_en_tetes.append(0, verificateur=Verificateur())
VAset_en_tetes.append(1, "nouvelle_valeur", Verificateur(bool))

VAset_dimensions = VerificateurArguments()
VAset_dimensions.append(0, "self", Verificateur())
VAset_dimensions.append(1, "nouvelles_dimensions", VLdimensions)

VAget_ligne = VerificateurArguments()
VAget_ligne.append(0, verificateur=Verificateur())
VAget_ligne.append(1, "index_ligne", Vindex_ligne)

VAset_ligne = VerificateurArguments()
VAset_ligne.append(0, verificateur=Verificateur())#correspond à l'argument self
VAset_ligne.append(1, "index_ligne", Vindex_ligne)
VAset_ligne.append(2, "nouvelle_ligne", VerificateurListes())

VAappend_ligne = VerificateurArguments()
VAappend_ligne.append(0, verificateur=Verificateur())#correspond à l'argument self
VAappend_ligne.append(1, "nb_lignes", Verificateur(int, 1))

VAinsert_ligne = VerificateurArguments()
VAinsert_ligne.append(0, verificateur=Verificateur())#correspond à l'argument self
VAinsert_ligne.append(1, "position", Vindex_ligne)
VAinsert_ligne.append(2, "nb_lignes", Verificateur(int, 1))

VAget_colonne = VerificateurArguments()
VAget_colonne.append(0, verificateur=Verificateur())
VAget_colonne.append(1, "index_colonne", VSindex_colonne)

VAset_colonne = VerificateurArguments()
VAset_colonne.append(0, verificateur=Verificateur())
VAset_colonne.append(1, "index_colonne", VSindex_colonne)
VAset_colonne.append(2, "nouvelle_valeur", VerificateurListes())

VAappend_colonne = VerificateurArguments()
VAappend_colonne.append(0, verificateur=Verificateur())#correspond à l'argument self
VAappend_colonne.append(1, "nb_colonnes", Verificateur(int, 1))

VAinsert_colonne = VerificateurArguments()
VAinsert_colonne.append(0, verificateur=Verificateur())#correspond à l'argument self
VAinsert_colonne.append(1, "position", VSindex_colonne)
VAinsert_colonne.append(2, "nb_colonnes", Verificateur(int, 1))

VAget_case = VerificateurArguments()
VAget_case.append(0, verificateur=Verificateur())
VAget_case.append(1, "index", VerificateurStr(minimum=1, regex=re_index_case))

VAset_case = VerificateurArguments()
VAset_case.append(0, verificateur=Verificateur())
VAset_case.append(1, "index", VerificateurStr(minimum=1, regex=re_index_case))
VAset_case.append(2, "nouvelle_valeur", Verificateur())

VAget_nom_ligne = VerificateurArguments()
VAget_nom_ligne.append(0, verificateur=Verificateur())
VAget_nom_ligne.append(1, "index_ligne", Vindex_ligne)

VAset_nom_ligne = VerificateurArguments()
VAset_nom_ligne.append(0, verificateur=Verificateur())
VAset_nom_ligne.append(1, "index_ligne", Vindex_ligne)
VAset_nom_ligne.append(2, "nouveau_nom", Verificateur())

VAget_nom_colonne = VerificateurArguments()
VAget_nom_colonne.append(0, verificateur=Verificateur())
VAget_nom_colonne.append(1, "index_colonne", VSindex_colonne)

VAset_nom_colonne = VerificateurArguments()
VAset_nom_colonne.append(0, verificateur=Verificateur())
VAset_nom_colonne.append(1, "index_colonne", VSindex_colonne)
VAset_nom_colonne.append(2, "nouveau_nom", Verificateur())

VAreverse = VerificateurArguments()
VAreverse.append(0, verificateur=Verificateur())
VAreverse.append(1, "index", VSindex_ligne_ou_colonne)

VAsort = VerificateurArguments()
VAsort.append(0, verificateur=Verificateur())
VAsort.append(1, "index", VSindex_ligne_ou_colonne)
VAsort.append(None, "key", Verificateur())
VAsort.append(None, "reverse", Verificateur(bool))

VAimport_csv = VerificateurArguments()
VAimport_csv.append(0, verificateur=Verificateur())
VAimport_csv.append(1, "fichier_csv", VSfichier_csv)

VAexport_csv = VerificateurArguments()
VAexport_csv.append(0, verificateur=Verificateur())
VAexport_csv.append(1, "fichier_csv", VSfichier_csv)
VAexport_csv.append(2, "dialect", VerificateurStr())

VAaffichage = VerificateurArguments()
VAaffichage.append(0, "self", Verificateur())
VAaffichage.append(1, "largeur_colonne", Vlargeur_colonne)
VAaffichage.append(2, "sep", VSsep)
VAaffichage.append(3, "print", Verificateur(bool))

VA_str_ligne = VerificateurArguments()
VA_str_ligne.append(0, verificateur=Verificateur())#correspond à l'argument self
VA_str_ligne.append(1, "index_ligne", Vindex_ligne)
VA_str_ligne.append(2, "largeur_colonne", Vlargeur_colonne)
VA_str_ligne.append(3, "sep", VSsep)

VA_str_case = VerificateurArguments()
VA_str_case.append(0, verificateur=Verificateur())#correspond à l'argument self
VA_str_case.append(1, "index_ligne", Vindex_ligne)
VA_str_case.append(2, "index_colonne_int", Verificateur(int, 0))
VA_str_case.append(3, "largeur_colonne", Vlargeur_colonne)

VA_index_colonne_int = VerificateurArguments()
VA_index_colonne_int.append(0, verificateur=Verificateur())
VA_index_colonne_int.append(1, "index_colonne", VSindex_colonne)

VA_index_colonne_str = VerificateurArguments()
VA_index_colonne_str.append(0, verificateur=Verificateur())
VA_index_colonne_str.append(1, "index_colonne_int", Vindex_ligne)

VA_index_case_int = VerificateurArguments()
VA_index_case_int.append(0, verificateur=Verificateur())
VA_index_case_int.append(1, "index", VerificateurStr(minimum=1, regex=re_index_case))

VA_clé_ligne = VerificateurArguments()
VA_clé_ligne.append(0, "self", Verificateur())
VA_clé_ligne.append(1, "ligne", Verificateur())
VA_clé_ligne.append(2, "index_ligne", Vindex_ligne)
VA_clé_ligne.append(None, "key", Verificateur())

VA_clé_colonne = VerificateurArguments()
VA_clé_colonne.append(0, "self", Verificateur())
VA_clé_colonne.append(1, "ligne", Verificateur())
VA_clé_colonne.append(2, "index_colonne", VSindex_colonne)
VA_clé_colonne.append(None, "key", Verificateur())

class Tableau :
    """Cette classe permet de créer des objets représentant des tableaux.
    
    Cette classe a trois arguments : le tableau lui-même représenté par des listes imbriquées, l'attribut "en_tetes_h" qui définit si le tableau possède des noms de colonnes et l'attribut "en_tetes_v" qui définit si le tableau possède des noms de lignes.
    """

    #Méthodes spéciales

    @controle_arguments(VAinit)
    def __init__(self, tableau=[[None,None],[None,None]], fichier_csv="",dimensions=(1,1), en_tetes_h=False, en_tetes_v=False) :
        """Cette méthode initialise les attributs de l'objet Tableau.

        La paramètre en_tetes_h et en_tetes_v doivent être des booléens.
        Ensuite, on peut préciser un des autres paramètres :
        - soit le paramètre tableau qui doit être une liste contenant une liste par ligne.
        - soit le paramètre fichier_csv qui permet d'importer un tableau enregistré dans un fichier csv.
        - soit le paramètre dimension qui permet de créer un tableau vide avec les dimensions précisés.
        Après quelques vérifications, cette méthode donne aux attributs les valeurs des trois paramètres.
        """
        #initialisation des paramètres des en-têtes
        self._en_tetes_h = en_tetes_h
        self._en_tetes_v = en_tetes_v

        #les vérifications sont faites grâce au décorateur controle_arguments
        self._tableau = tableau

        if dimensions != (1,1) :
            nb_colonnes = dimensions[0]+1
            nb_lignes = dimensions[1]+1
            tableau_dim = [[None]*nb_colonnes]*nb_lignes
            #for i in range(dimensions[1]+1) :
            #    tableau_dim.append([None]*(dimensions[0]+1))
            self._tableau = tableau_dim

        if fichier_csv :
            self.import_csv(fichier_csv)

    def __repr__(self) :
        """Méthode spéciale appelé quand on cherche à représenter l'objet.
        
        Représentation de l'objet. C'est cette chaîne qui sera affichée quand on saisit directement le dictionnaire dans l'interpréteur, ou en utilisant la fonction 'repr'. Utile pour le débuggage.
        """
        return "conteneurs.Tableau(tableau={obj._tableau}, en_tetes_h={obj._en_tetes_h}, en_tetes_v={obj._en_tetes_v})".format(obj = self)
    
    def __str__(self) :
        """Méthode appelée quand on souhaite afficher le tableau.
        
        Méthode appellée par la fonction 'print' quand le tableau est converti en chaîne grâce au constructeur 'str'.
        """
        return self.affichage(print=False)

    def __eq__(self, autre_tableau) :
        """Méthode renvoyant un booléen indiquant si deux tableaux sont égaux.
        
        Si l'autre tableau est un objet Tableau, cette méthode spéciale vérifie que chaque attribut sont égaux sur les deux tableaux. Si les en-têtes sont activés mais que l'autre tableau n'est pas un objet Tableau, les deux tableaux sont équaux si self._tableau == autre_tableau. (Car il contiennent les mêmes données).
        """
        retour = False
        if isinstance(autre_tableau, Tableau) :
            if self._tableau == autre_tableau._tableau and self._en_tetes_h == autre_tableau._en_tetes_h and self._en_tetes_v == autre_tableau._en_tetes_v :
                retour = True
        elif self._tableau == autre_tableau and self._en_tetes_h == True and self._en_tetes_v == True :
            retour = True
        return retour
    
    def __ne__(self, autre_tableau) :
        """Renvoie un booléen indiquant si deux tableaux sont différents.
        
        Si l'autre tableau est un objet Tableau, cette méthode spéciale vérifie qu'un des attributs est différent sur les deux tableaux. Si les en-têtes sont activés mais que l'autre tableau n'est pas un objet Tableau, les deux tableaux sont différents si self._tableau != autre_tableau. (Car il contiennent les mêmes données).
        """
        return not self.__eq__(autre_tableau)#on renvoie l'inverse de __eq__

    @controle_arguments(VAgetitem, conversion=True)
    def __getitem__(self, index) :
        """Retourne la valeur correspondant à l'index donné.
        
        Si l'index est un chiffre, on retourne la ligne correspondante. si ce sont des lettres, on retourne la colonne correspondante et s'il y a des lettres suivies par des chiffre on retourne le contenu de la case correspondante.
        """
        if re_index_ligne.search(index) : #s'il n'y a que des chiffres
            return self.get_ligne(index)
        elif re_index_colonne.search(index) : #il n'y a que des lettres
            return self.get_colonne(index)
        else :
            return self.get_case(index)

    @controle_arguments(VAsetitem, conversion=True)
    def __setitem__(self, index, nouvelle_valeur) :
        """Modifie la valeur correspondant à l'index donné.
        
        En général, on fourni l'index d'une case et sa nouvelle valeur. Peut aussi modifier toute une ligne ou tout une colonne, voir les méthodes set_ligne et set_colonne, appelées par cette méthode.
        """
        if re_index_ligne.search(index) : #s'il n'y a que des chiffres
            return self.set_ligne(index, nouvelle_valeur)
        elif re_index_colonne.search(index) : #il n'y a que des lettres
            return self.set_colonne(index, nouvelle_valeur)
        else :
            return self.set_case(index, nouvelle_valeur)

    @controle_arguments(VAgetitem, conversion=True)
    def __delitem__(self, index) :
        """Supprime la valeur correspondant à l'index donné.
        
        Si l'index correspond à une case, la case vaut alors None mais si l'index correspond à une ligne ou une colonne, la ligne ou colonne est supprimée et le tableau retrécit.
        """
        if re_index_ligne.search(index) : #s'il n'y a que des chiffres
            return self.del_ligne(index)
        elif re_index_colonne.search(index) : #il n'y a que des lettres
            return self.del_colonne(index)
        else :
            return self.del_case(index)

    def __contains__(self, valeur) :
        """Indique si le tableau contient la valeur cherchée.
        
        Retourne True si une des cases du tableau est égale à la valeur fournie.
        """
        retour = False
        for contenu in self :#on utilise la méthode spécialle __iter__ qui renvoie la liste de toute les cases du tableau.
            if contenu == valeur :
                retour = True
                break 
        return retour
    
    def __len__(self) :
        """Retourne le nombre de cases contenus dans le tableau.
        
        Les en-têtes ne sont pas comptés.
        """
        return self.dimensions[0]*self.dimensions[1]#nb_colonnes x nb lignes

    def __iter__(self) :
        """Retourne un itérateur qui parcours toutes les cases du tableau."""
        liste_cases = []
        for ligne in self.get_tableau() :
            for case in ligne :
                liste_cases.append(case)
        return iter(liste_cases)

    @controle_arguments(VAadd)
    def __add__(self, tableau_ajout) :
        """Renvoie un tableau avec les données de self et de tableau_ajout.

        Les données de self et de tableau_ajout sont intégrées dans un nouveau tableau qui est renvoyé.
        Tableau_ajout doit être un objet Tableau ou un objet correspondant à une structure de tableau (liste comprenant des sous-listes).
        """
        return self._add(tableau_ajout)

    @controle_arguments(VAadd)
    def __radd__(self, tableau_ajout) :
        """Renvoie un tableau avec les données de self et de tableau_ajout.
        
        Les données de self et de tableau_ajout sont intégrées dans un nouveau tableau qui est renvoyé.
        Tableau_ajout doit être un objet Tableau ou un objet correspondant à une structure de tableau (liste comprenant des sous-listes).
        """
        if isinstance(tableau_ajout, list) :#structure de tableau mais pas un objet Tableau
            VTtableau.controle_total(tableau_ajout)
            tableau_ajout = Tableau(tableau=tableau_ajout, en_tetes_h=True, en_tetes_v=True)#conversion en tableau
        Verificateur(Tableau).controle_total(tableau_ajout)
        return tableau_ajout + self

    @controle_arguments(VAadd)
    def __iadd__(self, tableau_ajout) :
        """Ajoute à self les données de self et de tableau_ajout.

        Les données de tableau_ajout sont intégrées dans le tableau (self).
        Tableau_ajout doit être un objet Tableau ou un objet correspondant à une structure de tableau (liste comprenant des sous-listes).
        """
        return self._add(tableau_ajout, self)

    #Accesseurs, mutateurs et suppresseurs des attributs de cette classe

    def get_tableau(self) :
        """Retourne l'attribut tableau.
        
        Si les en-têtes ne sont pas activées, les en-têtes ne sont pas renvoyés.
        """
        tableau = []
        for index_ligne in range(len(self._tableau)) :
            if index_ligne == 0 and self._en_tetes_h :
                ligne_en_tetes = self[index_ligne]
                if self._en_tetes_v :
                    ligne_en_tetes.insert(0, self._tableau[0][0])#on rajoute le nom du tableau
                tableau.append(ligne_en_tetes)
            if index_ligne !=0 :
                tableau.append(self[index_ligne])
        return tableau

    def get_en_tetes_h(self) :
        """Retourne l'attribut en_tetes_h qui est un booléen."""
        return self._en_tetes_h
    
    @controle_arguments(VAset_en_tetes)
    def set_en_tetes_h(self, nouvelle_valeur) :
        """Modifie l'attribut en_tetes_h.
        
        La nouvelle valeur doit être un booléen.
        """
        self._en_tetes_h = nouvelle_valeur

    def get_en_tetes_v(self) :
        """Retourne l'attribut en_tetes_v qui est un booléen."""
        return self._en_tetes_v
    
    @controle_arguments(VAset_en_tetes)
    def set_en_tetes_v(self, nouvelle_valeur) :
        """Modifie l'attribut en_tetes_v.
        
        La nouvelle valeur doit être un booléen.
        """
        self._en_tetes_v = nouvelle_valeur

    def get_nom_tableau(self) :
        """Retourne le nom du tableau."""
        return self._tableau[0][0]
    
    @controle_arguments(VAset_nom_tableau)
    def set_nom_tableau(self, nouveau_nom) :
        """Modifie le nom du tableau."""
        self._tableau[0][0] = nouveau_nom

    def del_nom_tableau(self) :
        """Supprimme le nom du tableau.
        
        Le nom du tableau devient None.
        """
        self._tableau[0][0] = None

    def get_dimensions(self) :
        """Retourne les dimensions du tableau sous forme de tuple.
        
        Les en-têtes ne sont pas comptés dans les dimmensions du tableau.
        """
        nb_colonnes = len(self._tableau[0])-1#-1 car on ne compte pas les en-têtes
        nb_lignes = len(self._tableau)-1#-1 car on ne compte pas les en-têtes
        return (nb_colonnes, nb_lignes)

    @controle_arguments(VAset_dimensions)
    def set_dimensions(self, nouvelles_dimensions) :
        """Change les dimensions du tableau."""
        difference_de_lignes = nouvelles_dimensions[1]-self.dimensions[1]
        if difference_de_lignes > 0 :#pas assez de lignes
            self.append_ligne(difference_de_lignes)
        while self.dimensions[1] > nouvelles_dimensions[1] :
            self.del_ligne(self.dimensions[1])

        difference_de_colonnes = nouvelles_dimensions[0]-self.dimensions[0]
        if difference_de_colonnes > 0 :#pas assez de colonnes
            self.append_colonne(difference_de_colonnes)
        while self.dimensions[0] > nouvelles_dimensions[0] :
            for index_ligne in range(len(self._tableau)) :
                del self._tableau[index_ligne][self.dimensions[0]]
    
    def del_dimensions(self) :
        """Il est impossible de supprimer les dimensions du tableau."""
        raise NotImplementedError("""Il est impossible de supprimer les dimensions du tableau.""")

    #Méthodes pour les lignes, colonnes et cases

    @controle_arguments(VAget_ligne, conversion=True)
    def get_ligne(self, index_ligne) :
        """Retourne la liste des éléments contenus dans la ligne.
        
        Si en_tetes_v vaut True, le premier élément est l'en-tête. Vient ensuite les éléments de la ligne. L'ordre des éléments est conservé.
        """
        Verificateur(int, 0, len(self._tableau)-1).controle_total(index_ligne)#vérifie que ligne est valide
        if index_ligne == 0 and not self._en_tetes_h :
            raise IndexError("Impossible d'afficher les en-têtes horizontaux car ils sont désactivés (self.en_tetes_h = False).")
        liste = []
        for i in range(len(self._tableau[index_ligne])) :
            if i==0 and self._en_tetes_v and index_ligne != 0 : #si c'est la première case d'une ligne est que les en-têtes verticales sont activées
               liste.append(self._tableau[index_ligne][0])
            if i!=0 :
                liste.append(self._tableau[index_ligne][i])
        return liste
    
    @controle_arguments(VAset_ligne, conversion=True)
    def set_ligne(self, index_ligne, nouvelle_valeur) :
        """Modifie la ligne correspondant à l'index fourni.
        
        La ligne a pour valeur nouvelle_valeur, qui doit être une liste avec la même nombre d'éléments que les autres lignes.
        """
        Verificateur(int, 0, len(self._tableau)-1).controle_total(index_ligne)#vérifie que ligne est valide
        longueur_liste = len(self._tableau[0])#le nombre de colonnes ; la liste doit avoir autant d'éléments que ce nombre. Même s'il n'y a pas d'en-tête il faut une case d'en-tête
        if index_ligne == 0 :
            if not self._en_tetes_h :
                raise IndexError("Les en-têtes horizontaux ne sont pas activés donc il n'est pas possible de les modifier.")
            nouvelle_valeur.insert(0, self._tableau[0][0])
        elif not self._en_tetes_v :#s'il n'y a pas d'en-têtes, l'utilisateur ne saisi pas de case pour les en-têtes 
            nouvelle_valeur.insert(0, self._tableau[index_ligne][0])#mais on en rajoute une en conservant la valeur de l'en-tête d'origine
        VLliste = VerificateurListes(minimum=longueur_liste, maximum=longueur_liste)#Vérification de la longueur et du type de la liste
        nouvelle_valeur = VLliste.controle_total(nouvelle_valeur)
        self._tableau[index_ligne] = nouvelle_valeur

    @controle_arguments(VAget_ligne, conversion=True)
    def del_ligne(self, index_ligne) :
        """Supprime la ligne correspondant à l'index donné.
        
        La ligne est supprimée, c'est à dire que sa place dans le tableau est enlevée et les lignes qui sont en-dessous remontent d'un cran. Les dimensions du tableau changent. Si on tente de supprimer la ligne des en-têtes avec l'index 0, on désactive les en-têtes.
        """
        Verificateur(int, 0, len(self._tableau)-1).controle_total(index_ligne)#vérifie que ligne est valide
        if index_ligne == 0 :
            self._en_tetes_h = False
        else :
            del self._tableau[index_ligne]

    @controle_arguments(VAappend_ligne)
    def append_ligne(self, nb_lignes=1) :
        """Rajoute des lignes vides en bas du tableau.
        
        Les cases des nouvelles lignes ont pour valeur None.
        Nb_lignes définit le nombre de lignes à ajouter.
        """
        for i in range(nb_lignes) :
            self._tableau.append([None]*len(self._tableau[0]))#* sert à répéter None dans la liste autant de fois que l'on souhaite

    @controle_arguments(VAinsert_ligne, conversion=True)
    def insert_ligne(self, position, nb_lignes=1) :
        """Rajoute des lignes vides à une position du tableau.
        
        Les cases des nouvelles lignes ont pour valeur None.
        Position détermine où insérer les nouvelles lignes. Nb_lignes définit le nombre de lignes à ajouter.
        """
        for i in range(nb_lignes) :
            nouvelle_ligne = []
            for index_colonne_int in range(len(self._tableau[0])) :
                nouvelle_ligne.append(None)
            self._tableau.insert(position, nouvelle_ligne)

    @controle_arguments(VAget_colonne)
    def get_colonne(self, index_colonne) :
        """Retourne la liste des éléments contenus dans la colonne.
        
        Si en_tetes_h vaux True, le premier élément est l'en-tête de la colonne.Vient ensuite les éléments de la colonne. L'ordre des éléments est conservé."""
        index_colonne_int = self._index_colonne_int(index_colonne)#conversion id colonne en chiffre
        if index_colonne == "@" and not self._en_tetes_v :
            raise IndexError("Impossible d'afficher les en-têtes verticaux car ils sont désactivés (self.en_tetes_v = False).")
        colonne = []
        for i, ligne in enumerate(self._tableau) :
            if i == 0 and self._en_tetes_h and index_colonne != "@" :
                colonne.append(ligne[index_colonne_int])
            if i != 0 :
                colonne.append(ligne[index_colonne_int])
        return colonne

    @controle_arguments(VAset_colonne)
    def set_colonne(self, index_colonne, nouvelle_valeur) :
        """Modifie la colonne correspondant à l'index fourni.
        
        La colonne a pour valeur nouvelle_valeur, qui doit être une liste avec la même nombre d'éléments que les autres colonnes (si les en-têtes de colonne sont activés, il faut préciser l'en-tête). Si la colonne est celle des en-têtes verticaux, il faut qu'il y ait autant d'élèment que de ligne (on ne précise pas le nom du tableau).
        """
        index_colonne_int = self._index_colonne_int(index_colonne)#conversion id colonne en chiffre
        longueur_liste = len(self._tableau)#le nombre de lignes ; la liste doit avoir autant d'éléments que ce nombre.
        if index_colonne_int == 0 :
            if not self._en_tetes_v :
                raise IndexError("Les en-têtes verticaux ne sont pas activés donc il n'est pas possible de les modifier.")
            nouvelle_valeur.insert(0, self._tableau[0][0])
        elif not self._en_tetes_h :#s'il n'y a pas d'en-têtes, l'utilisateur ne saisi pas de case pour les en-têtes 
            nouvelle_valeur.insert(0, self._tableau[0][index_colonne_int])#mais on en rajoute une en conservant la valeur de l'en-tête d'origine
        VLliste = VerificateurListes(minimum=longueur_liste, maximum=longueur_liste)#Vérification de la longueur et du type de la liste
        nouvelle_valeur = VLliste.controle_total(nouvelle_valeur)
        
        for index_ligne, valeur_case in enumerate(nouvelle_valeur) :
            self._tableau[index_ligne][index_colonne_int] = valeur_case

    @controle_arguments(VAget_colonne)
    def del_colonne(self, index_colonne) :
        """Supprime la colonne correspondant à l'index donné.
        
        La colonne est supprimée, c'est à dire que sa place dans le tableau est enlevée et les colonnes à sa droite sont décalés. Les dimensions du tableau changent. Si on tente de supprimer la colonne des en-têtes avec l'index "@", on désactive les en-têtes.
        """
        if index_colonne == "@" :
            self._en_tetes_v = False#on enlève les en-têtes
        else :
            index_colonne_int = self._index_colonne_int(index_colonne)#conversion id colonne en chiffre
            for index_ligne in range(len(self._tableau)) :
                del self._tableau[index_ligne][index_colonne_int]

    @controle_arguments(VAappend_colonne)
    def append_colonne(self, nb_colonnes=1) :
        """Rajoute des colonnes vides à droite du tableau.
        
        Les cases des nouvelles colonnes ont pour valeur None.
        Nb_colonnes définit le nombre de colonnes à ajouter.
        """
        for i in range(nb_colonnes) :
            for index_ligne in range(len(self._tableau)) :
                self._tableau[index_ligne].append(None)
    
    @controle_arguments(VAinsert_colonne)
    def insert_colonne(self, position, nb_colonnes=1) :
        """Rajoute des colonnes vides à une position du tableau.
        
        Les cases des nouvelles colonnes ont pour valeur None.
        Position détermine où insérer les nouvelles colonnes. Nb_colonnes définit le nombre de colonnes à ajouter.
        """
        index_colonne_int = self._index_colonne_int(position)
        for i in range(nb_colonnes) :
            for index_ligne in range(len(self._tableau)) :
                self._tableau[index_ligne].insert(index_colonne_int, None)

    @controle_arguments(VAget_case)
    def get_case(self, index) :
        """Retourne ce qui est contenu dans une case.
        
        Si la case n'est pas une case d'en-tête ou de nom du tableau, on modifie la case. sinon on appelle la méthode spécialisée.
        """
        index_colonne_int, index_ligne = self._index_case_int(index)
        if index[0] == 0 and index[1] == 0 :
            return self.get_nom_tableau()
        elif index[0] == 0 :
            return self.get_nom_ligne(index[1])
        elif index[1] == 0 :
            return self.get_nom_colonne(self._index_colonne_str(index[0]))
        else :
            return self._tableau[index_ligne][index_colonne_int]

    @controle_arguments(VAset_case)
    def set_case(self, index, nouvelle_valeur) :
        """Modifie la case correspondant à l'index avec la nouvelle valeur.
        
        Si la case n'est pas une case d'en-tête ou de nom du tableau, on modifie la case. sinon on appelle la méthode spécialisée.
        """
        index_colonne_int, index_ligne = self._index_case_int(index)
        if index[0] == 0 and index[1] == 0 :
            self.set_nom_tableau(nouvelle_valeur)
        elif index[0] == 0 :
            self.set_nom_ligne(index[1], nouvelle_valeur)
        elif index[1] == 0 :
            self.set_nom_colonne(self._index_colonne_str(index[0]), nouvelle_valeur)
        else :
            self._tableau[index_ligne][index_colonne_int] = nouvelle_valeur

    @controle_arguments(VAget_case)
    def del_case(self, index) :
        """Supprime le contenu de la case correspondant à l'index.
        
        Si la case n'est pas une case d'en-tête ou de nom du tableau, la valeur de la case vaut alors None. Sinon, on appelle la méthode spécialisée.
        """
        index_colonne_int, index_ligne = self._index_case_int(index)
        if index[0] == 0 and index[1] == 0 :
            self.del_nom_tableau()
        elif index[0] == 0 :
            self.del_nom_ligne(index[1])
        elif index[1] == 0 :
            self.del_nom_colonne(self._index_colonne_str(index[0]))
        else :
            self._tableau[index_ligne][index_colonne_int] = None

    @controle_arguments(VAget_nom_ligne, conversion=True)
    def get_nom_ligne(self, index_ligne) :
        """Retourne le nom de la ligne (son en-tête).
        
        Si en_tetes_v est faux, lève une erreur.
        """
        if index_ligne == 0 :
            raise IndexError("Cette méthode ne peut pas retourner le nom du tableau (d'index @0). Utiliser la méthode get_nom_tableau.")
        elif self._en_tetes_v :
            return self._tableau[index_ligne][0]
        else :
            raise IndexError("Ce tableau n'a pas d'en-têtes de ligne car self.en_tetes_v == False. Les lignes n'ont pas de nom.")

    @controle_arguments(VAset_nom_ligne, conversion=True)
    def set_nom_ligne(self, index_ligne, nouveau_nom) :
        """Modifie l'en-tête de la ligne (son nom).
        
        Si en_tetes_v est faux, lève une erreur.
        """
        if index_ligne == 0 :
            raise IndexError("Cette méthode ne peut pas modifier le nom du tableau (d'index @0). Utiliser la méthode set_nom_tableau.")
        elif self._en_tetes_v :
            self._tableau[index_ligne][0] = nouveau_nom
        else :
            raise IndexError("Ce tableau n'a pas d'en-têtes de ligne car self.en_tetes_v == False. Les lignes n'ont pas de nom.")

    @controle_arguments(VAget_nom_ligne)
    def del_nom_ligne(self, index_ligne) :
        """Supprimme le nom de la ligne.
        
        Si en_tetes_v est faux, lève une erreur. Sinon, le nom de la ligne (son en-tête) vaut alors None.
        """
        if index_ligne == 0 :
            raise IndexError("Cette méthode ne peut pas supprimer le nom du tableau (d'index @0). Utiliser la méthode del_nom_tableau.")
        elif self._en_tetes_v :
            self._tableau[index_ligne][0] = None
        else :
            raise IndexError("Ce tableau n'a pas d'en-têtes de ligne car self.en_tetes_v == False. Les lignes n'ont pas de nom.")

    @controle_arguments(VAget_nom_colonne)
    def get_nom_colonne(self, index_colonne) :
        """Retourne le nom de la colonne (son en-tête).
        
        Si en_tetes_h est faux, lève une erreur.
        """
        if index_colonne == "@" :
            raise IndexError("Cette méthode ne peut pas retourner le nom du tableau (d'index @0). Utiliser la méthode get_nom_tableau.")
        elif self._en_tetes_h :
            index_colonne_int = self._index_colonne_int(index_colonne)#conversion id colonne en chiffre
            return self._tableau[0][index_colonne_int]
        else :
            raise IndexError("Ce tableau n'a pas d'en-têtes de colonne car self.en_tetes_h == False. Les colonnes n'ont pas de nom.")

    @controle_arguments(VAset_nom_colonne)
    def set_nom_colonne(self, index_colonne, nouveau_nom) :
        """Modifie le nom de la colonne (son en-tête).
        
        Si en_tetes_h est faux, lève une erreur.
        """
        if index_colonne == "@" :
            raise IndexError("Cette méthode ne peut pas modifier le nom du tableau (d'index @0). Utiliser la méthode set_nom_tableau.")
        elif self._en_tetes_h :
            index_colonne_int = self._index_colonne_int(index_colonne)#conversion id colonne en chiffre
            self._tableau[0][index_colonne_int] = nouveau_nom
        else :
            raise IndexError("Ce tableau n'a pas d'en-têtes de colonne car self.en_tetes_h == False. Les colonnes n'ont pas de nom.")

    @controle_arguments(VAget_nom_colonne)
    def del_nom_colonne(self, index_colonne) :
        """Supprime le nom de la colonne (son en-tête).
        
        Si en_tetes_h est faux, lève une erreur. Sinon, le nom de la colonne vaut None.
        """
        if index_colonne == "@" :
            raise IndexError("Cette méthode ne peut pas supprimer le nom du tableau (d'index @0). Utiliser la méthode del_nom_tableau.")
        elif self._en_tetes_h :
            index_colonne_int = self._index_colonne_int(index_colonne)#conversion id colonne en chiffre
            self._tableau[0][index_colonne_int] = None
        else :
            raise IndexError("Ce tableau n'a pas d'en-têtes de colonne car self.en_tetes_h == False. Les colonnes n'ont pas de nom.")

    #Méthode générales et de tri

    def clear(self) :
        """Supprime tout le contenu du tableau."""
        for i in range(len(self._tableau)) :
            for j in range(len(self._tableau[0])) :
                self._tableau[i][j] = None

    @controle_arguments(VAreverse, conversion=True)#ajouter verificateur
    def reverse(self, index="A") :
        """Inverse l'ordre des valeurs des lignes ou des colonnes.
        
        Inverse soit l'ordre des valeurs de chaque colonne (et pour cela préciser un index de colonne) soit inverse l'ordre des valeurs de chaque ligne (et pour cela préciser un index de ligne).
        """
        if re_index_ligne.search(index) :
            for i in range(len(self._tableau)) :
                inverse = reversed(self._tableau[i][1:])#on inverse les valeurs des lignes
                inverse = list(inverse)#on convertit en liste
                self._tableau[i] = [self._tableau[i][0]] + inverse
        elif re_index_colonne.search(index) :
            inverse = reversed(self._tableau[1:])
            inverse = list(inverse)
            self._tableau= [self._tableau[0]] + inverse

    def renversement_tableau(self) :
        """Méthode tranformant les lignes en colonnes et vice-versa
        
        Attention ! Ne pas utiliser cette méthode à la légère : cette méthode transforme le tableau.
        Les lignes deviennent des colonnes et les colonnes deviennent des lignes. En_tetes_h devient en_tetes_v et vice-versa.
        """
        nouveau_tableau = []
        for j in range(len(self._tableau[0])) :#on parcours chaque colonne
            #on transforme une colonne en ligne
            ligne = []
            for i in range(len(self._tableau)) :
                ligne.append(self._tableau[i][j])#on prend la valeur actuelle de [i][j] pour la mettre à la future place [j][i]
            nouveau_tableau.append(ligne)

        self._tableau = nouveau_tableau
        self._en_tetes_h, self._en_tetes_v = self._en_tetes_v, self._en_tetes_h

    @controle_arguments(VAsort, conversion=True)
    def sort(self, index="A", key=None, reverse=False) :
        """Tri les valeurs du tableau en fonction d'une ligne/colonne.
        
        Index doit être l'index de la ligne ou de la clolonne selon laquelle on trie. Key doit être une fonction et reversed un booléen.
        """
        index_colonne = index
        if re_index_ligne.search(index) :#si on trie selon une ligne
            self.renversement_tableau()#on renverse le tableau pour trier selon une colonne (c'est plus simple)
            index_colonne = self._index_colonne_str(index)#on convertit l'index de la ligne en index de colonne
        
        tableau_trié = sorted(self._tableau, key=lambda ligne :self._clé_colonne(ligne, index_colonne=index_colonne, key=key))#on tri selon la colonne précisée
        tableau_trié = list(tableau_trié)
        self._tableau = tableau_trié
        if re_index_ligne.search(index) :#si au départ on tri par ligne
            self.renversement_tableau()#on re renverse le tableau
        if reverse :
            self.reverse(index)#on inverse l'ordre du tableau si besoin

    #Méthodes d'enregistrement, d'importation et d'exportation

    @controle_arguments(VAimport_csv)
    def import_csv(self, fichier_csv) :
        """Importe les données d'un fichier csv pour former un tableau.
        
        Cette méthode supprime tout ce qui était contenu auparanvant dans le tableau.
        Si les en-têtes sont activés, la première ligne/colonne du tableau contenue dans le fichier csv est considéré comme ligne/colonne d'en-têtes.
        """
        with open(fichier_csv, newline='') as fichier :#ouverture du fichier
            dialect = csv.Sniffer().sniff(fichier.read(1024))#détection du dialect utilisé pour encoder le fichier csv
            fichier.seek(0)
            lecteur_csv = csv.reader(fichier, dialect)#lecture du fichier
        
            _tableau = []#on crée un tableau
            for ligne in lecteur_csv :
                _tableau.append(ligne)
        
        if not self._en_tetes_v :#si on a désactivé les en-têtes
            for i in range(len(_tableau)) :
                _tableau[i].insert(0, None)#on rajoute des cases vides pour les en-têtes (qui ne seront pas visibles)
        if not self._en_tetes_h :
            _tableau.insert(0, [])
            for j in range(len(_tableau[1])) :
                _tableau[0].append(None)#idem

        _tableau = VTtableau.controle_total(_tableau)#controle si toutes les lignes ont bien la même longueur
        self._tableau = _tableau
        #conversion des chaine qui sont en fait des nombres
        self._conversion_nombres()

    @controle_arguments(VAexport_csv)
    def export_csv(self, fichier_csv, dialect='excel') :
        """Exporte le tableau dans un fichier .csv.
        
        On enregistre le tableau dans un fichier csv. Si les en-têtes sont activées, on les enregistre aussi.
        Le paramètre dialect permet de configurer le mode d'écriture du fichier csv. Il est passé en argument de csv.writer(). Voir la documentation de cette fonction.
        """
        with open(fichier_csv, "w", newline='') as fichier :
	        transcripteur = csv.writer(fichier, dialect)
	        transcripteur.writerows(self.tableau)

    #Méthodes ne modifiant pas le tableau :
    # Méthode parcourant le tableau, recherchant des éléments, ou pour l'affichage

    def lignes(self) :
        """Méthode parcourant toutes les lignes du tableau.
        
        Ne retourne jamais la ligne des en-têtes horizontaux.
        """
        return list(self.tableau[1:])#on ne retourne pas la ligne d'en-têtes horizontaux : on enlève la ligne 0
    
    def colonnes(self) :
        """Méthode parcourant toutes les colonnes du tableau.
        
        Ne retourne jamais la colonne des en-têtes verticaux.
        """
        colonnes = []
        for index_colonne_int in range(1, self.dimensions[0]+1) :#1 car on ne prend pas la colonne des en-têtes et +1 car on s'arrête à la borne inférieure
            index_colonne = self._index_colonne_str(index_colonne_int)
            colonnes.append(self[index_colonne])
        return list(colonnes)

    @controle_arguments(VAaffichage)
    def affichage(self, largeur_colonne=15, sep="|", print=True) :
        """Méthode qui permet d'afficher le tableau.
        
        On peut définir la largeur des colonnes, en nombre d'espaces, grâce au paramètre largeur_colonne. On peut aussi définir le séparateurs de colonnes grâce à sep. Si on préfère retourner une chaine qui représente le tableau pour l'affichage, on met print à False.
        """
        chaine = """"""
        if self._en_tetes_h :
            chaine += self._str_ligne(0, largeur_colonne=largeur_colonne, sep=sep)
        chaine += "\n"
        for i in range(1, len(self._tableau)) :
            chaine += self._str_ligne(i, largeur_colonne=largeur_colonne, sep=sep)
            chaine += "\n"
        if print :
            print(chaine)
        else :
            return chaine

    def index(self, valeur) :
        """Renvoie l'index de la première case où a été trouvée la valeur.
        
        Si la valeur n'est pas trouvée dans le tableau, on retourne False.
        """
        if valeur == self.nom_tableau :#si c'est le nom du tableau, pas besoin de tout parcourir/ le nom du tableau est accessible même si les en-têtes sont désactivés
            return "@0"
        for index_ligne, ligne in enumerate(self._tableau) :
            if index_ligne !=0 or (index_ligne == 0 and self._en_tetes_h) :#on parcours pas si c'est la ligne d'en-tête et qu'elle est désactivée
                for index_colonne_int, case in enumerate(ligne) :
                    if case == valeur and (index_colonne_int != 0 or (index_colonne_int == 0 and self._en_tetes_v)) :#si on a trouvé la valeur et que la valeur est accessible (vérif que c'est pas un en-tete desactivé)
                        index_colonne = self._index_colonne_str(index_colonne_int)
                        return index_colonne + str(index_ligne)
        raise ValueError("La valeur n'est pas présente dans le tableau.")#si on n'a pas trouvé la valeur, on lève une erreur

    #Méthode internes
    #Ne pas utiliser ces méthodes en dehors de cette classe

    @controle_arguments(VA_str_ligne)
    def _str_ligne(self, index_ligne, largeur_colonne=15, sep="|") :
        """Affiche la ligne demandée.
        
        Le paramètre ligne doit être le numéro correspondant à la ligne. Le paramètre largeur_colonne est le nombre d'espaces qui définissent la largeur des colonnes.
        """
        Verificateur(int, 0, len(self._tableau)-1).controle_total(index_ligne)#vérifie que index_ligne est valide
        chaine = """"""
        if index_ligne == 0 and not self._en_tetes_h :
            raise IndexError("Les en-têtes horizontales sont désactivées donc il est impossible de les afficher.")
        for i in range(len(self._tableau[index_ligne])) :
            if i==0 and self._en_tetes_v : #si c'est la première case d'une ligne est que les en-têtes verticales sont activées
                chaine += self._str_case(index_ligne, 0, largeur_colonne)
                chaine+= sep
            elif i!=0 :#si c'est une case normale
                chaine += self._str_case(index_ligne,i, largeur_colonne)
                chaine+= sep
        return chaine

    @controle_arguments(VA_str_case)
    def _str_case(self, index_ligne, index_colonne_int, largeur_colonne=15) :
        """Retourne une chaine de caractère représantant la case.
        
        Le paramètre largeur_colonne est le nombre d'espaces qui définissent la largeur des colonnes. La chaine renvoyée correspond à la largeur de la colonne. Si la largeur de colonne ne suffit pas à afficher tout le contenu de la case, la chaine est tronquée.
        """
        Verificateur(int, 0, len(self._tableau)-1).controle_total(index_ligne)#vérifie que index_ligne est valide
        contenu_case = self._tableau[index_ligne][index_colonne_int]
        if contenu_case is not None :
            str_case = str(contenu_case)#on va afficher le contenu de la case
        else :
            str_case = ""#on ne va pas afficher None mais des espaces
        largeur_max = largeur_colonne-int(largeur_colonne/10)#largeur maximal car tous les caractères ne sont pas aussi étrois qu'un espace 
        largeur_max -=1#pour laissez la place du caractère () indiquant que le contenu n'est pas affiché complètement
        if len(str_case) > largeur_max :
            str_case = str_case[0:largeur_max]
            str_case += "»"
        return str_case.center(largeur_colonne)

    @controle_arguments(VA_index_colonne_int)
    def _index_colonne_int(self, index_colonne) :
        """Convertit l'identifiant de la colonne en entier.
        
        Convertit l'identifiant d'une colonne, composé d'une ou plusieurs majuscule, en nombre entier. Ce nombre entier est un index correspondant à la position de la colonne dans le tableau.
        """
        index_colonne = index_colonne[::-1]#inverse l'ordre des lettres
        index_colonne_int = 0
        for i, lettre in enumerate(index_colonne) :
            valeur_lettre = ord(lettre)#on prend la valeur décimale de la lettre grâce aux tableau de correspondance de l'ASCII : A=65, B=66 
            valeur_lettre-=64#On enlève 64 : A=1, B=2
            index_colonne_int+= valeur_lettre * 26**i#on prend en compte la position de la lettre (multiplication par sa puissance)
        return index_colonne_int

    @controle_arguments(VA_index_colonne_str, conversion=True)
    def _index_colonne_str(self, index_colonne_int) :
        """Convertit l'index de la colonne (int) en string.
        
        Convertit un nombre entier en identifiant d'une colonne, composé d'une ou plusieurs majuscules. Ce nombre entier est un index correspondant à la position de la colonne dans le tableau.
        """
        if index_colonne_int == 0 :
            index_colonne = "@"#indique que l'on a affaire à un en tête vertical
        else :
            #on cherche la plus petite puissance supérieure à l'index fourni
            puissance = 1
            while index_colonne_int > pow(26, puissance) :
                puissance +=1
            liste_valeurs_lettres = []
            #on convertit index_colonne_int en base 26 (stocké chiffre par chiffre  dans une liste)
            while index_colonne_int != 0 :
                i = 26
                if index_colonne_int >= pow(26, puissance) :
                    while index_colonne_int < i*pow(26, puissance) :
                        i -= 1
                    index_colonne_int -= i*pow(26, puissance)
                    liste_valeurs_lettres.append(i)
                puissance -= 1
            #on convertit le nombre en base 26 en lettre
            index_colonne = ""
            for i, valeur_lettre in enumerate(liste_valeurs_lettres) :
                lettre = chr(valeur_lettre+64)#On ajoute 64 pour avoir une lettre dont la valeur ASCII corresponde à valeur_lettre+64 (car A=65 en  ASCII et pas A=1)
                index_colonne += lettre
        return index_colonne

    @controle_arguments(VA_index_case_int)
    def _index_case_int(self, index) :
        """Retourne les index (int) de ligne et colonne d'une case."""
        index_ligne_str = re_index_partie_ligne.search(index)[0]#on prend juste les chiffres
        index_ligne = int(index_ligne_str)
        index_colonne = re_index_partie_colonne.search(index)[0]#on prend juste les lettres
        index_colonne_int = self._index_colonne_int(index_colonne)
        return index_colonne_int, index_ligne
    
    def _conversion_nombres(self) :
        """Convertit les chaines str représentant des nombres en int ou float.
        
        Cette méthode tente de convertir les chaines str contenues dans les cases (et en-têtes) du tableau. Si la chine représente un nombre on la convertit en float. Et si ce nombre n'a pas de partie décimale, on le reconvertit en int.
        """
        for i in range(len(self._tableau)) :
            for j, contenu in enumerate(self._tableau[i]) :
                if isinstance(contenu, str) :
                    try :
                        self._tableau[i][j] = float(contenu)
                    except (TypeError, ValueError) :
                        pass#on ne peut convertir la chaine en nombre donc on laisse la chaine en nombre
                    else :#si il n'y a pas d'erreurs
                        if math.floor(self._tableau[i][j]) == self._tableau[i][j] :#s'il n'y a pas de partie décimale
                            self._tableau[i][j] = int(self._tableau[i][j])#on converti en entier

    @controle_arguments(VA_clé_ligne, conversion=True)
    def _clé_ligne(self, ligne, index_ligne=1, key=None) :
        """Fonction qui permet de trier une ligne.
            
        ligne indique la ligne qui est triée
        index_ligne indique la ligne à trier. Key indique comment trier les objets contenus dans la ligne.
        Attention cette méthode n'est pas testée ! Elle ne devrait pas être utilisée.
        """
        raise UserWarning("Attention cette méthode n'est pas testée ! Elle ne devrait pas être utilisée.")
        data = ligne[index_ligne]#on prend les valeur de la ligne selon laquelle on trie
        if data == self._tableau[index_ligne][0] :
            data = min(self[index_ligne][1:], key=key)#on cherche la plus petite valeur de la ligne (hormi l'en-tete) pour que l'en-tete reste en premier (tri stable)
            print(data)
        if key :
            data = key(data)
        return data

    @controle_arguments(VA_clé_colonne, conversion=True)
    def _clé_colonne(self, ligne, index_colonne="A", key=None) :
        """Fonction qui permet de trier une colonne.
            
        ligne indique la ligne qui est triée
        index_ligne indique la ligne à trier. Key indique comment trier les objets contenus dans la ligne.
        """
        index_colonne_int = self._index_colonne_int(index_colonne)
        data = ligne[index_colonne_int]#on prend les valeurs de la colonne selon laquelle on trie
        if data == self._tableau[0][index_colonne_int] :
            data = min(self[index_colonne][1:], key=key)#on cherche la plus petite valeur de la colonne (hormi l'en-tete) pour que l'en-tete reste en premier (tri stable)
        if key :
            data = key(data)
        return data
    
    def _add(self, tableau_ajout, tableau_retour=None) :
        """Renvoie un tableau avec les données de self et de tableau_ajout.

        Les données de self et de tableau_ajout sont intégrées dans un tableau qui est renvoyé. Si tableau_retour n'est pas précisé on en retourne un nouveau.
        Tableau_ajout doit être un objet Tableau ou un objet correspondant à une structure de tableau (liste comprenant des sous-listes).
        """
        if isinstance(tableau_ajout, list) :#structure de tableau mais pas un objet Tableau
            VTtableau.controle_total(tableau_ajout)
            tableau_ajout = Tableau(tableau=tableau_ajout, en_tetes_h=True, en_tetes_v=True)#conversion en tableau
        Verificateur(Tableau).controle_total(tableau_ajout)
        if tableau_retour is None :
            tableau_retour = copy.deepcopy(self)#on copie le tableau
        anciennes_dimensions = self.dimensions

        #copie des en-têtes et mise au dimensions
        if self.en_tetes_h and tableau_ajout.en_tetes_h :
            for en_tete in tableau_ajout[0] :
                nouvel_en_tete = True
                for en_tete_existant in self[0] :
                    if not en_tete:
                        break
                    elif en_tete == en_tete_existant :
                        nouvel_en_tete = False
                        break
                if nouvel_en_tete :
                    tableau_retour.append_colonne()
                    tableau_retour._tableau[0][tableau_retour.dimensions[0]] = en_tete#ajout de l'en-tête
        else :
            tableau_retour.append_colonne(tableau_ajout.dimensions[0])
        
        if self.en_tetes_v and tableau_ajout.en_tetes_v :
            for en_tete in tableau_ajout["@"] :
                nouvel_en_tete = True
                for en_tete_existant in self["@"] :
                    if not en_tete :
                        break
                    elif en_tete== en_tete_existant :
                        nouvel_en_tete = False
                        break
                if nouvel_en_tete :
                    tableau_retour.append_ligne()
                    tableau_retour[tableau_retour.dimensions[1]+1][0] = en_tete#ajout de l'en-tête
        else :
            tableau_retour.append_ligne(tableau_ajout.dimensions[1])

        for index_ligne in range(1, tableau_ajout.dimensions[1]+1) :#1 car on ne parcours pas les en têtes et +1 car on s'arrête à la borne inférieure
            for index_colonne_int in range(1, tableau_ajout.dimensions[0]+1) :
                index_c = anciennes_dimensions[0] + index_colonne_int#valeur par défaut
                if self.en_tetes_h and tableau_ajout.en_tetes_h :
                    en_tete_c = tableau_ajout._tableau[0][index_colonne_int]
                    if en_tete_c :
                        index_en_tete_c = tableau_retour.index(en_tete_c)
                        index_c = re_index_partie_colonne.search(index_en_tete_c)[0]

                index_l = anciennes_dimensions[1] + index_ligne
                if self.en_tetes_v and tableau_ajout.en_tetes_v :
                    en_tete_l = tableau_ajout["@"+str(index_ligne)]
                    if en_tete_l :
                        index_en_tete_l = tableau_retour.index(en_tete_l)
                        index_l = re_index_partie_ligne.search(index_en_tete_l)[0]

                nouvel_index = index_c+str(index_l)
                ancienne_valeur = tableau_retour[nouvel_index]
                if ancienne_valeur is None :
                    tableau_retour[nouvel_index] = tableau_ajout._tableau[index_ligne][index_colonne_int]
                elif ancienne_valeur != tableau_ajout._tableau[index_ligne][index_colonne_int] :
                    raise Warning("Écrasement de données.\nCertaines données du tableau à ajouter n'ont pas pu être mise dans le nouveau tableau. Ces valeurs ont le même en-tête de ligne et le même en-tête de colonne qu'une autre valeur dans le premier tableau.")
        return tableau_retour


    tableau = property(get_tableau)
    en_tetes_h = property(get_en_tetes_h, set_en_tetes_h)
    en_tetes_v = property(get_en_tetes_v, set_en_tetes_v)
    
    #attribut factices présents pour faciliter l'utilisation des tableaux
    nom_tableau = property(get_nom_tableau, set_nom_tableau, del_nom_tableau, "Attribut représantant le nom du tableau.")
    dimensions = property(get_dimensions, set_dimensions, del_dimensions, "Représente les dimensions du tableau sous forme de tuple : (nb_colonnes, nb_lignes). Les en-têtes ne sont pas comptées dans les")