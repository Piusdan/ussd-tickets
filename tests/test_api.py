from flask import url_for
from base64 import b64encode

import json
import datetime
import unittest
from app import create_app, db
from app.models import User, Role, Event


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

    def test_get_event(self):

        response = self.client.get(self.event_url,
                                   content_type='application/json'
                                   )
        self.assertTrue(response.status_code==200)

    def test_get_events(self):
        response = self.client.get(url_for('api.get_events'),
                                   content_type='application/json')
        self.assertTrue(response.status_code == 200)

    def test_post(self):
        # create a new user
        resp = self.client.post(
            url_for('api.create_event', _external=True),
            headers = self.admin_headers,
            data=json.dumps({'desc': 'working party',
                             'date': str(datetime.datetime.utcnow())}, default=date_handler)
        )
        self.assertTrue(resp.status_code == 201)

    def test_delete(self):
        resp = self.client.delete(self.event_url,
                                  headers = self.admin_headers
                                  )
        self.assertTrue(resp.status_code == 200)
        response = self.client.get(self.event_url)
        self.assertTrue(response.status_code == 404)

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError, 'Object of type %s with value of %s is ' \
                         'not JSON serializable' % (type(obj), repr(obj))