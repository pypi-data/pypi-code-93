from passlib.context import CryptContext

password_context: CryptContext = CryptContext(schemes=["bcrypt"])
