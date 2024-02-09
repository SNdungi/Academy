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


from flask import Flask, request,render_template,url_for,redirect,flash,session,g,jsonify,send_from_directory,make_response
from flask_mail import Mail,Message
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func,and_,or_
import models
from forms import LoginForm,UserMaintenanceForm,creditProducts,ForgotPassword,PasswordReset
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5 # pip install bootstrap-flask
from dbops import create_query_new, update_entry,data_extractor,update_customer_csv,create_tables
from reports import generate_pdf_statement,UserDetails,Transaction,Summary
from flask_migrate import Migrate
from flask_login import LoginManager, login_required,login_user,current_user,logout_user
import pandas  as pd
import random



app = Flask(__name__)

app.secret_key='thel0rdismypr0viderisha11notw@nt'
bootstrap = Bootstrap5(app)
current_year = datetime.today().year   

app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///TransXcore.db"
db=SQLAlchemy(app)
migrate=Migrate(app,db)
login_manager=LoginManager(app)
login_manager.login_view="login"

app.config['MAIL_SERVER']='smtp-mail.outlook.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']='stephen.ndungi@outlook.com'
app.config['MAIL_PASSWORD']='X@v1er@8213'
mail=Mail(app)


#DATABASE SESSIONS_________________________________________________________________________________________________________________________________________________
# creates unique sessions for each process

with app.app_context():
    create_tables(db.engine)
    session_maker = sessionmaker(autocommit=False, bind=db.engine)

def create_new_db_session():
  dbsession=session_maker()
  return dbsession

def get_db_session():
    if 'db_session' not in g:
        g.db_session = create_new_db_session() 
    return g.db_session

@app.teardown_appcontext
def close_db_session(error):
    db_session = g.pop('db_session', None)
    if db_session is not None:
        db_session.close()

#USER LOADER_________________________________________________________________________________________________________________________________________________________
# on login the loader checks the database on maintains a fresh verification of the active user for each App Call
@login_manager.user_loader
def load_user(user_id):
    dbsession = get_db_session()
    user = dbsession.query(models.user).filter_by(user_id=user_id).first()
    return user

#ADMIN CREATION__________________________________________________________________________________________________________________________________________
# creates unique sessions for each process
class TablesAdm(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated # and current_user.is_admin=True
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('home',next=request.url))
admin= Admin(app)
admin.add_view(TablesAdm(models.user,db.session))
admin.add_view(TablesAdm(models.customer,db.session))

#DATABASE MIGRATION___________________________________________________________________________________________________________________________________________
#ONLY FOR MIGRATIONS from excel/ CSV version of customers 
@app.route("/hifadhi", methods=['GET','POST'] )
def dbupdate():
    dbsession = get_db_session()
    credit_products_form= creditProducts()
    if request.method=='POST':
      dbsession.query(models.customer).delete()
      link=request.form['link']
      Data=data_extractor(file=link)#file is from the maintenance.html
      for index, row in Data.iterrows():
       row = row.apply(lambda x: "" if pd.isna(x) else x)
       # Create a Customer instance for each row
       new_member = models.customer(
        member_id=row['member_id'],
        lastname=row['lastname'],
        firstname=row['firstname'],
        othernames=row['othenames'],  # Assuming this column is 'othenames' in your DataFrame
        email=row['email'],
        contact=row['contact'],
        dateofbirth=row['dateofbirth'],
        gender=row['gender'],
        identification=row['identification'],
        nationality=row['nationality'],
        country_of_residence=row['country_of_residence'],
        membership_status=row['membership_status'],
        task_id=row['task_id'],
        created_at=datetime.utcnow(),  # Assuming you want to update this field with the current time
        updated_at=datetime.utcnow(),
        )
       #new_member.member_id=models.generate_member_id(new_member.firstname,new_member.lastname,index+1)
       #update existing members by checking the 
       existing_member=dbsession.query(models.customer).filter_by(member_id=row['member_id']).first()
       if existing_member:
           update_customer_csv(existing=existing_member,session=dbsession,data=Data)
       else:
           update_entry(new_member,dbsession)     
    return render_template('db_maintenance.html',current_user=current_user,credit_products_form=credit_products_form)

