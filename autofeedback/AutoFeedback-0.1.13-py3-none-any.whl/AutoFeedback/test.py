import numpy as np
import matplotlib.pyplot as plt
import sympy as sy

def check_value(a,b):
    import numpy as np

    if (isinstance(a,str) and isinstance(b,str)) \
        or (isinstance(a,dict) and isinstance(b,dict)):
        return (a==b)
    else:
        try: # treat inputs as ndarrays and compare with builtin
            return np.all(np.isclose(a,b))
        except: # if not ndarrays, treat as list (of strings) and compare elements
            try: 
                for x,y in zip(a,b):
                    if not(x==y): return False
                return True
            except:
                return False
a={"name":"Andrew", "age":34}
b={"age":34, "name":"Andrew"}
print (check_value(a,b))
