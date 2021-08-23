
import re
from businessLogic.validationException import ValidationException
from dataAcces.userDA import UserDA
from entites.user import User

class UserManager:
    
    def SignUp(self, user: User, passwordConfirm: bytes):
        da = UserDA()
        
        self.__checkValidEmail(user.Email)
        self.__checkPasswordConfirm(user.Password,passwordConfirm)
        
        return da.Insert(user)

    def Login(self, email: str, password: str):
        da = UserDA()
        
        resultDb = da.GetByEmailPassword(email, password)

        if(resultDb != None):
            return User(resultDb[1],resultDb[2],resultDb[3],id=resultDb[0])
        else:
            return None

    def __checkPasswordConfirm(self, password: bytes, passwordConfirm: bytes):
        if(password != passwordConfirm):
            raise ValidationException("Debe ingresar una contraseña que coincida con el campo de confirmación.", field="Password")

    def __checkValidEmail(self, email: str):
        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
        
        if(not re.search(regex, email)):
            raise ValidationException("Debe ingresar un email válido.", field="Email")