from sqlalchemy.orm.session import sessionmaker

Session = sessionmaker(autocommit=False, autoflush=False)