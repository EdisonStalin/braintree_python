from this import s
from unittest import result
from flask import Flask, redirect, url_for, render_template, request, flash

import os
from os.path import join, dirname
from dotenv import load_dotenv
import braintree
from gateway import generate_client_token, transact, find_transaction, get_plans, create_customer, create_subscriptions

load_dotenv()

app = Flask(__name__)
#app.secret_key
key = os.urandom(24)
app.secret_key = key

PORT = int(os.environ.get('PORT', 4567))

TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('register'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        firstname = request.form.get("first_name")
        lastname = request.form.get("last_name")
        company = request.form.get("company")
        email = request.form.get("email")
        phone = request.form.get("phone")

        result = create_customer({
                "id": "customer_1",
                "first_name": firstname,
                "last_name": lastname,
                "company": company,
                "email": email,
                "phone": phone,
                'payment_method_nonce': 'fake-valid-nonce'
            })

        #create subscriptions
        token = result.customer.payment_methods[0].token
        print('create subscription', token)

        create_subscriptions({
            "payment_method_token": token,
            "plan_id": "q22g"
            })

        return redirect(url_for('new_checkout'))
    else:
        return render_template('checkouts/register.html')


    
@app.route('/checkouts/new', methods=['GET'])
def new_checkout():
    client_token = generate_client_token()
    plans = get_plans()
    return render_template('checkouts/new.html', plans=plans, client_token=client_token )


@app.route('/checkouts/<transaction_id>', methods=['GET'])
def show_checkout(transaction_id):
    transaction = find_transaction(transaction_id)
    
    
    result = {}
    if transaction.status in TRANSACTION_SUCCESS_STATUSES:
        result = {
            'header': 'Sweet Success!',
            'icon': 'success',
            'message': 'Your test transaction has been successfully processed. See the Braintree API response and try again.'
        }

    else:
        result = {
            'header': 'Transaction Failed',
            'icon': 'fail',
            'message': 'Your test transaction has a status of ' + transaction.status + '. See the Braintree API response and try again.'
        }

    return render_template('checkouts/show.html', transaction=transaction, result=result)

@app.route('/checkouts', methods=['POST'])
def create_checkout():
    payment_method_nonce = request.form['payment_method_nonce']
    result = transact({
        'customer_id': "customer_1",
        'amount': request.form['amount'],
        'payment_method_nonce': payment_method_nonce,
        'options': {
            "submit_for_settlement": True,
            "store_in_vault_on_success": True,
        }
    })

    print(result)

    if result.is_success or result.transaction:
        return redirect(url_for('show_checkout',transaction_id=result.transaction.id))
    else:
        for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
        return redirect(url_for('new_checkout'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
