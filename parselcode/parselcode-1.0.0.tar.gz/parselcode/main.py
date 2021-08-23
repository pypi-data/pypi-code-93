#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import random
import os
this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir, "code.csv")
df = pd.read_csv(DATA_PATH)
df['P1Z'] = 10000 * df['P1Z']
df.round()
df = df.astype(int)


class Cipher(object):
    
    def __init__(self):
        pass
        
    def randArrGenerator(self, num = 21):
        rand_arr = []
        for i  in range(num):
            rand_arr.append(random.randrange(-1,219))
            rand_arr.append(random.randrange(-2,231))
            rand_arr.append(random.randrange(-171,120))
        return rand_arr   
    
    def encrypter(self, c):
        rand = random.randrange(0,121)
        arr = []
        final = []
        asc = ord(c)

        if (asc == 32 or (asc >= 33 and asc <= 47) or (asc >= 58 and asc <= 64) or (asc >= 91 and asc <= 96) or (asc >= 123 and asc <= 126) or asc == 74 or asc == 106 or asc == 90 or asc == 122):
            flag = 0
            arr.append(flag)
            arr.append(asc)
            arr = arr + self.randArrGenerator()

        elif (asc >= 48 and asc <= 57):
            flag = 1
            arr.append(flag)
            arr.append(int(c))
            arr = arr + self.randArrGenerator()

        elif (asc >= 65 and asc < 90):
            flag = 2
            arr.append(flag)
            arr.append(rand)
            for i in df.iloc[((asc - 65) * 120) + rand]:
                arr.append(i)

        elif (asc >= 97 and asc < 122):
            flag = 3
            arr.append(flag)
            arr.append(rand)
            for i in df.iloc[((asc - 97) * 120) + rand]:
                arr.append(i)

        return arr
    
    def encrypt(self, sentence):
        ciphertext = []
        for element in sentence:
            for i in self.encrypter(element):
                ciphertext.append(i//12)
                ciphertext.append(i%12)
        return ciphertext
    
    def decrypt(self, code):
        result = ""
        i = 0
        if (len(code) % 130) != 0:
            return "Invalid Input"
        for k in range(len(code) // 130):
            flag = (code[i] * 12) + code[i+1]
            identifier = (code[i+2] * 12) + code[i+3]
            if flag == 0:
                result += chr(identifier)
                i = i + 130
                continue
            if flag == 1:
                result += str(identifier)
                i = i + 130
                continue
            if flag == 2:
                i = i + 4
                arr = []
                while (i % 130) != 0 :
                    arr.append((code[i] * 12) + code[i+1])
                    i = i + 2
                iter = 0
                for j in range(identifier,3001,120):
                    condition = ((df.iloc[j]).tolist()) == arr
                    if condition:
                        result += chr(iter + 65)
                        break
                    iter = iter + 1
                continue    
            if flag == 3:
                i = i + 4
                arr = []
                while (i % 130) != 0 :
                    arr.append((code[i] * 12) + code[i+1])
                    i = i + 2
                iter = 0
                for j in range(identifier,3001,120):
                    condition = ((df.iloc[j]).tolist()) == arr
                    if condition:
                        result += chr(iter + 97)
                        break
                    iter = iter + 1
                continue   
        return result


# In[ ]:




