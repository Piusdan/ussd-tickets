import os, logging
from africastalking.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException


class GatewayException(AfricasTalkingGatewayException):
    pass


class Gateway(AfricasTalkingGateway):
    def __init__(self):
        logging.info("Initialising Africastalking gateway")

    def init_app(self, app):
        # this initialises an AfricasTalking Gateway instanse similar to calling
        # africastalking.gateway(username, apikey, environment)
        # this enables us to initialise one gateway to use throughout the app

        self.username = os.environ.get('AT_USERNAME') or 'sandbox'
        self.apiKey = '61d44b58e63275291fb25de10498551e9325ebe1bae75a33d80ec9dbaf26dcc4'
        self.environment = os.environ.get('AT_ENVIRONMENT') or 'sandbox'
        self.HTTP_RESPONSE_OK = 200
        self.HTTP_RESPONSE_CREATED = 201
 
        # Turn this on if you run into problems. It will print the raw HTTP response from our server
        self.Debug= False
