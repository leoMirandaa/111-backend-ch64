from flask import Flask, jsonify, request
import sqlite3
# from http import HTTPStatus

app = Flask(__name__)

DB_NAME = "budget_manager.db"


def init_db():
    conn = sqlite3.connect(DB_NAME) # Opens a connection to the D.B. file named 'budget_manager.db'
    cursor = conn.cursor() # Creates a cursor/tool that lets us send commands(SELECT,INSERT...) to the DB

    cursor.execute("""
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
      )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT NOT NULL,
            amount INT NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit() # Save changes to the D.B.
    conn.close() # Close the connection to the D.B.


# @app.route('/api/health', methods=["GET"])
# def health_check():
#   return jsonify({
#     "status": "OK"
#   }), HTTPStatus.OK

@app.get('/api/health')
def health_check():
    return jsonify({
      "status": "OK"  
    }), 200


@app.post('/api/register')
def register():
    new_user = request.get_json()
    print(new_user)
    print(new_user["username"])
    print(new_user["password"])

    username = new_user["username"]
    password = new_user["password"]

    conn = sqlite3.connect(DB_NAME) # Opens a connection to the D.B. file named 'budget_manager.db'
    cursor = conn.cursor() # Creates a cursor/tool that lets us send commands(SELECT,INSERT...) to the DB
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password)) # Execute SQL statement
    conn.commit() # Save changes to the D.B.
    conn.close() # Close the connection to the D.B

    return jsonify({
      "success": True,
      "message": "User registered successfully"
    }), 201


@app.get('/api/users')
def get_users():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allows columns values to be retrieved by name, row["username"]
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall() # Retrieves all rows from the result of the query.
    print(rows)
    conn.close()

    users = []
    for row in rows:
        user = {
            "id": row["id"],
            "username": row["username"],
            "password": row["password"]
        }
        users.append(user)


    return jsonify({
        "success": True,
        "message": "Users retrieved successfully",
        "data": users
    }), 200


# Path parameters
# http://127.0.0.1:5000/api/users/3
@app.get('/api/users/<int:user_id>')
def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    #print(row)

    if not row:
        conn.close()

        return jsonify({
            "success": False,
            "message": "User not found"    
        }), 404
    else:
        user_information = {
            "id": row["id"], 
            "username": row["username"] 
        }
        
        conn.close()

        return jsonify({
            "success": True,
            "message": "User retrieved successfully",
            "data": user_information
        }), 200


# update user
@app.put('/api/users/<int:user_id>')
def update_user(user_id):
    updated_user = request.get_json()
    username = updated_user["username"]
    password = updated_user["password"]
    print(updated_user)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * from users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    cursor.execute("UPDATE users SET username=?, password=? WHERE id=?", (username, password, user_id))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "User updated successfully",
    }), 200


# delete user
@app.delete('/api/users/<int:user_id>')
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id=?",(user_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404 

    cursor.execute("DELETE FROM users WHERE id=?",(user_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "User deleted successfully"
    }), 200


# ------------ Expenses ------------
@app.post('/api/expenses')
def create_expense():
    new_expense = request.get_json()
    print(new_expense)

    title = new_expense["title"]
    description = new_expense["description"]
    amount = new_expense["amount"]
    date = new_expense["date"]
    category = new_expense["category"]
    user_id = new_expense["user_id"]

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # make rows behave like dicts
    cursor = conn.cursor()

    cursor.execute(""" 
                   INSERT INTO expenses (title, description, amount, date, category, user_id) 
                   VALUES (?, ?, ?, ?, ?, ?)""", 
                   (title, description, amount, date, category, user_id))
    conn.commit()
    conn.close()

    return jsonify({
        "success": False,
        "message": "Expense created successfully"
    }), 201


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
