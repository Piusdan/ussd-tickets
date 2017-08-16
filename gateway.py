from africastalking.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException

class GatewayException(AfricasTalkingGatewayException):
    pass

class Gateway(AfricasTalkingGateway):
    def __init__(self):
        pass
    
    def init_app(self, app):
        # this initialises an AfricasTalking Gateway instanse similar to calling
        # africastalking.gateway(username, apikey, environment)
        # this enables us to initialise one gateway to use throughout the app
        self.username    = 'sandbox'
        self.apiKey      = 'ba45842273aed6928fe00afcaddd697755535b7d3d9ad8ec4986727543ff7ea5'
        self.environment = 'sandbox'
 
        self.HTTP_RESPONSE_OK       = 200
        self.HTTP_RESPONSE_CREATED  = 201
 
        # Turn this on if you run into problems. It will print the raw HTTP response from our server
        self.Debug= False