@app.route("/hifadhi/txn", methods=['GET','POST'] )
def dbupdate_txn():
    dbsession = get_db_session()
    if request.method=='POST':
       print('1')
       dbsession.query(models.transaction).delete()
       dbsession.commit()
       print('2')
       link=request.form['link_txn']
       Data=data_extractor(file=link)#file is from the maintenance.html
       for index, row in Data.iterrows():
            row['date'] = pd.to_datetime(row['date'], errors='coerce')
        #Query
            new_txn= models.transaction(
                    date=row['date'],
                    user_id=row['user_id'],
                    narrative_beneficiary=row['narrative_beneficiary'],
                    CR_DR=row['CR_DR'], 
                    transaction_purpose=row['transaction_purpose'],
                    credit_id=row['credit_id'],
                    amount=row['amount'],
                    created_at=datetime.utcnow(),  
                    updated_at=datetime.utcnow(),
                    )
            #update existing members by checking the 
            update_entry(new_txn,dbsession)     
    return render_template('db_maintenance.html',current_user=current_user)

# CREATE USERS_____________________________________________________________________________________________________________________________________________
# create Admins that can access all screens 
# Check users for different roles
# Create limited Members(Can access only limited screens to view personal details)

@app.route("/maintenance", methods=['GET', 'POST'])
def maintenance():
   
   dbsession = get_db_session()
   UserMaintenance = UserMaintenanceForm()
   if request.method == 'POST' and UserMaintenance.validate_on_submit():
        # Check if the user with the same email already exists
        existing_user = dbsession.query(models.user).filter_by(email=UserMaintenance.email.data).first()

        if existing_user:
            flash("This user already exists!")
        else:
            # Generate a user ID, created_at, and updated_at timestamp
            existing_mbr=dbsession.query(models.customer).filter_by(email=UserMaintenance.email.data).first()
            if existing_mbr:
                user_id=existing_mbr.member_id
            else:
                user_id = models.generate_user_id(UserMaintenance.firstname.data,UserMaintenance.lastname.data)  # Implement user ID generation logic

            task=dbsession.query(models.task).filter(models.task.task_name==UserMaintenance.tasks.data).first()
            customer=dbsession.query(models.customer).filter(models.customer.member_id==UserMaintenance.memberid.data).first()
            new_user = models.user(
                user_id=user_id,
                firstname=UserMaintenance.firstname.data,
                lastname=UserMaintenance.lastname.data,
                email=UserMaintenance.email.data,
                task=task,
                customer=customer,
            )
            new_user.password=new_user.generate_password_hash(UserMaintenance.password.data)
            print(new_user)
            # Add the user to the database
            update_entry(new_user,dbsession)
            flash('User registered successfully', 'success')
            return redirect(url_for('maintenance'))
   return render_template('app_maintenance.html', user_update_form=UserMaintenance,current_user=current_user,requestor=None)

@app.route("/maintenance/change", methods=['GET', 'POST'])

def maintenance_change():
   dbsession = get_db_session()
   if request.method=='POST':
            data = request.get_json()
            id = data.get('user_id')
            if id is None:
                return jsonify({'error': 'Customer ID not provided'}), 400 
            applicant=dbsession.query(models.user).filter_by(user_id=id).first()
            if applicant is None:
                return jsonify({'error': 'No data found for the provided customer ID'}), 400 
            if applicant.member_id==current_user.user_id:
                user_info = {
                    'lastname': applicant.lastname, 
                    'firstname': applicant.firstname,
                    'email': applicant.email,
                    }
            else:
                return jsonify({'error': 'User not authorised to Book a credit'}), 400 
            return jsonify(user_info)
   

#APP LOGIN / LOGOUT_________________________________________________________________________________________________________________________________________________________________
@app.route("/", methods=['GET','POST'])
def login():
    login_form=LoginForm()
    dbsession = get_db_session()

    if request.method == 'POST' and login_form.validate_on_submit() :
        my_id =login_form.userid.data.upper()
        pword = login_form.password.data
        user=dbsession.query(models.user).filter_by(user_id=my_id).first()

        if user and models.user.check_password(dbpassword=user.password,password=pword) and user.status:
            print(models.user.check_password(dbpassword=user.password,password=pword))
            login_user(user)   
            next_url = url_for('home')
            if not next_url:
                next_url = url_for('logout')
            return redirect(next_url)
        elif user and models.user.check_password(dbpassword=user.password,password=pword):
            flash('please reset your password!')
            reset_token=login_form.password.data
            reset_code=models.user.generate_password_hash(reset_token)
            session['reset_code']={'code':reset_code, 'email':user.email,'id':user.user_id}
            return redirect (url_for('password_reset'))
        else:
            flash('invalid user or password')
    
    return render_template('app_login.html', date_year=current_year,form= login_form)    

