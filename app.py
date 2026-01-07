'''
import os
from flask import Flask
from flaskext.mysql import MySQL      # For newer versions of flask-mysql 
# from flask.ext.mysql import MySQL   # For older versions of flask-mysql
app = Flask(__name__)

mysql = MySQL()

mysql_database_host = 'MYSQL_DATABASE_HOST' in os.environ and os.environ['MYSQL_DATABASE_HOST'] or  'localhost'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'db_user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Passw0rd'
app.config['MYSQL_DATABASE_DB'] = 'employee_db'
app.config['MYSQL_DATABASE_HOST'] = mysql_database_host
mysql.init_app(app)

conn = mysql.connect()

cursor = conn.cursor()

@app.route("/")
def main():
    return "Welcome!"

@app.route('/how are you')
def hello():
    return 'I am good, how about you?'

@app.route('/read from database')
def read():
    cursor.execute("SELECT * FROM employees")
    row = cursor.fetchone()
    result = []
    while row is not None:
      result.append(row[0])
      row = cursor.fetchone()

    return ",".join(result)

if __name__ == "__main__":
    app.run()
'''

import os
from flask import Flask, jsonify
import pymysql

app = Flask(__name__)

# MySQL configurations
DB_USER = os.environ.get("MYSQL_DATABASE_USER", "db_user")
DB_PASSWORD = os.environ.get("MYSQL_DATABASE_PASSWORD", "Passw0rd")
DB_NAME = os.environ.get("MYSQL_DATABASE_DB", "employee_db")
DB_HOST = os.environ.get("MYSQL_DATABASE_HOST", "localhost")
DB_PORT = int(os.environ.get("MYSQL_DATABASE_PORT", "3306"))

def get_connection():
    """Create a new connection per request."""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,  # rows as dicts
        autocommit=True,
    )

@app.route("/")
def main():
    return "Welcome!"

@app.route("/how-are-you")
def hello():
    return "I am good, how about you?"

@app.route("/read-from-database")
def read():
    # Example: read first column of employees table and return as CSV
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM employees")
            rows = cursor.fetchall()
        # If employees has a column 'name', adjust accordingly.
        # Here we'll collect the first key in each row dict.
        result = []
        for row in rows:
            # pick first column value deterministically
            first_col = next(iter(row.values())) if row else None
            if first_col is not None:
                result.append(str(first_col))
        return ",".join(result) if result else "No rows found"
    except Exception as e:
        # Return a JSON error for easier debugging
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    # Bind to all interfaces if you want external access
    app.run(host="0.0.0.0", port=5000)
