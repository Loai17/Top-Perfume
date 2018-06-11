from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///database.db')

DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()


class Emails(Base):
	__tablename__ = 'emails'
	id = Column(Integer,primary_key=True)
	email = Column(String)

class ShopItems(Base):
	__tablename__ = 'shopItems'
	id = Column(Integer,primary_key=True)
	name = Column(String)
	gender = Column(String)
	brand = Column(String)
	description = Column(String)
	price = Column(String)
	thumbnail = Column(String)
	images = Column(String) #Use a sign to seperate links.

	reviews = relationship('Reviews')

class Admin(Base):
	__tablename__ = 'admin'
	id = Column(Integer,primary_key=True)
	name = Column(String)
	username = Column(String)
	password = Column(String)

class Reviews(Base):
	__tablename__ = 'reviews'
	id = Column(Integer,primary_key=True)
	rating = Column(Float)
	review = Column(String)
	shopItemID = Column(Integer, ForeignKey('shopItems.id'))

class Buyers(Base):
	__tablename__ = 'buyers'
	id = Column(Integer,primary_key=True)
	name = Column(String)
	email = Column(String)
	phone = Column(String)
	shippingAddress = Column(String)
	cartItems = Column(String) #Seperate with shopItems IDs
	paid = Column(Boolean)

Base.metadata.create_all(engine)

# chris = ShopItems(name = "La Vie En Rose",gender="men",brand="Brandd",description="Sexy af",price="200",thumbnail="None",images="none")
# session.add(chris)

# admin = Admin(name="Rami Naddaf",username="rami",password="123123")
# session.add(admin)
# session.commit()
