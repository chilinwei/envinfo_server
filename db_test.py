import datastore

conn = datastore.conn()
cur = conn.cursor()
cur.execute('SELECT VERSION();')
ver = cur.fetchone()
print "Database version: %s"%ver

conn.close()