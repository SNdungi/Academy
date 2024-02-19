'''
REGX: The registration App for updating databases:
1. Persons
   1.1 institutions: Hospitals, Education, ... 
   1.2 business clientelle
   1.3 customers
   1.4 Organisations: Employment, Project, ...
   1.5 Regulatory: Govt services
2. Entities: Businesses, trusts, firms(partnerships)
3. Assets: Cars, Land, premises,...
4. Inventory: items,livestock,...
5. logs: Virtual inventory

BUILD:
1. go to Set up to select nature of operation
2. Pick pre defined template
3. Update required fields
4. Create to preview
5. Run to Integrate

'''

from flask import Flask, g
from flask_mail import Mail
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5 # pip install bootstrap-flask
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)
app.secret_key='thel0rdismypr0viderisha11notw@nt'
bootstrap = Bootstrap5(app)
  

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///TransXcore.db"
db=SQLAlchemy(app)


app.config['MAIL_SERVER']='smtp-mail.outlook.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']='stephen.ndungi@outlook.com'
app.config['MAIL_PASSWORD']='X@v1er@8213'
mail=Mail(app)

from app import routes

