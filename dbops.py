from sqlalchemy.orm import class_mapper
import models
import pandas as pd
from datetime import datetime
from flask import flash,request


def create_tables(engine):
    models.Base.metadata.create_all(engine)

def update_entry(update_query,session):
        session.add (update_query)
        session.commit()

def dbtable_get_all(session,table):
    return session.query(table).all()

def dbtable_get_all_filtered(session,table,filters):
    return session.query(table).filter(filters).all()


#BULK UPDATE
def update_customer_csv(existing,session,data):
    for index, row in data.iterrows():
        row = row.apply(lambda x: "" if pd.isna(x) else x)
    # Create a Customer instance for each row
        existing.member_id=row['member_id'],
        existing.lastname=row['lastname'],
        existing.firstname=row['firstname'],
        existing.othernames=row['othenames'],  # Assuming this column is 'othenames' in your DataFrame
        existing.email=row['email'],
        existing.contact=row['contact'],
        existing.dateofbirth=row['dateofbirth'],
        existing.gender=row['gender'],
        existing.identification=row['identification'],
        existing.nationality=row['nationality'],
        existing.country_of_residence=row['country_of_residence'],
        existing.is_admin=row['is_admin'],
        existing.membership_status=row['membership_status'],
        existing.created_at=datetime.utcnow(),  
        existing.updated_at=datetime.utcnow(),
        existing.member_reg_id=row['member_reg_id']
        session.commit()

# ONBOARDING: Updating the customer using the app route.

# READ,CREATE & UPDATE_____________________________________________________________________________________________________________________________________________________________
def create_query_new(table, session, form): 
    try:
        #CONSRUCT QUERY
        attributes = [attr.key for attr in class_mapper(table).iterate_properties]
        update_dict = {}
        for attribute in attributes:
            if attribute in form:
               update_dict[attribute] = form[attribute]
        filters={k: v for k, v in update_dict.items() if v}
        existing_record = session.query(table).filter_by(**filters).first()
        print('attributes created',filters)

        #UPDATE
        if existing_record and form.get('update')is not None:

            for attribute, value in update_dict.items():
                setattr(existing_record, attribute, value)

            existing_record.updated_at = datetime.utcnow()
            flash(f"{table.__tablename__} updated successfully", "success")

        #READ
        elif existing_record and form.get('fetch') is not None:
            return existing_record
        
        #CREATE
        if existing_record and form.get('create')is not None:
            flash("Record exists, Please share request for CHANGE with the Admin") 
        else:
            if form.get('create')is not None:
                new_record = table(**update_dict)
                if table==models.customer:
                    print('new custome')
                    new_record.member_id=models.new_id(form,table,session)
                    print(new_record)
                
                elif table==models.user:
                    print('new user')
                    new_record.user_id=models.generate_user_id(form,table,session)

                elif table==models.creditor:
                    print('new credit',new_record)
                    new_record.credit_id=models.credit_id_gen(session,table)
                    new_record.status='application'
                    new_record.approver='credit Officer'
                    new_record.step=0
                    print('got here')
                    service_fee,processing_fee,interest,repayment,monthly_repayments=crops.product_charges(
                        product_name=new_record.credit_product_name,
                        amount=new_record.credit_amount,
                        months=new_record.repayment_period,
                        session=session,
                        product=models.product)
                    print('got here3')
                    new_record.credit_interest=interest
                    new_record.credit_processing_fee=processing_fee
                    new_record.credit_service_fee=service_fee
                    new_record.repayment_amount=repayment
                    new_record.monthly_repayment=monthly_repayments
                    print('new record',new_record)
                    return new_record

                session.add(new_record)
                flash(f"{table.__tablename__} added successfully", "success")
                
        print('fin')
        session.commit()

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        session.rollback()

#BULK TRANSACTIONS UPDATE___________________________________________________________________________________________________________________________________________________________________
#update transactions from CSV       
def update_transactions_csv(existing,session,data):
    for index, row in data.iterrows():
        row = row.apply(lambda x: None if pd.isna(x) or x == "" else x)
        row['date'] = pd.to_datetime(row['date'], errors='coerce').to_pydatetime()
        #alter_table 
        existing.date=row['date'],
        existing.user_id=row['user_id'],
        existing.narrative_beneficiary=row['narrative_beneficiary'],
        existing.CR_DR=row['CR_DR'],  
        existing.transaction_purpose=row['transaction_purpose'],
        existing.credit_id=row['credit_id'],
        existing.amount=row['amount'],
        existing.created_at=datetime.utcnow(),  
        existing.updated_at=datetime.utcnow(),
        session.commit() 
        
def data_extractor(file):
  data=pd.read_csv(file, encoding='ISO-8859-1')
  if 'date' in data.columns:
      data['date'] = pd.to_datetime(data['date'], format="%d/%m/%Y", errors='coerce')
  return data

