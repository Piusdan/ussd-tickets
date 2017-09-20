"""Payment options for the app
"""
from cPickle import dumps

from app.ussd.tasks import async_mpesa_checkoutc2b


class Payments():
    """Custom gateway for accepted payments
    """
    _name = 'PAYMENTS'

    def __init__(self, user, amount, metadata):
        self.user = user
        self.amount = amount
        self.metadata = metadata

    def __str__(self):
        return self._name

    def execute(self):
        pass

class Mpesa(Payments):
    _name = "MPESA"

    def execute(self):
        payload = {"user": self.user.to_bin(),
                   "amount": self.amount,
                   "metadata": dumps(self.metadata)
                   }
        async_mpesa_checkoutc2b.apply_async(args=[payload], countdown=5)


payments = {
    "1": Mpesa
}
