import sqlite3
c = sqlite3.connect('mhw.db').cursor()
c.execute('PRAGMA table_info(decoration)')
for r in c.fetchall():
    print(r[1])
