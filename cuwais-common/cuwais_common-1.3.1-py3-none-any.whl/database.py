import os

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Float, Index
from sqlalchemy.orm import declarative_base, relationship, Session

from cuwais.config import config_file

_Base = declarative_base()
_Engine = create_engine(config_file.get("db_connection"), echo=config_file.get("debug"), future=True)


def create_session() -> Session:
    return Session(_Engine)


class User(_Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    real_name = Column(Text, nullable=False)
    nickname = Column(Text, nullable=False, unique=True, index=True)
    google_id = Column(String(255), nullable=True, unique=True, index=True)
    is_bot = Column(Boolean, unique=False, nullable=False, default=False)
    is_admin = Column(Boolean, unique=False, nullable=False, default=False)
    display_real_name = Column(Boolean, unique=False, nullable=False, default=False)

    submissions = relationship("Submission", back_populates="user")

    @property
    def display_name(self):
        return self.nickname if not self.display_real_name else self.real_name

    def to_public_dict(self) -> dict:
        public_vals = {'_cuwais_type': 'user',
                       'user_id': self.id,
                       'display_name': self.display_name,
                       'nickname': self.nickname,
                       'display_real_name': self.display_real_name,
                       'is_bot': self.is_bot,
                       'is_admin': self.is_admin}

        if self.display_real_name:
            public_vals['real_name'] = self.real_name

        return public_vals

    def to_private_dict(self) -> dict:
        private_vals = {'real_name': self.real_name,
                        'google_id': self.google_id}

        return {**self.to_public_dict(), **private_vals}

    def __repr__(self):
        return f"User(id={self.id!r}, nickname={self.nickname!r})"


class Submission(_Base):
    __tablename__ = 'submission'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    submission_date = Column(DateTime, unique=False, nullable=False)
    url = Column(Text, unique=False, nullable=False)
    active = Column(Boolean, unique=False, nullable=False, default=True, index=True)
    files_hash = Column(Text, unique=False, nullable=False)

    user = relationship("User", back_populates="submissions")
    results = relationship("Result", back_populates="submission")

    def to_public_dict(self) -> dict:
        return {'_cuwais_type': 'submission',
                'submission_id': self.id,
                'user_id': self.user_id,
                'submission_date': self.submission_date}

    def to_private_dict(self) -> dict:
        private_vals = {'url': self.url,
                        'active': self.active,
                        'files_hash': self.files_hash}

        return {**self.to_public_dict(), **private_vals}

    def __repr__(self):
        return f"Submission(id={self.id!r}, url={self.url!r}, url={self.submission_date!r})"


class Match(_Base):
    __tablename__ = 'match'

    id = Column(Integer, primary_key=True)
    match_date = Column(DateTime, unique=False, nullable=False, index=True)
    recording = Column(Text, unique=False, nullable=False)

    results = relationship("Result", back_populates="match")

    def to_public_dict(self) -> dict:
        return {'_cuwais_type': 'match',
                'match_id': self.id,
                'match_date': self.match_date,
                'recording': self.recording}

    def to_private_dict(self) -> dict:
        private_vals = {}

        return {**self.to_public_dict(), **private_vals}

    def __repr__(self):
        return f"Match(id={self.id!r}, match date={self.match_date!r})"


class Result(_Base):
    __tablename__ = 'result'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('match.id'), nullable=False, index=True)
    submission_id = Column(Integer, ForeignKey('submission.id'), nullable=False, index=True)
    outcome = Column(Integer, unique=False, nullable=False, index=True)
    points_delta = Column(Float, unique=False, nullable=False)
    healthy = Column(Boolean, unique=False, nullable=False, index=True)
    player_id = Column(Text, unique=False, nullable=False)
    prints = Column(Text, unique=False, nullable=True)
    result_code = Column(Text, unique=False, nullable=False)

    submission = relationship("Submission", back_populates="results")
    match = relationship("Match", back_populates="results")

    def to_public_dict(self) -> dict:
        return {'_cuwais_type': 'result',
                'match_id': self.match_id,
                'submission_id': self.submission_id,
                'outcome': self.outcome,
                'player_id': self.player_id}

    def to_private_dict(self) -> dict:
        private_vals = {'points_delta': self.points_delta,
                        'healthy': self.healthy,
                        'prints': self.prints,
                        'result_code': self.result_code}

        return {**self.to_public_dict(), **private_vals}

    def __repr__(self):
        return f"Result(id={self.id!r}, match id={self.match_id!r}, submission id={self.submission_id!r})"


Index('healthy_outcome_index', Result.healthy, Result.outcome)


def create_tables():
    _Base.metadata.create_all(_Engine)
