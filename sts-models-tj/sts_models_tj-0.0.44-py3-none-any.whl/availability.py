from datetime import datetime

from . import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# AvailabilityRequest class is used, so we must define it here or else it has to be definied by clients of the used class,
# and they don't necessarily know that they need to do this
from .availability_request import AvailabilityRequest


# Note from the future,
# avail start time and end time should be 30 minute boundary
# but, if we request times for say, 1:30-2, we dont want something
# that ends at 1:30. So, when querying for end time, use < instead of <=

# like this below

# 
#            (and_(Availability.startTime>=query_start_time, Availability.startTime<query_end_time)),
#            (and_(Availability.endTime>query_start_time, Availability.endTime<=query_end_time)),
#            (and_(Availability.startTime<=query_start_time, Availability.endTime>=query_end_time))

class Availability(Base):
    """ Availability Model for storing when users are available to tutor """
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subjects = Column(String(511), nullable=False)
    startTime = Column(DateTime, nullable=False)
    endTime = Column(DateTime, nullable=False)
    tutor = Column(String(255), ForeignKey('users.cognitoId'), nullable=False)

    requests = relationship("AvailabilityRequest", cascade="all, delete, delete-orphan")

    def __init__(self, subjects, startTime, endTime, tutor):
        self.subjects = subjects
        self.startTime = startTime
        self.endTime = endTime
        self.tutor = tutor