@app.route('/logout')
def logout():
    logout_user()
 # Clear the authentication status from the session
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET','POST'])
def forgot_password():
    dbsession=get_db_session()
    change_form=ForgotPassword()
    if request.method=='POST':
        user=dbsession.query(models.user).filter(models.user.email==change_form.email.data).first()
        if user and change_form.validate_on_submit():
            reset_token= str(random.randint(1000,9999))#send to phone
            reset_code=models.user.generate_password_hash(reset_token)# i need to salt
            session['reset_code']={'code':reset_code, 'email':user.email}
            send_mail(user,reset_token)
            flash(' email sent, please check the link to reset your password! ')
            return render_template('forgot_password.html',change_form=change_form )
        else:
            flash(' unable to verify email! ')
            return render_template('forgot_password.html ',change_form=change_form )
    return render_template('forgot_password.html ',change_form=change_form )

@app.route('/password-reset', methods=['GET','POST'])
def password_reset():
    dbsession=get_db_session()
    reset_form=PasswordReset()
    if request.method=='POST':
        if reset_form.validate_on_submit():
          pword = reset_form.current_password.data
          if 'reset_code' in session and session['reset_code']:
            token=session.get('reset_code',{})
            user=dbsession.query(models.user).filter_by(user_id=token['id']).first()
            member=dbsession.query(models.customer).filter_by(member_id=token['id']).first()
            print(member.firstname)
            if user and models.user.check_password(dbpassword=token,password=pword) and member:# use salt
                if member.email==token['email']:
                    # ask for the token sent email/phone
                    if reset_form.new_password.data==reset_form.confirm_password.data:
                        user.password=user.generate_password_hash(reset_form.new_password.data)
                        user.status=True
                        update_entry(user,dbsession)
                        flash(f'pasword changed {reset_form.new_password.data},for {user.firstname} and status is {user.status} ')
                        return redirect(url_for('login'))
                    else:
                        flash(' The passwords do not match, try again! ')
                        return redirect(url_for('password_reset'))
                else:
                    flash(' member not maintained of email missing ')
                    return redirect(url_for('password_reset'))
            else:
                flash(' Confirm token value and email credentials! ')
                return redirect(url_for('password_reset'))
          else:
            flash(' Illegal access. Please contact Admin for a reset! ')      
    return render_template('reset_password.html',reset_form=reset_form)

def send_mail(user,reset_token):
    token=models.user.get_token(id=user.user_id,key=app.secret_key)
    msg=Message('Passord Reset Request',recipients=[user.email],sender='stephen.ndungi@outlook.com')
    msg.body=f'''  To reset your password please follow the link below
    {url_for('reset_token',token=token,_external=True)}

    your reset password is {reset_token}

    if you did not request please ignore

    Regards,
    regx@fluidcore.org
    '''
    mail.send(msg)

@app.route('/reset_token/<token>',methods=['GET','POST'])
def reset_token(token):
    dbsession=get_db_session()
    user_id=models.user.verify_token(app.secret_key,token)
    print(user_id,'from mail')
    user=dbsession.query(models.user).filter(models.user.user_id==user_id).first()
    user_data={'id':user_id}
    reset_code_data = session.get('reset_code', {})
    reset_code_data.update(user_data)
    session['reset_code'] = reset_code_data
    if user is None:
        flash('please try again','warning')
        return redirect (url_for('login'))
    return redirect(url_for('password_reset'))
#APP HOME___________________________________________________________________________________________________________________________________________________________________-
@app.route("/home")
def home():
    dbsession=get_db_session()
    return render_template('index.html', date_year=current_year,current_user=current_user)

# CUSTOMER ONBOARDING__________________________________________________________________________________________________________________________________________________ 
@app.route('/membership-join',methods=['GET','POST'])
@login_required
def members():
    dbsession = get_db_session()
    if request.method== "POST":
        create_query_new(table=models.customer,session=dbsession,form=request.form)
    return render_template('registration.html', current_user=current_user,existing=None)

