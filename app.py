import os
import hashlib
import time
import random
from flask import Flask, render_template, request, url_for, send_file
from reportlab.pdfgen import canvas
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv



app = Flask(__name__)
load_dotenv()
# Load PayU credentials from environment variables
MERCHANT_KEY = os.getenv("PAYU_MERCHANT_KEY")
MERCHANT_SALT = os.getenv("PAYU_MERCHANT_SALT")

# Validate that the credentials are set
if not MERCHANT_KEY or not MERCHANT_SALT:
    raise ValueError("PayU credentials are missing. Set PAYU_MERCHANT_KEY and PAYU_MERCHANT_SALT environment variables.")

PAYU_URL = os.getenv("PAYU_URL", "https://secure.payu.in/_payment")  # Fetch from environment


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/pay')
def pay():
    plan = request.args.get('plan')
    amount = request.args.get('amount')

    txnid = "TXN" + str(int(time.time() * 1000)) + str(random.randint(1000, 9999))  # Unique txnid
    productinfo = plan
    firstname = "John"
    email = "john@example.com"
    phone = "9999999999"

    hash_string = f"{MERCHANT_KEY}|{txnid}|{amount}|{productinfo}|{firstname}|{email}|||||||||||{MERCHANT_SALT}"
    hashh = hashlib.sha512(hash_string.encode()).hexdigest()

    payu_data = {
        "key": MERCHANT_KEY,
        "txnid": txnid,
        "amount": amount,
        "productinfo": productinfo,
        "firstname": firstname,
        "email": email,
        "phone": phone,
        "surl": url_for('success', _external=True),
        "furl": url_for('failure', _external=True),
        "hash": hashh
    }

    return render_template('payment.html', payu_url=PAYU_URL, payu_data=payu_data)

@app.route('/success', methods=['POST'])
def success():
    txnid = request.form.get('txnid', 'Unknown')
    plan = request.form.get('productinfo', 'N/A')
    amount = request.form.get('amount', '0.00')

    pdf_path = f"receipt_{txnid}.pdf"
    generate_pdf(txnid, plan, amount, pdf_path)

    return render_template('payment_success.html', txnid=txnid, plan=plan, amount=amount, pdf_path=pdf_path)

@app.route('/generate_receipt/<txnid>')
def generate_receipt(txnid):
    plan = request.args.get('plan')
    amount = request.args.get('amount')
    pdf_path = f"receipt_{txnid}.pdf"
    generate_pdf(txnid, plan, amount, pdf_path)
    return send_file(pdf_path, as_attachment=True)

def generate_pdf(txnid, plan, amount, pdf_path):
    c = canvas.Canvas(pdf_path)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 800, "Payment Receipt")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f"Transaction ID: {txnid}")
    c.drawString(100, 730, f"Plan: {plan}")
    c.drawString(100, 710, f"Amount Paid: ${amount}")
    
    c.drawString(100, 680, "Thank you for your purchase!")
    c.save()

@app.route('/failure', methods=['POST'])
def failure():
    return "Payment Failed"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8000)))



