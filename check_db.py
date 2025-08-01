import sqlite3

conn = sqlite3.connect('database/mess_menu.db')
cursor = conn.cursor()

print("Users in database:")
cursor.execute('SELECT username, full_name, is_admin FROM users')
for row in cursor.fetchall():
    print(f"  {row}")

print("\nTesting password verification:")
from werkzeug.security import check_password_hash

cursor.execute('SELECT username, password_hash FROM users WHERE username = ?', ('student',))
user = cursor.fetchone()
if user:
    username, password_hash = user
    print(f"User: {username}")
    print(f"Password hash: {password_hash[:50]}...")
    print(f"Password 'student123' matches: {check_password_hash(password_hash, 'student123')}")
else:
    print("Student user not found!")

conn.close()
