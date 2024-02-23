from flask import Flask, request,render_template,url_for,redirect,flash,session,g,jsonify,send_from_directory,make_response
from flask_mail import Mail,Message
from datetime import datetime
from app import app,db,models,mail,content_math
from sqlalchemy import func,and_,or_
from app.forms import LoginForm,UserMaintenanceForm,ForgotPassword,PasswordReset
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import sessionmaker
from app.dbops import create_query_new, update_entry,data_extractor,update_customer_csv
from flask_migrate import Migrate
from flask_login import LoginManager, login_required,login_user,current_user,logout_user
import pandas  as pd
import random
import subprocess

current_year = datetime.today().year 


migrate=Migrate(app,db)
login_manager=LoginManager(app)
login_manager.login_view="login"

#DATABASE SESSIONS_________________________________________________________________________________________________________________________________________________
# creates unique sessions for each process

with app.app_context():
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
@app.route('/learn/elementary',methods=['GET','POST'])
def elementary():
    dbsession = get_db_session()
    return render_template('learn_elementary.html', current_user=current_user,existing=None)

@app.route('/learn/intermediate',methods=['GET','POST'])
def intermediate():
    dbsession = get_db_session()
    return render_template('learn_intermediate.html', current_user=current_user,existing=None)

@app.route('/learn/advanced',methods=['GET','POST'])
def advanced():
    dbsession = get_db_session()
    return render_template('learn_advanced.html', current_user=current_user,existing=None)

@app.route('/contact',methods=['GET','POST'])
def contact():
    dbsession = get_db_session()
    return render_template('contact.html', current_user=current_user,existing=None)


@app.route('/display', methods=['GET', 'POST'])
def display():
    place_values = None
    num=None
    if request.method == 'POST':
        number = float(request.form['number'])
        place_values = content_math.get_place_values(number)
        num = '{:,.4f}'.format(number)

    return render_template('index.html', place_values=place_values,num=num)

@app.route('/display/addition', methods=['GET', 'POST'])
def display_add():
    try:
        streamlit_output = subprocess.run(['streamlit', 'run', 'animath.py'], capture_output=True)
        return render_template('index.html', streamlit_output=streamlit_output.stdout.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        error_message = f"Error running Streamlit app: {e}"
        return render_template('index.html', error=error_message)
    
@app.route('/streamlit')
def streamlit():
    streamlit.set_page_config(page_title="My Streamlit App")
    streamlit.write("Hello, world!")