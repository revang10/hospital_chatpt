from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import requests
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    column_mapping = {
    "patient name": "patient_name",
    "name": "patient_name",
    "bill": "total_bill",
    "amount": "total_bill",
    "charges": "total_bill",
    "visit date": "visit_date",
    "department": "department",
    "gender": "gender",
    "age": "age",
    }

    for word, col in column_mapping.items():
        if word.lower() in user_message.lower():
            user_message = user_message.lower().replace(word.lower(), col)



    try:
        # Ask Gemini via OpenRouter
        prompt = f"""
            You are a SQL generator for a MySQL database.

            Table: patient_visits
            Columns:
            id
            name
            age
            gender
            department
            diagnosis
            visit_date
            total_bill

            If the user uses different terms for a column, map them to the correct one:
            Examples:
            - "patient name" or "name" → patient_name
            - "bill", "amount", or "charges" → total_bill
            - "visit date" → visit_date

            Generate a SQL SELECT query that matches the user request exactly.
            Only return the SQL code with no extra text.

            User request: {user_message}
            """


        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.0-flash-exp:free",  # use a supported Gemini model
                "messages": [
                    {"role": "system", "content": "You are an expert SQL generator for MySQL."},
                    {"role": "user", "content": prompt}
                ]
            }
        )

        if response.status_code != 200:
            return jsonify({"result": f"Error from OpenRouter: {response.text}"}), 500

        sql_query = response.json()["choices"][0]["message"]["content"].strip()

        # Clean any accidental code fences
        if sql_query.startswith("```"):
            sql_query = sql_query.strip("`")  # remove all backticks
        sql_query = sql_query.replace("sql", "", 1).strip()

        # Execute SQL
        cursor.execute(sql_query)
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"result": "No records found."})

        return jsonify({"result": rows})

    except Exception as e:
        return jsonify({"result": f"Error generating SQL query: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
