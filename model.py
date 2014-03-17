import config
import bcrypt
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, DateTime, Text

from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

from flask.ext.login import UserMixin

engine = create_engine(config.DB_URI, echo=False) 
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
    created_on = Column(DateTime, nullable=False)


    codes = relationship("Code", backref="users")  
                                #uselist=True? what does this do again? 
                                #if uselist=False, it returns a scalar, 
                                #but then, wouldn't the default be a list?

    buddies = relationship("User", secondary="friendships") 
    #Backref- something different is going on

    def set_password(self, password):
        self.salt = bcrypt.gensalt()
        password = password.encode("utf-8")
        self.password = bcrypt.hashpw(password, self.salt)

    def authenticate(self, password):
        password = password.encode("utf-8")
        return bcrypt.hashpw(password, self.salt.encode("utf-8")) == self.password


class Code(Base):
    __tablename__ = "codes"
    
    id = Column(Integer, primary_key=True)
    link_code = Column(String(200), nullable=False)
    company = Column(Integer, ForeignKey("companies.id"), nullable=False)
    expiry_date = Column(DateTime, nullable=True) #should i include a default if it is nullable?
    #category= Column(String(60), ForeignKey("categories.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date_added = Column(DateTime, nullable=False)


    # According to docs- it is the parent class that has the 'relationship' 
    # each of these Foreign Keys must refer to classes where the attribute are primary key

    codescat = relationship("Category", secondary= "codescats", backref="codes")

    #secondary- for an association table, many-one-one-many. 
    #But this is not quite this- this is one-many-one-many. One code-many categories.
    #TODO: check if it is the same.


class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    buddy_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(String(10), nullable=False)

    #association table to users- the relationship is on users.

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    date_added = Column(DateTime, nullable=False)

    #parent to codes:
    codes = relationship("Code", backref="companies")  


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)

    #this table is part of the association table CodesCat- so it is the child of codes. 


class CodesCat(Base):
    __tablename__ = "codescats"

    id = Column(Integer, primary_key=True)
    code_id = Column(Integer, ForeignKey("codes.id"))
    category_id = Column(Integer, ForeignKey("categories.id")) 

    # This is an association table, so the parent is really codes, the child is categories.




# def create_tables():
#     Base.metadata.create_all(engine)
#     u = User(email="test@test.com")
#     u.set_password("unicorn")
#     session.add(u)
#     p = Post(title="This is a test post", body="This is the body of a test post.")
#     u.posts.append(p)
#     session.commit()



if __name__ == "__main__":
    create_tables()