from flask import url_for
from base64 import b64encode

import json
import datetime
import unittest
from app import create_app, db
from app.model import User, Role, Event


class APITestEvent(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()
        admin = User(password='cat', phone_number='254703554404')
        user = User(password='cat', phone_number='254703554403')
        event = Event(description="eating party")
        event.organiser = admin
        db.session.add(event)
        db.session.add(admin)
        db.session.add(user)
        db.session.commit()
        self.event_id = Event.query.first().id
        self.event_url = url_for('api.get_event', id=self.event_id, _external=True)
        self.admin_headers = self.get_api_headers('254703554404', 'cat')
        self.user_headers = self.get_api_headers('254703554403', 'cat')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, phone_number, password):
        return {
            'authorization':
                'Basic ' + b64encode(
                    (phone_number + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'Application/json'
        }

    def test_post(self):
        response = self.client.post(
            url_for('api.create_ticket', _external=True),
            headers = self.admin_headers,
            data = json.dumps({
                "type": "Regular",
                "Price": 1000,
                "event_id": self.event_id
            })
        )
        self.assertTrue(response.status_code == 201)

        response = self.client.post(
            url_for('api.create_ticket', _external=True),
            headers = self.admin_headers,
            data = json.dumps({
                "type": "Regular",
                "Price": 1000,
            })
        )
        self.assertTrue(response.status_code == 402)

    def test_get(self):
        response = self.client.post(
            url_for('api.create_ticket', _external=True),
            headers=self.admin_headers,
            data=json.dumps({
                "type": "Regular",
                "Price": 1000,
                "event_id": self.event_id
            })
        )
        ticket_url = url_for('api.get_tickets', event_id=self.event_id, _external=True)

        response = self.client.get(ticket_url,
                                   headers=self.user_headers)
        self.assertTrue(response.status_code == 200)

    def test_delete_ticket(self):
        response = self.client.post(
            url_for('api.create_ticket', _external=True),
            headers=self.admin_headers,
            data=json.dumps({
                "type": "Regular",
                "Price": 1000,
                "event_id": self.event_id
            })
        )
        ticket_url = json.loads(response.data).get("ticket_url")
        response = self.client.delete(ticket_url,
                           headers=self.admin_headers)
        self.assertTrue(response.status_code == 200)
        inadequate_permissions = self.client.delete(ticket_url,
                                      headers=self.user_headers)
        self.assertTrue(inadequate_permissions.status_code == 403)