#MEMBERSHIP VIEW SCREEN___________________________________________________________________________________________________________________________________________________
@app.route('/membership-join/view', methods=['POST'])
@login_required
def membersview():
  dbsession = get_db_session()
  if request.method=='POST':
    existing=create_query_new(table=models.customer, session=dbsession, form=request.form) 
    if existing is None:
        flash('Missing: Confirm and only search with Member_Id')

    return render_template('registration.html', current_user=current_user, existing=existing)


# STATEMENTS _______________________________________________________________________________________________________________________________________________________
#Member Reports: Statements of shares, Dividends and mebership
#Guarantee Report:  Shares Exposed
#credit Report:credit Status
@app.route('/Statements-Search', methods=['GET','POST'])
@login_required
def statements():
    dbsession = get_db_session()
    if request.method == 'POST':
        user_id = request.form['customer_id']
        user_transactions = dbsession.query(models.transaction).filter(models.transaction.user_id == user_id).all()
        user_details= user_transactions[0] if user_transactions else None
        transaction_sums = (
            dbsession.query(
                models.transaction.transaction_purpose,
                func.sum(models.transaction.amount).label('total_amount')
            )
            .filter(models.transaction.user_id == user_id)
            .group_by(models.transaction.transaction_purpose)
            .all()
        )
        return render_template('report_request.html',user_transactions=user_transactions,transaction_sums=transaction_sums,current_user=current_user,user_details=user_details)    
    return render_template('report_request.html',current_user=current_user, user_details=None)  

# REPORTS ___________________________________________________________________________________________________________________________________________________________
#Regulatory Returns Reports: Statements of shares, Dividends and mebership
    # P&L
    # Balance Sheet
    # Director credits
    # Membership
# Perfomance Dashboard: Graphs and Plots
@app.route('/static/pdfjs-dist/<path:filename>')
def pdfjs_static(filename):
    return send_from_directory('static/pdfjs-dist', filename)

#personal reports
@app.route('/Reports', methods=['GET','POST'])
@login_required
def reports():
    dbsession = get_db_session()
    user_id = current_user.user_id
    user_transactions = dbsession.query(models.transaction).filter(models.transaction.user_id == user_id).all()
    user_details = user_transactions[0] if user_transactions else None
    transaction_sums = (
        dbsession.query(
            models.transaction.transaction_purpose,
            func.sum(models.transaction.amount).label('total_amount')
        )
        .filter(models.transaction.user_id == user_id)
        .group_by(models.transaction.transaction_purpose)
        .all()
    )

    if request.method == 'POST':

        if not user_transactions:
            return redirect(url_for('members'))       
        user_details=UserDetails(user_id=user_id, narrative_beneficiary=user_details.narrative_beneficiary, date = datetime.utcnow())
        user_txns=[]
        for transaction in user_transactions:
            user_txn=Transaction(date=transaction.date, transaction_purpose=transaction.transaction_purpose, credit_id=transaction.credit_id, amount=transaction.amount)
            user_txns.append(user_txn)
        summary=[Summary(purpose=sum.transaction_purpose,amount=sum.total_amount) for sum in transaction_sums]

        filename = f"{user_id}_customer_statement.pdf"
        pdf=generate_pdf_statement(summary,user_txns, user_details, filename)

        response = make_response(pdf.output(dest='S').encode('latin-1'))  # Use dest='S' to get the content as a string

        # Set the appropriate headers for a PDF filewww
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename={filename}'

        return response

    return render_template('reports.html', user_transactions=user_transactions, transaction_sums=transaction_sums, current_user=current_user, user_details=user_details)
#UNDER CONSTRUCTION______________________________________________________________________________________________________________________________________________________
# Phase 3

#Productivity
@app.route('/productivity', methods=['GET','POST'])
@login_required
def productivity():
    return render_template('report_dashboard.html')


@app.route('/pdf_viewer')
def pdf_viewer():
    # Replace 'your_pdf.pdf' with the actual path or URL to your PDF file
    pdf_url = "#"
    return render_template('pdf_viewer.html', pdf_url=pdf_url)

#set up
@app.route('/setup')
@login_required
def setup():
    return render_template('setup.html')



if __name__ == '__main__':
    app.run(debug= True)

