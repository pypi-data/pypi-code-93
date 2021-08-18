from datetime import datetime

from . import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String


class AvailabilityRequest(Base):
    """ Availability Request Model for storing the state of a request a student makes for a tutoring session"""
    __tablename__ = "availability_request"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fromUser = Column(String(255), ForeignKey('users.cognitoId'), nullable=False)
    forAvailability = Column(Integer, ForeignKey('availability.id'), nullable=False)
    status = Column(String(31), nullable=False)

    def __init__(self, subjects, from_user, for_availability):
        self.fromUser = from_user
        self.forAvailability = for_availability
        self.status = "REQUESTED" # possibilities are REQUESTED, ACCEPTED, DENIED, CANCELED
