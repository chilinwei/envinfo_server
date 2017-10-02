import ConfigParser
import mysql.connector as mariadb

conf = ConfigParser.ConfigParser()
conf.read('settings.ini')

_host = conf.get('database','host')
_database = conf.get('database','database')
_user = conf.get('database','user')
_password = conf.get('database','password')

#print(_host,_database,_user,_password)

def conn():
    conn = mariadb.connect(host=_host,user=_user, password=_password, database=_database)
    return conn