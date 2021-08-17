class Ratio:
    """Ratio Class, a class for conducting various functions seen in real life, that are related to Rational Numbers."""

    def __init__(self, antecedent, consequent):

        self.antecedent = antecedent
        self.consequent = consequent
        self.ratio = f"Antecedent:Consequent"

    def get(self):

        self.ratio = f"{self.antecedent}:{self.consequent}"

        return self.ratio

    def simplify(self):

        HCF = Factor(self.antecedent, self.consequent).HCF()

        simplified_ratio = (self.antecedent//HCF, self.consequent//HCF)

        self.ratio = f"{simplified_ratio[0]}:{simplified_ratio[1]}"

        return self.ratio

    def add(self, ratio):

        self.antecedent *= ratio.consequent
        ratio.antecedent *= self.consequent
        self.consequent, ratio.consequent = self.consequent * ratio.consequent, ratio.consequent * self.consequent

        self.antecedent += ratio.antecedent

        HCF = Factor(self.antecedent, self.consequent).HCF()

        self.antecedent //= HCF
        self.consequent //= HCF

        self.ratio = f"{self.antecedent}:{self.consequent}"

        answer = f"{self.ratio}"

        return answer

    def subtract(self, ratio):

        self.antecedent *= ratio.consequent
        ratio.antecedent *= self.consequent
        self.consequent, ratio.consequent = self.consequent * ratio.consequent, ratio.consequent * self.consequent

        if self.antecedent > ratio.antecedent:
            self.antecedent -= ratio.antecedent
            self.ratio = f"{self.antecedent}:{self.consequent}"
        if self.antecedent < ratio.antecedent:
            ratio.antecedent -= self.antecedent
            self.antecedent = ratio.antecedent
            self.ratio = f"{self.antecedent}:{self.consequent}"

        HCF = Factor(self.antecedent, self.consequent).HCF()

        self.antecedent //= HCF
        self.consequent //= HCF

        self.ratio = f"{self.antecedent}:{self.consequent}"

        answer = f"{self.ratio}"

        return answer

    def multiply(self, ratio):

        self.antecedent *= ratio.antecedent
        self.consequent *= ratio.consequent

        HCF = Factor(self.antecedent, self.consequent).HCF()

        self.antecedent //= HCF
        self.consequent //= HCF

        self.ratio = f"{self.antecedent}:{self.consequent}"

        answer = f"{self.ratio}"

        return answer

    def divide(self, ratio):

        self.antecedent *= ratio.consequent
        self.consequent *= ratio.antecedent

        HCF = Factor(self.antecedent, self.consequent).HCF()

        self.antecedent //= HCF
        self.consequent //= HCF

        self.ratio = f"{self.antecedent}:{self.consequent}"

        answer = f"{self.ratio}"

        return answer

class Factor:
    """Factor Class, a class for conducting various functions seen in real life, that are related to Factorization."""

    def __init__(self, *numbers):

        self.numbers = list(numbers)
        self.collective_factors = []
        self.collective_multiples = []

        for i in self.numbers:
            nominee_factors = list(range(1, i+1))
            factors = []
            for j in nominee_factors:
                if i % j == 0:
                    factors.append(j)

            self.collective_factors.append(factors)

        for i in self.numbers:
            multipliers = range(1, max(self.numbers)+1)
            multiples = []
            for j in multipliers:
                multiples.append(i*j)

            self.collective_multiples.append(multiples)

    def HCF(self):

        mixed_factors = []
        len_collective_factors = len(self.collective_factors)
        for i in self.collective_factors:
            for j in i:
                mixed_factors.append(j)
        mixed_factors.sort()
        HCF_nominees = []
        for i in mixed_factors:
            if mixed_factors.count(i) == len_collective_factors:
                HCF_nominees.append(i)
        HCF = max(HCF_nominees)

        return HCF

    def LCM(self):

        mixed_multiples = []
        len_collective_multiples = len(self.collective_multiples)

        for i in self.collective_multiples:
            for j in i:
                mixed_multiples.append(j)

        mixed_multiples.sort()
        LCM_nominees = []

        for i in mixed_multiples:
            if len_collective_multiples <= mixed_multiples.count(i) > 0:
                LCM_nominees.append(i)

        LCM = min(LCM_nominees)

        return LCM

class Fraction:

    def __init__(self, numerator, denominator, whole_num=None):

        self.numerator = numerator
        self.denominator = denominator
        self.whole_num = whole_num

        self.type = str()

        if self.whole_num != None:
            self.type = "Mixed"
        else:
            if self.numerator < self.denominator:
                self.type = "Proper"
            if self.numerator > self.denominator:
                self.type = "Improper"
            else:
                self.type = f"Improper Fraction Type ({self.numerator}, {self.denominator}, whole num = {self.whole_num})"

    def get(self):

        if self.whole_num == None:
            fraction = f"{self.numerator}/{self.denominator}"
        else:
            fraction = f"{self.whole_num} + {self.numerator}/{self.denominator}"

        return fraction

    def getType(self): return self.type

    def simplify(self):

        HCF = Factor(self.numerator, self.denominator).HCF()

        simplified_fraction = (self.numerator//HCF, self.denominator//HCF)

        if self.type != "Mixed":
            fraction = f"{simplified_fraction[0]}/{simplified_fraction[1]}"
        else:
            fraction = f"{self.whole_num} + {simplified_fraction[0]}/{simplified_fraction[1]}"

        return fraction

    def add(self, fraction):

        self.numerator *= fraction.denominator
        fraction.numerator *= self.denominator
        self.denominator, fraction.denominator = self.denominator * fraction.denominator, fraction.denominator * self.denominator

        self.numerator += fraction.numerator

        if self.whole_num != None and fraction.whole_num != None:
            self.whole_num += fraction.whole_num
        if self.whole_num == None and fraction.whole_num == None:
            self.whole_num = 0
        HCF = Factor(self.numerator, self.denominator).HCF()

        self.numerator //= HCF
        self.denominator //= HCF

        if self.whole_num == 0:
            self.fraction = f"{self.numerator}/{self.denominator}"
        else:
            self.fraction = f"{self.whole_num} + {self.numerator}/{self.denominator}"

        answer = f"{self.fraction}"

        return answer

    def subtract(self, fraction):

        self.numerator *= fraction.denominator
        fraction.numerator *= self.denominator
        self.denominator, fraction.denominator = self.denominator * fraction.denominator, fraction.denominator * self.denominator

        if self.whole_num != None and fraction.whole_num != None:
            if self.whole_num > fraction.whole_num:
                self.whole_num -= fraction.whole_num
            if self.whole_num < fraction.whole_num:
                fraction.whole_num -= self.whole_num
                self.whole_num = fraction.whole_num
        if self.whole_num == None and fraction.whole_num == None:
            self.whole_num = 0

        if self.numerator > fraction.numerator:
            self.numerator -= fraction.numerator
        if self.numerator < fraction.numerator:
            fraction.numerator -= self.numerator
            self.numerator = fraction.numerator

        HCF = Factor(self.numerator, self.denominator).HCF()

        self.numerator //= HCF
        self.denominator //= HCF

        if self.whole_num == 0:
            self.fraction = f"{self.numerator}/{self.denominator}"
        else:
            self.fraction = f"{self.whole_num} + {self.numerator}/{self.denominator}"

        answer = f"{self.fraction}"

        return answer

    def multiply(self, fraction):

        self.numerator *= fraction.numerator
        self.denominator *= fraction.denominator

        if self.whole_num != None or fraction.whole_num != None:
            self.whole_num *= fraction.whole_num
        if self.whole_num == None and fraction.whole_num == None:
            self.whole_num = 0

        HCF = Factor(self.numerator, self.denominator).HCF()

        self.numerator //= HCF
        self.denominator //= HCF

        if self.whole_num == 0:
            self.fraction = f"{self.numerator}/{self.denominator}"
        else:
            self.fraction = f"{self.whole_num} + {self.numerator}/{self.denominator}"

        answer = f"{self.fraction}"

        return answer

    def divide(self, fraction):

        self.numerator *= fraction.denominator
        self.denominator *= fraction.numerator

        if self.whole_num != None or fraction.whole_num != None:
            self.whole_num //= fraction.whole_num
        if self.whole_num == None and fraction.whole_num == None:
            self.whole_num = 0

        HCF = Factor(self.numerator, self.denominator).HCF()

        self.numerator //= HCF
        self.denominator //= HCF

        if self.whole_num == 0:
            self.fraction = f"{self.numerator}/{self.denominator}"
        else:
            self.fraction = f"{self.whole_num} + {self.numerator}/{self.denominator}"

        answer = f"{self.fraction}"

        return answer

    def convert(self):
        if self.type == "Mixed":
            self.numerator = self.denominator * self.whole_num + self.numerator
            self.fraction = f"{self.numerator}/{self.denominator}"
            return self.fraction
        if self.type == "Improper":
            self.whole_num = self.numerator // self.denominator
            self.numerator -= self.denominator * self.whole_num
            self.fraction = f"{self.whole_num} + {self.numerator}/{self.denominator}"
            return self.fraction
        else:
            self.fraction = f"{self.numerator}/{self.denominator}"
            return self.fraction

def Factors(number):

    factors = []

    for i in range(1, number+1):
        if number % i == 0:
            factors.append(i)

    return factors

def PrimeNumbers(range_start, range_end):

    prime_numbers = []

    for i in range(range_start, range_end+1):
        if Factors(i) == [1, i]:
            prime_numbers.append(i)

    return prime_numbers

def CompositeNumbers(range_start, range_end):

    composite_numbers = []

    for i in range(range_start, range_end+1):
        if Factors(i) == [1, i]:
            pass
        else:
            composite_numbers.append(i)
            if composite_numbers.__contains__(1):
                composite_numbers.remove(1)

    return composite_numbers