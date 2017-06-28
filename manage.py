#!/usr/bin/env python
"""
Launch script
Creates a shell context for the app
"""
import os
from app import create_app
from app.models import User, Role, Event, Ticket
from flask_script import Manager, Shell
from flask_migrate import  Migrate, MigrateCommand
from app import db

app = create_app(os.getenv('VALHALLA_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, User=User, Role=Role, Ticket=Ticket, Event=Event)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """
    Run unit tests.
    :return: 
    """
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    manager.run()
