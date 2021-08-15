"""Ce fichier contient la classe DictionnaireOrdonné."""

class DictionnaireOrdonné :
    """Cette classe fonctionne comme un dictionnaire sauf qu'elle est ordonnée.
    
    Définit un dictionnaire ordonné : l'ordre des clés est important. Deux dictionnaire égaux à l'ordre près ne forment pas deux dictionnaires ordonnés égaux. En conséquence, on peut trier les dictionnaires ordonnés... 
    """

    def __init__(self,base = {},**données) :
        """Constructeur du dictionnaire ordonné.
        
        Il peut ne prendre aucun paramètre (dans ce cas, le dictionnaire sera vide). On peut aussi construire un dictionnaire remplis grâce :
        -   au dictionnaire 'base' passé en premier paramètre ;
        -   aux valeurs que l'on retrouve dans "donnees".
        """
        
        self._clés = []
        self._valeurs = []

        
        if type(base) not in (dict,DictionnaireOrdonné) :
            raise TypeError("""\
Le type de l'objet à convertir en dictionnaire ordonné doit être un dictionnaire (usuel ou ordonné).""")
        
        for clé,valeur in base.items() :
            self[clé] = base[clé]
            
        for clé,valeur in données.items() :
            self[clé] = données[clé]

    def __repr__(self) :
        """Méthode spéciale appelé quand on cherche à représenter l'objet.
        
        Représentation de l'objet. C'est cette chaîne qui sera affichée quand on saisit directement le dictionnaire dans l'interpréteur, ou en utilisant la fonction 'repr'. Utile pour le débuggage.
        """

        chaîne = """{"""
        for clé, valeur in self.items() :
            chaîne += repr(clé)
            chaîne +=  """: """
            chaîne += repr(valeur)
            chaîne += """, """
            
        if not chaîne[-1:] == """{""" :
            chaîne = chaîne[:-2]
        chaîne += """}"""
        return chaîne

    def __str__(self) :
        """Méthode appelée quand on souhaite afficher le dictionnaire.
        
        Méthode appellée par la fonction 'print' quand le dictionnaire est converti en chaîne grâce au constructeur 'str'. On redirige sur __repr__.
        """
        return repr(self)

    def __getitem__(self, clé) :
        """Retourne la valeur associé à la clé fournie en paramètre.
        
        Méthode spéciale appelé lorsque l'on saisi objet[clé]. Elle retourne la valeur correspondante à la clé.
        """
        if clé not in self._clés :
            raise KeyError(\
                """La clé {0} ne se trouve pas dans le dictionnaire.""".format(clé))
        else :
            indice = self._clés.index(clé)
            return self._valeurs[indice]

    def __setitem__(self,clé,valeur) :
        """permet de podifier la valeur associée à une clé.
        
        Méthode spéciale appelée quand on veut modifier une clé présente dans le dictionnaire. Si elle n'est pas présente, on l'ajoute à la fin du dictionnaire.
        """

        if clé in self._clés :
            indice = self._clés.index(clé)
            self._valeurs[indice] = valeur
        else :
            self._clés.append(clé)
            self._valeurs.append(valeur)

    def __delitem__(self,clé) :
        """Permet de supprimer une clé et sa valeur.
        
        Méthode spéciale appelé par Python lorsque l'on cherche à supprimer une clé (donc en même temps une valeur).
        """
        if clé not in self._clés :
            raise KeyError(\
                """La clé {0} ne se trouve pas dans le dictionnaire.""".format(clé))
        else :
            indice = self._clés.index(clé)
            del self._clés[indice]
            del self._valeurs[indice]

    def __len__(self) :
        """Retourne la longueur du dictionnaire ordonné.
        
        Méthode spéciale appelé quand on cherche à connaitre la longueur du dictionnaire ordonné (combien il y a de clé dans le dictionnaire).
        """
        return len(self._clés)

    def __contains__(self, clé) :
        """Retpurne True si la clé est trouvée dans le dictionnaire.
        
        Méthode spéciale appellée quand on cherche à savoir si une clé est présente dans le dictionnaire ordonné.
        """
        return clé in self._clés

    def __iter__(self) :
        """Méthode de parcourt de l'objet. On renvoie l'iterateur des clés."""
        return iter(self._clés)

    def __add__(self, dictionnaire_à_ajouter) :
        """Méthode qui ajoute un dictionnaire ordonné à un autre dictionnaire.
        
        Méthode spéciale appelée quand l'on veut ajouter deux dictionnaires entre eux. Permet de faire DictionnaireOrdonné + DictionnaireUsuel mais ne permet pas faire DictionnaireUsuel + DictionnaireOrdonné (voir méthode __radd__).
        """
        if type(dictionnaire_à_ajouter) not in (dict, DictionnaireOrdonné) :
            raise TypeError(\
                """Impossible de concaténer {0} et {1}.""".format(\
                    type(self),type(dictionnaire_à_ajouter)))
        else :
            nouveau = DictionnaireOrdonné()
            for clé,valeur in self.items() :
                nouveau[clé] = valeur
            for clé,valeur in dictionnaire_à_ajouter.items():
                nouveau[clé] = valeur
            return nouveau
        
    def __radd__(self, dictionnaire_à_ajouter) :
        """Méthode qui ajoute un dictionnaire à un dictionnaire ordonné.
        
        Méthode spéciale appelée lorsque l'on ajoute un dictionnaire à un dictionnaire ordonné. Elle renvoit l'addiction inverse : l'addition du dictionnaire ordonné avec le dictionnaire normal.
        """
        if type(dictionnaire_à_ajouter) not in (dict, DictionnaireOrdonné) :
            raise TypeError(\
                """Impossible de concaténer {0} et {1}.""".format(\
                    type(self),type(dictionnaire_à_ajouter)))
        else :
            return self + dictionnaire_à_ajouter

    def __eq__(self, dictionnaire_à_comparer) :
        """Retourne un booléen indiquant si les deux dictionnaires sont égaux.
        
        Méthode spéciale appelé lorsque l'on compare deux dictionnaire avec ==. Renvoie un booléen (True/False).
        """
        retour = False
        if isinstance(dictionnaire_à_comparer, DictionnaireOrdonné) :#si l'autre dictionnaire est un DO (évite de lever des exceptions à la prochaine instruction conditionnelle)
            if self._clés == dictionnaire_à_comparer._clés and self._valeurs == dictionnaire_à_comparer._valeurs :
                retour = True
        return retour
    
    def __ne__(self, dictionnaire_à_comparer) :
        """Retourne un booléen indiquant si deux dictionnaires sont différents.
        
        Méthode spéciale appelé lorsque l'on compare deux dictionnaire avec !=. La méthode appelle ensuite __eq__ renvoie l'inverse du booléen renvoyé par __eq__ .
        """
        return not self == dictionnaire_à_comparer
        
    def insert(self, index, clé, valeur) :
        """Insère un couple clé/valeur à l'index précisé.
        
        Si l'index est supérieur à len(self), une erreur est levée.
        """
        if index < len(self) :
            self._clés.insert(index, clé)
            self._valeurs.insert(index, valeur)
        elif index == len(self) :
            self.__setitem__(clé, valeur)
        else :
            raise IndexError("Index out of range.")

    def keys(self) :
        """Méthodesui parcourt les clés d'un dictionnaire ordonné.""" 
        return list(self._clés)
        
    def values(self) :
        """Méthode qui parcourt les valeurs d'un dictionnaire ordonné.""" 
        return list(self._valeurs)
    
    def items(self) :
        """Parcourt les clés et les valeurs d'un dictionnaire ordonné."""
        for i, clé in enumerate(self._clés) :
            valeur = self._valeurs[i]
            yield (clé,valeur)

    def sort(self, key = None, reverse=False) :
        """Méthode qui trie un DictionnaireOrdonné en fonction de ses clés."""
        clés_triées = sorted(self._clés, key = key, reverse = False)
        valeurs = []
        for clé in clés_triées :
            valeur = self[clé]
            valeurs.append(valeur)
        self._clés = clés_triées
        self._valeurs = valeurs
        
        if reverse == True :
            self.reverse()
        
    def reverse(self) :
        """ Cette méthode permet d'inverser le dictionnaire."""
        self._clés.reverse()
        self._valeurs.reverse()

