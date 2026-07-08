from sqlmodel import SQLModel, Session, create_engine

engine=create_engine(url="sqlite:///data/Database.db", echo=True, connect_args={'check_same_thread':False})

def create_database():
    SQLModel.metadata.create_all(bind=engine)

def get_session():
    with Session(bind=engine) as session:
        yield session