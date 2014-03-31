import config
import datetime 

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Text

from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

from flask.ext.login import UserMixin

import hashlib


engine = create_engine(config.DB_URI, echo=True) 
session = scoped_session(sessionmaker(bind=engine,
                         autocommit = False,
                         autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

class User(Base, UserMixin):   #UserMixin- only for user model definitions.
    __tablename__ = "users" 
    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    email = Column(String(64), nullable=False)
    
    password = Column(String(64), nullable=False)
    created_on = Column(DateTime, nullable=False, default=datetime.datetime.today())


    salt = "sdjbagadfkljgb"



    def set_password(self, password):
        password = password.encode("utf-8")
        self.password = hashlib.sha1(password + self.salt).hexdigest()

    def authenticate(self, password):
        password = password.encode("utf-8")
        return hashlib.sha1(password + self.salt).hexdigest() == self.password



class Code(Base):
    __tablename__ = "codes"
    
    id = Column(Integer, primary_key=True)
    referral_code = Column(String(200), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    expiry_date = Column(DateTime, default=datetime.datetime(3000, 1, 1)) 
    user_id = Column(Integer, ForeignKey("users.id"), default=0)
    date_added = Column(DateTime, nullable=False, default=datetime.datetime.today())
    description = Column(String(200), default="No description")
    url = Column(String(200), default="No URL")

    user = relationship("User", backref="codes")  
    company = relationship("Company", backref="codes")  



class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    buddy_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(String(10), nullable=False)

    buddy = relationship("User", foreign_keys= [buddy_id], backref="buddies")
    user = relationship("User", foreign_keys= [user_id], backref="user") 




class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    date_added = Column(DateTime, nullable=False, default=datetime.datetime.today())

    #parent to codes

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)



class CodesCat(Base):
    __tablename__ = "codescats"

    id = Column(Integer, primary_key=True)
    code_id = Column(Integer, ForeignKey("codes.id"))
    category_id = Column(Integer, ForeignKey("categories.id")) 

    code = relationship("Code", foreign_keys= [code_id], backref="categories")
    categories = relationship("Category", foreign_keys= [category_id], backref="codes") 

    #This is an association table, so the parent is really codes, the child is categories.


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    invitee_email = Column(String(64), nullable=False)
    message = Column(String(300), nullable=True)
    sent_at = Column(DateTime, nullable=False, default=datetime.datetime(3000, 1, 1))
    inviter_id = Column(Integer, ForeignKey("users.id"))
    invitee_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20))

    inviter = relationship("User", foreign_keys= [inviter_id], backref="invitees")
    invitee = relationship("User", foreign_keys= [invitee_id], backref="inviters") 









def create_tables():
    Base.metadata.create_all(engine)
    session.commit()


def connect():
    global ENGINE
    global Session

    # ENGINE = create_engine("sqlite:///my_app.db", echo=True)
    ENGINE = create_engine(config.DB_URI, echo=True) 

    Session = sessionmaker(bind=ENGINE)

    return Session()


if __name__ == "__main__":
    # create_tables()
    pass