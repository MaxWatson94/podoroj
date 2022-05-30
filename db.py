import sqlite3


conn = sqlite3.connect('db/users.db')
cur = conn.cursor()


# cur.execute("""CREATE TABLE IF NOT EXISTS users(
#    userid INT PRIMARY KEY,
#    username TEXT,
#    carNumber TEXT,
#    lastBalance INT);
# """)
# conn.commit()


# cur.execute("SELECT carNumber FROM users WHERE userid = 838719023;")
# one_result = cur.fetchone()
# print(one_result)


cur.execute("SELECT userid FROM users")
one_result = cur.fetchone()
print(one_result)


