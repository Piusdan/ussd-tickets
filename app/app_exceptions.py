class SignupError(ValueError):
    def __init__(self, *args):
        self.message = args

class GeocoderError(Exception):
    pass
