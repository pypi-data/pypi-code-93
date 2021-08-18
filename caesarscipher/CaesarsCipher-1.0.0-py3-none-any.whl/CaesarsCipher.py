class CaesarsCipher():

    def cipher(self, text, s):
        if self.filter(text, s):
            result = ""
            for i in range(len(text)):
                char = text[i]
                if (char.isupper()):
                    result += chr((ord(char) + s - 65) % 26 + 65)
                elif (char.islower()):
                    result += chr((ord(char) + s - 97) % 26 + 97)
                else:
                    result+=char
            return result
    
    def filter(self, text, s):
        flag = True
        for i in text:
            if not i.isalpha() and not i.isspace():
                flag = False
                raise Exception("Input Text Can Only Contain Alphabets And Spaces")
        if not isinstance(s,int):
            flag = False
            raise Exception("The Shift Value Can Only Be Integer")
        return flag
    
    def encrypt(self,text, s):
        return f"Input Value: {text}, Shift Value: {s}, Encrypted Value: {self.cipher(text, s)}"
    
    def decrypt(self,text,s=None):
        if s != None:
            return f"Input Value: {text}, Shift Value: {s}, Decrypted Value: {self.cipher(text, -s)}"
        else:
            print('[INFO] Shift Value Was Not Provided, Going Into Brute Force Mode..')
            for s in range(26):
                print(f"Input Value: {text}, Shift Value: {s}, Decrypted Value: {self.cipher(text, -s)}")

Caesar = CaesarsCipher()





