import unittest
from app import create_app, db
from app.models import User, Event, Ticket

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_can_create_event(self):
        e = Event(description="Eat")
        self.assertTrue(e)

    def test_event_has_organiser(self):
        u = User(email="joe@example.com", password='cat')
        e = Event(description='Eat')
        e.organiser = u
        self.assertTrue(e.organiser_id == u.id)

    def test_event_has_tickets(self):
        u = User(email="joe@example.com", password='cat')
        e = Event(description='Eat')
        e.organiser = u
        ticket = Ticket()
        ticket.event = e
        self.assertTrue(ticket.event_id == e.id)

    def test_ticket_has_holder(self):
        u = User(email="joe@example.com", password='cat')
        ticket = Ticket()
        u.ticket = ticket
        self.assertTrue(u.ticket_id == ticket.id)

    def test_ticket_has_many_holders(self):
        ticket = Ticket()
        u = User(email="joe@example.com", password='cat', ticket=ticket)
        u2 = User(email="jo@example.com", password='cat', ticket=ticket)
        u3 = User(email="oe@example.com", password='cat', ticket=ticket)

        self.assertTrue(u.ticket_id == ticket.id and u2.ticket_id == ticket.id and u3.ticket_id == ticket.id)

