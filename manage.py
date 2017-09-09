#!/usr/bin/env python
"""
Launch script
Creates a shell context for the app
"""
import os
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate

from app import create_app, db
from app.models import User, Role, Event, Ticket, Account, Location, Purchase

app = create_app(os.environ.get('VALHALLA_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)
app.logger.info("initialising app")

COV = None

if os.environ.get('VALHALLA_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


def make_shell_context():
    return dict(app=app, User=User, Role=Role, Ticket=Ticket,
                Event=Event, Account=Account,
                Location=Location, db=db, Purchase=Purchase)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def add_roles():
    from flask_migrate import upgrade
    from app.models import Role

    # migrate db to latest version
    app.logger.info("migrating database to latest state")
    upgrade()

    # create user roles
    app.logger.info("adding user roles")
    Role.insert_roles()


@manager.command
def deploy():
    """Run deployment tasks"""
    from flask_migrate import upgrade
    from app.models import Role, User

    # migrate db to latest version
    upgrade()

    # create user roles
    Role.insert_roles()


@manager.command
def test(coverage=False):
    """
    Run unit tests.
    :return: 
    """
    if coverage and not os.getenv('VALHALLA_COVERAGE'):
        import sys
        os.environ['VALHALLA_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        # basedir = os.path.abspath(os.path.dirname(__file__))
        # covdir = os.path.join(basedir, 'tmp/coverage')
        # COV.html_report('HTML version: file://%s/index.html' % covdir)
        # COV.erase()


if __name__ == "__main__":
    manager.run()
