from sqlalchemy import create_engine, DateTime, Column, String, Integer,Boolean, Float, ForeignKey,Sequence,func,MetaData
from app import db
from sqlalchemy.orm import declarative_base,relationship
from flask_bcrypt import Bcrypt
from datetime import datetime
import random
from flask_security import UserMixin,RoleMixin
from itsdangerous.url_safe import URLSafeTimedSerializer as serilz


bcrypt= Bcrypt()
Base=declarative_base()

class task(Base,RoleMixin): # Dim
    __tablename__='task'
    task_id= Column(Integer,autoincrement=True,primary_key=True)
    task_name=Column(String(30), unique=True, nullable=False)
    task_desc=Column(String(200))
    customers=relationship('customer',back_populates='task')#task in customer
    users=relationship('user', back_populates='task')#task in user

class user(Base,UserMixin): # feature (txn dim)
    __tablename__='user'
    id= Column(Integer(),primary_key=True, autoincrement=True)
    user_id=Column(String(20),unique=True)
    firstname=Column(String(30),nullable=False)
    lastname=Column(String(30),nullable=False)#lastname
    email=Column(String(60),nullable=False,unique=True)
    password=Column(String(100),nullable=False)
    task_id=Column(Integer,ForeignKey('task.task_id')) #back_populates= users
    customer_id=Column(Integer,ForeignKey('customer.customer_id')) #back_populates= customer
    status=Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow) #meta
    updated_at = Column(DateTime, onupdate=datetime.utcnow) #meta
    task=relationship('task', back_populates='users')#foreign
    transactions= relationship('transaction', back_populates='user')
    customer=relationship('customer', back_populates= 'users')#foreign
    notes=relationship('note', back_populates= 'user')

    def __repr__(self):
         return(f'user(user_id={self.user_id}, firstname={self.firstname}, lastname={self.lastname}, email={self.email}, created= {self.created_at})')
    
    @classmethod
    def generate_password_hash(cls, password):
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    @classmethod
    def check_password(cls, dbpassword, password):
        if dbpassword is not None:
            try:
                bcrypt.check_password_hash(dbpassword, password)
                return bcrypt.check_password_hash(dbpassword, password)
            except:
                return False
    
    def get_id(self):
        return str(self.user_id)
    
    def is_active(self):
        return self.is_active
    
    @staticmethod
    def get_token(id,key):
        serial=serilz(key)
        return serial.dumps({'user_id':id})

         
    @staticmethod
    def verify_token(key,token):
        serial=serilz(key)
        try:
            user_id=serial.loads(token)['user_id']
        except:
            return None
        return user_id
    
