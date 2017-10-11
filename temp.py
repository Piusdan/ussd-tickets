#!/usr/bin/python
import sys
import MySQLdb
from sqlalchemy import create_engine

try:
    #  conn = MySQLdb.connect (
    #   host = "piusdan.mysql.pythonanywhere-services.com",
    #   user = "piusdan",
    #   passwd = "valhalla",
    #   db = "valhala")
    engine = create_engine('mysql+mysqldb://{username}:{password}@{host}/{db}'.
                           format(
                               username="piusdan",
                               password="vallhalla",
                               host="piusdan.mysql.pythonanywhere-services.com",
                               db="valhalla"
                           ))
    conn = engine.connect()
    print 'connexted'

except Exception as exc:
    print "Error: {exc}".format(exc=exc)
    sys.exit(1)

print "connected to the database"
