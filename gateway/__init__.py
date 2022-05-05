import os
from dotenv import load_dotenv
import braintree

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment=braintree.Environment.Sandbox,
        merchant_id='xdf6rv8vjryxz9ng',
        public_key='mfvzxxhc5krzmqps',
        private_key='9a1b2096763b7e280529e4b8e4c9f0eb'
    )
)

def generate_client_token():
    return gateway.client_token.generate()

def transact(options):
    return gateway.transaction.sale(options)

def find_transaction(id):
    return gateway.transaction.find(id)

def get_plans():
    return gateway.plan.all()

def create_customer(costumer):
    return gateway.customer.create(costumer)

def create_subscriptions(options):
    return gateway.subscription.create(options)