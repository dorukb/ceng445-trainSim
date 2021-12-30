'''
import sqlite3

db = sqlite3.connect('./auth-demo.db')
db.execute('CREATE TABLE users (username TEXT PRIMARY KEY, password TEXT)')
db.execute('INSERT INTO users (username, password) VALUES (?, ?), (?, ?)',
           ('huey', 'meow', 'mickey', 'woof'))


def authorizer(action, arg1, arg2, db_name, trigger_name):
    if action == SQLITE_DELETE and arg1 == 'users':
        return SQLITE_DENY  # 1
    elif action == SQLITE_READ and arg1 == 'users' and arg2 == 'password':
        return SQLITE_IGNORE  # 2
    return SQLITE_OK  # 0

db.set_authorizer(authorizer)

cursor = db.execute('SELECT * FROM users;')
for username, password in cursor.fetchall():
    print(username, password)  # Password will be None (NULL).

# ('huey', None)
# ('mickey', None)

db.execute('DELETE FROM users WHERE username = ?', ('huey',))


# Triggers an exception:
# ------------------------------------------------------
# DatabaseError        Traceback (most recent call last)
# <ipython-input-10-04b65dd3e206> in <module>()
#       1 # Trying to delete a user will result in an error.
# ----> 2 db.execute('DELETE FROM users WHERE username '...)
#
# DatabaseError: not authorized
'''
import sqlite3


def create_table():
    query = "DROP TABLE IF EXISTS login"
    cursor.execute(query)
    conn.commit()
    
    query = "CREATE TABLE login(Username VARCHAR UNIQUE, Password VARCHAR)"
    cursor.execute(query)
    conn.commit()

def enter(username, password):
    query = "INSERT INTO login (Username, Password) VALUES (?, ?)"
    cursor.execute(query, (username, password))
    conn.commit()

def check(username, password):
    query = 'SELECT * FROM login WHERE Username = ? AND Password = ?'
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    conn.commit()
    print('[DEBUG][check] result:', result)
    return result

def loginlol():
    answer = input("Login (Y/N): ")

    if answer.lower() == "y":
        username = input("Username: ")
        password = input("Password: ")
        if check(username, password):
            print("Username correct!")
            print("Password correct!")
            print("Logging in...")
        else:
            print("Something wrong")

# --- main ---

conn = sqlite3.connect("pooptest123.db")
cursor = conn.cursor()

create_table()

Username = input("Create username: ")
Password = input("Create password: ")

enter(Username, Password)

#check(Username, Password)

loginlol()

cursor.close()
conn.close()