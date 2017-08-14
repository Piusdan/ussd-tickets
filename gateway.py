from africastalking.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException

class GatewayException(AfricasTalkingGatewayException):
    pass

class Gateway(AfricasTalkingGateway):
    def __init__(self):
        self.HTTP_RESPONSE_OK = 200
        self.HTTP_RESPONSE_CREATED = 201

        # Turn this on if you run into problems. It will print the raw HTTP response from our server
        self.Debug = False

    def init_app(self, app):
        self.username = app.config['AT_USERNAME']
        self.apiKey = app.config['AT_APIKEY']
        self.environment = app.config.get('AT_ENVIRONMENT') or "production"