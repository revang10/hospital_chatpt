from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# MySQL DB connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="hospital_db"
)
cursor = db.cursor(dictionary=True)

# Serve the index.html when visiting the root URL
@app.route('/')
def home():
    return render_template('index.html')

# Chat route for handling queries
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').lower()

    if "cardiology" in user_message:
        query = "SELECT * FROM patient_visits WHERE department = 'Cardiology';"
    elif "female" in user_message:
        query = "SELECT * FROM patient_visits WHERE gender = 'Female';"
    elif "bill over" in user_message:
        query = "SELECT * FROM patient_visits WHERE total_bill > 4000;"
    else:
        return jsonify({"result": "Sorry, I don't understand that query yet."})

    cursor.execute(query)
    rows = cursor.fetchall()

    if not rows:
        return jsonify({"result": "No records found."})

    return jsonify({"result": rows})

if __name__ == '__main__':
    app.run(debug=True)
