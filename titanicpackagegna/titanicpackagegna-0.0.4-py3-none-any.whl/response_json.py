class Response_json:
    def __init__(self):
        self.f_v = 0
        self.f_m = 0
        self.h_v = 0
        self.h_m = 0
        self.pclass1_v = 0
        self.pclass1_m = 0
        self.pclass2_v = 0
        self.pclass2_m = 0
        self.pclass3_v = 0
        self.pclass3_m = 0
        self.child_v = 0
        self.child_m = 0
        self.adult_v = 0
        self.adult_m = 0
        self.old_v = 0
        self.old_m = 0


    
    # features[1] = 1 (male) / = 0 (female) 
    # target[0] = 1 (survived) / = 0 (dead)
    def sex_survived(self, X, y):
        for features, target in zip(X.values, y.values):
            if int(features[1]) == 0 and target[0] == 1:
                self.f_v += 1
            elif int(features[1]) == 0 and target[0] == 0:
                self.f_m += 1
            elif int(features[1]) == 1 and target[0] == 1:
                self.h_v += 1
            elif int(features[1]) == 1 and target[0] == 0:
                self.h_m += 1
        return [{"name":"Nombre de femmes ayant survécu","pourcent":self.f_v},{"name":"Nombre de femmes n'ayant pas survécu", "pourcent":self.f_m},
                {"name":"Nombre d'hommes ayant survécu", "pourcent":self.h_v},{"name":"Nombre d'hommes n'ayant pas survécu", "pourcent":self.h_m}]       


    def pclass_survived(self, X, y):
        for features, target in zip(X.values, y.values):
            if int(features[0]) == 1 and target[0] == 1:
                self.pclass1_v += 1
            elif int(features[0]) == 1 and target[0] == 0:
                self.pclass1_m += 1
            elif int(features[0]) == 2 and target[0] == 1:
                self.pclass2_v += 1
            elif int(features[0]) == 2 and target[0] == 0:
                self.pclass2_m += 1
            elif int(features[0]) == 3 and target[0] == 1:
                self.pclass3_v += 1
            elif int(features[0]) == 3 and target[0] == 0:
                self.pclass3_m += 1
        return [{"name": "Nombre de survivants ayant un ticket en 1ère classe","pourcent": self.pclass1_v},
                {"name":"Nombre de morts ayant un ticket en 1ère classe","pourcent":self.pclass1_m},
                {"name":"Nombre de survivants ayant un ticket en 2ème classe","pourcent":self.pclass2_v},
                {"name":"Nombre de morts ayant un ticket en 2ème classe","pourcent":self.pclass2_m},
                {"name":"Nombre de survivants ayant un ticket en 3ème classe","pourcent":self.pclass3_v},
                {"name":"Nombre de morts ayant un ticket en 3ème classe","pourcent":self.pclass3_m}]


    def age_survived(self, X, y):
        for age, target in zip(X.values, y.values):
            if int(age[2]) >= 0 and int(age[2]) <= 18 and target[0] == 1:
                self.child_v += 1
            elif int(age[2]) >= 0 and int(age[2]) <= 18 and target[0] == 0:
                self.child_m += 1
            elif int(age[2]) > 18 and int(age[2]) <= 50 and target[0] == 1:
                self.adult_v += 1
            elif int(age[2]) > 18 and int(age[2]) <= 50 and target[0] == 0:
                self.adult_m += 1
            elif int(age[2]) > 50 and target[0] == 0:
                self.old_v += 1
            elif  int(age[2]) > 50 and target[0] == 1:
                self.old_m += 1
        return [{"name": "Nombre d'enfants ayant survécu'","pourcent": self.child_v},
                {"name":"Nombre d'enfants n'ayant pas survécu","pourcent":self.child_m},
                {"name":"Nombre d'adultes ayant survécu","pourcent":self.adult_v},
                {"name":"Nombre d'adultes n'ayant pas survécu","pourcent":self.adult_m},
                {"name":"Nombre de personnes âgées ayant survécu","pourcent":self.old_v},
                {"name":"Nombre de personnes âgées n'ayant pas survécu","pourcent":self.old_m}]
