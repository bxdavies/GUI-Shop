#############
# Libraries #
#############

# SQLAlchemy Libraries #
from itertools import product
from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, Boolean, Numeric, Date, Text
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Other Libraries #
import bcrypt
from sqlalchemy.sql.sqltypes import Date
from datetime import datetime
import os

########
# Base #
########
base = declarative_base()

#################
# Create Engine #
##################
engine = create_engine(os.getenv("DATABASE_STRING"))

########################
# Create Session Maker #
########################
Session = sessionmaker(bind=engine)


############
# Customer #
############
class Customer(base):
    """ Customer Accounts """

    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True, autoincrement=True)
    forename = Column(String(35), nullable=False)
    surname = Column(String(35), nullable=False)
    dob = Column(Date(), nullable=False)
    email_address = Column(String(256), nullable=False)
    password = Column(String(255), nullable=False)

    def setPassword(self, password):
        '''
        Hash Password

        Parameters:
            password: The password to hash
        '''
        self.password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt())

    def checkPassword(self, password):
        '''
        Checked Hashed Password

        Parameters:
            password: The password to check against

        Returns:
            boolean
        '''
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))


#########
# Staff #
#########
class Staff(base):
    """ Staff Members """

    __tablename__ = 'staff'

    id = Column(Integer, primary_key=True, autoincrement=True)
    forename = Column(String(35), nullable=False)
    surname = Column(String(35), nullable=False)
    password = Column(String(255), nullable=False)

    def setPassword(self, password):
        self.password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt())

    def checkPassword(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))


###########
# Booking #
###########
class Booking(base):
    """ Customer Bookings """

    __tablename__ = 'booking'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    placed_datetime = Column(
        DateTime(), default=datetime.now(), nullable=False)
    booking_datetime = Column(DateTime(), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    approved = Column(Boolean, default=False, nullable=False)

    customer = relationship('Customer')


###########
# Product #
###########
class Product(base):
    """ Products """

    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text(), nullable=False)
    image = Column(String(255), nullable=False)
    price = Column(Numeric(14, 2), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    stock = Column(Integer, nullable=False)

    category = relationship('Category')


############
# Category #
############
class Category(base):

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text(), nullable=False)


#########
# Order #
#########
class Order(base):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    placed_datetime = Column(
        DateTime(), default=datetime.now(), nullable=False)
    collection_datetime = Column(DateTime(), nullable=False)
    sub_total = Column(Numeric(14, 2), nullable=False)
    total = Column(Numeric(14, 2), nullable=False)
    completed = Column(Boolean(), default=False, nullable=False)

    customer = relationship('Customer')


#############
# Sub Order #
#############
class SubOrder(base):

    __tablename__ = 'sub_order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('order.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product_quantity = Column(Integer(), nullable=False)

    order = relationship('Order')
    product = relationship('Product')


##############
# Create All #
##############
base.metadata.create_all(engine)
