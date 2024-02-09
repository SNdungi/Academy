from sqlalchemy import create_engine, DateTime, Column, String, Integer,Boolean, Float, ForeignKey,Sequence,func,MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base,relationship
from flask_bcrypt import Bcrypt
from datetime import datetime
import random
from flask_security import UserMixin,RoleMixin
from itsdangerous.url_safe import URLSafeTimedSerializer as serilz


bcrypt= Bcrypt()
Base=declarative_base()
db=SQLAlchemy()

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
    

class customer(Base):#dim (task feature)
    __tablename__='customer'
    customer_id=Column(Integer,primary_key=True,autoincrement=True)
    member_id=Column (String(20), unique=True)
    lastname=Column(String(30),nullable=False)
    firstname=Column(String(30),nullable=False)
    othernames=Column(String(30))
    email=Column(String(60),nullable=False,unique=True)
    contact=Column(Integer)# FOR MOBILE WE WILL USE CONTACT AS THE VALIDATOR
    dateofbirth=Column(String(20))
    gender=Column(String(20))
    identification=Column(String(20),nullable=False,unique=True)#id/passport
    nationality=Column(String(50),nullable=True)
    country_of_residence=Column(String(50),nullable=True)
    membership_status=Column(String(40),nullable=True) 
    task_id=Column(Integer,ForeignKey('task.task_id')) #backpop='task'
    #REF TASK
    task=relationship('task',back_populates='customers')#foreign
    users=relationship('user',back_populates= 'customer')
    creditors=relationship('creditor',back_populates='customer')
    guarantors=relationship( 'guarantor',back_populates='customer')
    transactions= relationship('transaction', back_populates='customer')
    created_at = Column(DateTime, default=datetime.utcnow) #meta
    updated_at = Column(DateTime, onupdate=datetime.utcnow) #meta

    @property
    def full_name(self):
         return f'{self.lastname} {self.othernames}'
    def __repr__(self):
         return(f'customer(member_id={self.member_id},' 
                f'firstname={self.lastname},'
                f'lastname={self.othernames}, email={self.email},contact={self.contact},id= {self.identification},created= {self.created_at})')

#This is the  credit application table 
#The app will populate a credit form for signing
#The credit application will get additional info from credit  and guarantor tables
#verify shares (Share x 3)
class creditor(Base):#feature
    __tablename__='creditor'
    cr_id=Column(Integer,primary_key=True,autoincrement=True)#autogen
    credit_id=Column(String(10),nullable=False, unique=True)#autogen
    credit_amount=Column(Float, nullable=False)
    repayment_period=Column(Integer)
    member_cr_id=Column(String(50))
    credit_interest=Column(Float, nullable=False)
    credit_processing_fee=Column(Float, nullable=False)
    credit_service_fee=Column(Float, nullable=False)
    monthly_repayment=Column(Float, nullable=False)
    repayment_amount=Column(Float, nullable=False)
    credit_product_name=Column(String(60))
    product_id=Column(Integer, ForeignKey('product.product_id'))
    #REF PRODUCT
    customer_id=Column (Integer,ForeignKey('customer.customer_id'))
    #REF CUSTOMER
    physical_address=Column(String(100),nullable=True)
    city=Column(String(60),nullable=True)
    employment_address=Column(String(60),nullable=False)
    employment_contact=Column(Integer,nullable=True)
    employment_email=Column(String(50),nullable=True)
    kin_name=Column(String(50),nullable=False)
    kin_contact=Column(Integer,nullable=False)
    status=Column(String(10),nullable=False, default='application')#review,approved,declined,active,cleared
    approver=Column(String(10))
    step=Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow) #meta
    updated_at = Column(DateTime, onupdate=datetime.utcnow) #meta
    guarantors = relationship("guarantor", back_populates="creditor",cascade='delete')
    transactions=relationship('transaction', back_populates='creditor')
    customer=relationship('customer',back_populates='creditors')
    product=relationship('product', back_populates='creditors')
    notes=relationship('note', back_populates= 'creditor')
    
class note(Base):
    __tablename__='note'
    notes_id=Column(Integer,Sequence("notes_id_seq"),primary_key=True,autoincrement=True)
    user_id=Column(Integer,ForeignKey('user.id'))
    creditor_id=Column(Integer,ForeignKey('creditor.cr_id'))
    notes=Column(String(500))
    status=Column(String(10))
    credit_id=Column(String(10))   
    timestamp=Column(DateTime, default=datetime.utcnow)
    user=relationship('user',back_populates= 'notes')
    creditor=relationship('creditor', back_populates='notes')

