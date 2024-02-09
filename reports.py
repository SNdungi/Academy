from fpdf import FPDF
import PyPDF2
import datetime
import os
from flask import make_response
import base64

# MEMBER STATEMENTS_________________________________________________________________________________________________________________________________________________________
class PDF(FPDF):
    def header(self):
        self.set_font('Times', 'B', 14)
        self.cell(0, 10, 'Customer Statement', 0, 1, 'C')

    def summary_header(self):
        self.set_font('Times', 'B', 11)
        self.cell(0, 7, 'Summary of transacations:', 0, 1, 'L')

    def user_details(self, user_id, member_name, date):
        self.set_font('Times', '', 11)
        self.cell(60, 10, f'Member ID: {user_id}', 0, 0, 'L')
        self.cell(60, 10, f'Member Name: {member_name}', 0, 0, 'C')
        formatted_date = date.strftime('%d/%m/%Y')
        self.cell(0, 10, f'Date: {formatted_date}', 0, 1, 'R')
        self.ln(10)

    def add_transaction(self, date, purpose, credit_id, amount):
        self.set_font('Times', '', 11)
        formatted_date = date.strftime('%d/%m/%Y')
        self.cell(50, 7, str(formatted_date), 0)
        self.cell(60, 7, purpose or '', 0)
        self.cell(40, 7, credit_id or '', 0)
        self.cell(40, 7, "{:,.2f}".format(amount), 0)
        self.ln()

    def summarize (self, purpose, amount):
        self.set_font('Times', 'B', 11)
        self.cell(50, 8, purpose, 1, 0, 'L') 
        self.cell(40, 8, "{:,.2f}".format(amount), 1, 0, 'L')
        self.ln()

    def end_of_report (self):
        self.set_font('Times', '', 11)
        self.cell(0, 10, '_______End of Statement_______', 0, 1, 'C')
#Personal Statement
def generate_pdf_statement(summaries,transactions, user_details, filename):
    pdf = PDF()
    pdf.add_page()

    letterhead_path = 'static\hsacco.png' 
    if letterhead_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
        pdf.image(letterhead_path, x=10, y=10, w=50)
    else:
        converted_path = 'path/to/your/letterhead.png'
        convert_command = f'inkscape -z -e {converted_path} {letterhead_path}'
        os.system(convert_command)
        pdf.image(converted_path, x=10, y=10, w=50)
    pdf.ln(10)

    #title
    pdf.set_font('Times', 'B', 12)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())


    pdf.user_details(user_details.user_id, user_details.narrative_beneficiary, user_details.date)

    pdf.set_font('Times', 'B', 12)

  
    pdf.set_fill_color(220, 220, 220)  
    pdf.cell(50, 5, 'Date', 0, 0, 'L', 1)  # Add background and center align
    pdf.cell(60, 5, 'Purpose of Transaction', 0, 0, 'L', 1)  # Add background and center align
    pdf.cell(40, 5, 'credit ID', 0, 0, 'L', 1)  # Add background and center align
    pdf.cell(40, 5, 'Amount', 0, 1, 'L', 1)  # Add background, center align, and move to the next line

    # Reset subsequent cells
    pdf.set_fill_color(255, 255, 255)

    #transactions
    pdf.set_font('Times', '', 12)
    for transaction in transactions:
        pdf.add_transaction(transaction.date, transaction.transaction_purpose, transaction.credit_id, transaction.amount)

   #add space
    pdf.ln(10)
    pdf.summary_header()
    for summary in summaries:
        pdf.summarize(summary.purpose,summary.amount)

    pdf.ln(10)
    pdf.end_of_report()
    return pdf

class UserDetails:
    def __init__(self, user_id, narrative_beneficiary,date):
        self.user_id = user_id
        self.narrative_beneficiary = narrative_beneficiary
        self.date = date

class Transaction:
    def __init__(self, date, transaction_purpose, credit_id, amount):
        self.date = date
        self.transaction_purpose = transaction_purpose
        self.credit_id = credit_id
        self.amount = amount

class Summary:
    def __init__(self,purpose, amount):
        self.purpose = purpose
        self.amount = amount

# FINANCIAL REPORTS______________________________________________________________________________________________________________________________________________________________

def fill_pdf_form(input_pdf_path):
    # Open the existing PDF
    with open(input_pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        writer = PyPDF2.PdfWriter()

        page = reader.pages[0]
        fields = reader.get_fields()

        writer.add_page(page)

        writer.update_page_form_field_values(
            writer.pages[0], {
                '201': 2222, 
                '202': 3333, 
                '203': 500, 
                '204': '', 
                '205': '0', 
                '206': '', 
                '207': '', 
                '208': '', 
                '209': '', 
                '210': '', 
                '211': '0', 
                '212': '', 
                '213': '', 
                '214': '', 
                '215': '', 
                '216': '', 
                '217': '', 
                '218': '', 
                '219': '', 
                '220': '0', 
                '221': '', 
                '222': '', 
                '223': '', 
                '224': '', 
                '225': '', 
                '226': '0', 
                '227': '', 
                '228': '', 
                '229': '', 
                '230': '', 
                '231': '', 
                '232': '0', 
                '233': '', 
                '234': '', 
                '235': '0', 
                '236': '', 
                '237': '', 
                '238': '', 
                '239': '', 
                '240': '', 
                '241': '', 
                '242': '', 
                '243': '0', 
                '244': '', 
                '245': '0', 
                '246': '0', 
                '247': '0',
                '248': '', 
                '249': '', 
                '250': '', 
                '251': '0', 
                '252': '', 
                '253': '0', 
                '254': '', 
                '255': '', 
                '256': '', 
                '257': '', 
                '258': '0', 
                '259': ''
                }
        )
        # write "output" to PyPDF2-output.pdf
        with open('static\IncomeStatement.pdf', "wb") as output_stream:
            writer.write(output_stream)
        return fields
# Example usage
input_pdf ='static\IncomeStatement.pdf'
fill_pdf_form(input_pdf)
# DASHBOARD______________________________________________________________________________________________________________________________________________________________________________