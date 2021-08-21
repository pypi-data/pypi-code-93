import datetime

from . import Base
from sqlalchemy import Column, DateTime, Boolean, Integer, String
from sqlalchemy.orm import relationship

# Availability class is used, so we must define it here or else it has to be definied by clients of the User class,
# and they don't necessarily know that they need to do this
from .availability import Availability


class User(Base):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    parentName = Column(String(255))
    parentEmail = Column(String(255), nullable=False)

    email = Column(String(255))
    cognitoId = Column(String(255), nullable=False, unique=True)
    registeredOn = Column(DateTime, nullable=False)
    firstName = Column(String(65), nullable=False)
    lastName = Column(String(65), nullable=False)
    school = Column(String(127), nullable=False)
    grade = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    address = Column(String(255), nullable=False)
    bio = Column(String(511)) # TODO variable length string(s)
    admin = Column(Boolean, nullable=False, default=False)

    availabilities = relationship("Availability", cascade="all, delete, delete-orphan")

    requestsSent = relationship("AvailabilityRequest", cascade="all, delete, delete-orphan")
    requestsReceived = relationship("AvailabilityRequest", cascade="all, delete, delete-orphan") # ooo this could be bad

    def __init__(self, parentName, parentEmail, email, cognitoId, firstName, lastName, school, grade, age, address, bio=""):
        self.parentName = parentName
        self.parentEmail = parentEmail
        self.email = email
        self.cognitoId = cognitoId
        self.firstName = firstName
        self.lastName = lastName
        self.school = school
        self.grade = grade
        self.age = age
        self.address = address
        self.bio = bio
        self.registeredOn = datetime.datetime.now()