class transaction(Base):#feature(only foreign)
    __tablename__='transaction'
    txn_id=Column(Integer,Sequence("txn_id_seq"),primary_key=True,autoincrement=True)
    date=Column(DateTime)
    user_id=Column (String(20),nullable=False)
    narrative_beneficiary=Column(String(150),nullable=False)
    CR_DR=Column(String(10),nullable=False)
    transaction_purpose=Column(String(50),nullable=False)
    credit_id=Column(String(20),nullable=True)
    amount=Column(Float,nullable=False)
    user_id=Column(Integer, ForeignKey('user.id'))
    cr_id=Column(Integer, ForeignKey('creditor.cr_id'))# creditor
    product_id=Column(Integer,ForeignKey('product.product_id'))# product
    customer_id=Column (Integer,ForeignKey('customer.customer_id'))# customer
    created_at = Column(DateTime, default=datetime.utcnow) #meta
    updated_at = Column(DateTime, onupdate=datetime.utcnow) #meta
    user=relationship('user',back_populates='transactions')
    customer=relationship( 'customer',back_populates='transactions')
    creditor=relationship('creditor',back_populates='transactions')
    product=relationship('product', back_populates='transactions')

class product(Base):#dimension(no foreign)
    __tablename__='product'
    product_id=Column(Integer,Sequence("prod_id_seq"),primary_key=True,autoincrement=True)
    product_name=Column (String(50),nullable=False,unique=True)
    product_category=Column(String(50))
    max_period_month=Column(Integer,nullable=False)
    interest_month=Column(Float,nullable=False)
    service_fees=Column(Float,nullable=False)
    processing_fees=Column(Float,nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow) #meta
    updated_at = Column(DateTime, onupdate=datetime.utcnow) #meta
    creditors = relationship("creditor", back_populates="product")
    transactions=relationship('transaction',back_populates='product')



class guarantor(Base):#feature
    __tablename__='guarantor'
    grnt_id=Column(Integer,Sequence("guarantor_id_seq"),primary_key=True,autoincrement=True)
    amount_guaranteed=Column(Float,nullable=False)
    guarantor_member_id=Column(String(20),nullable=False)
    guarantor_lastname=Column(String(50),nullable=False)
    guarantor_firstname=Column(String(50),nullable=False)
    guarantor_email=Column(String(50),nullable=False)
    guarantor_contact=Column(Integer,nullable=False)
    credit_id=Column (Integer,nullable=False)#autopopulate
    cr_id=Column(Integer,ForeignKey('creditor.cr_id'))
    #backref="creditguarantee"
    customer_id=Column(Integer,ForeignKey('customer.customer_id'))
    #backref='memberguarantee'
    status=Column(String(10),nullable=False, default='pending')#confirmed status
    applicant_member_id=Column(String(50),nullable=False)#autopopulate
    created_at = Column(DateTime, default=datetime.utcnow) #meta
    updated_at = Column(DateTime, onupdate=datetime.utcnow) #meta
    customer=relationship('customer', back_populates='guarantors')
    creditor=relationship('creditor', back_populates='guarantors')


def generate_user_id(firstname,lastname):
            new_number = random.randint(1,999)
            f =(firstname[0].upper() if firstname else "")
            l =(lastname[0].upper() if lastname else "")

            return f'HSADM{f}{l}{new_number:03d}'

def new_id(form,table,session):
    firstname=form['firstname']
    lastname=form['lastname']
    last_customer = session.query(table).order_by(table.customer_id.desc()).first()
    last_customer_id = last_customer.customer_id if last_customer else 0
    new_member_id = generate_member_id(firstname=firstname, lastname=lastname, index=last_customer_id + 1)
    return new_member_id

def generate_member_id(firstname,lastname,index):
        f = firstname[0].upper() if firstname else ""
        l= lastname[0].upper() if lastname else ""
        return f'HS{f}{l}{index:04d}'

def credit_id_gen(session,table):
        last_cr = session.query(table).order_by(table.cr_id.desc()).first()
        last_cr_id = last_cr.cr_id if last_cr else 0
        rn=random.randint(1,999)
        return f'LN{rn:03d}{last_cr_id + 1:04d}'


    
