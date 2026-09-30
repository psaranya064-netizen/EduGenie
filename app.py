from flask import Flask, render_template,jsonify, request
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
import sqlite3

app = Flask(__name__)


# ---------------- DATABASE ----------------

def get_db_connection():
    connection = sqlite3.connect("edugenie.db")
    connection.row_factory = sqlite3.Row
    return connection


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/materials")
def materials():
    return render_template("materials.html")

@app.route("/materials/python")
def python_material():
    return """
    <h1>🐍 Python Programming</h1>
    <p>Python fundamentals, variables, conditions, loops, functions and lists.</p>
    """
@app.route("/materials/sql")
def sql_material():
    return """
    <h1>💾 SQL & Database</h1>
    <p>Learn SQL queries, tables, database operations and CRUD concepts.</p>
    """
@app.route("/materials/ai")
def ai_material():
    return """
    <h1>🤖 Artificial Intelligence</h1>
    <p>Explore AI fundamentals, machine learning and intelligent systems.</p>
    """
@app.route("/materials/web")
def web_material():
    return """
    <h1>🌐 Web Development</h1>
    <p>Learn HTML, CSS and JavaScript to build modern websites.</p>
    """
@app.route("/materials/cloud")
def cloud_material():
    return """
    <h1>☁️ Cloud Computing</h1>
    <p>Understand cloud concepts, services and modern cloud platforms.</p>
    """
@app.route("/materials/cyber")
def cyber_material():
    return """
    <h1>🔐 Cyber Security</h1>
    <p>Learn basic security concepts, threats and protection techniques.</p>
    """
@app.route("/ai-tutor")
def ai_tutor():
    return render_template("ai-tutor.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "message": "Please fill all fields"
        })

    connection = get_db_connection()

    try:

        connection.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Registration successful! 🎉"
        })

    except sqlite3.IntegrityError:

        return jsonify({
            "success": False,
            "message": "Email already registered"
        })

    finally:

        connection.close()


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    connection = get_db_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, password)
    ).fetchone()

    connection.close()

    if user:

        return jsonify({
            "success": True,
            "message": "Login successful! 🎓",
            "name": user["name"]
        })

    return jsonify({
        "success": False,
        "message": "Invalid email or password"
    })


# ---------------- RUN SERVER ----------------
# ---------------- SAVE QUIZ SCORE ----------------

@app.route("/save-score", methods=["POST"])
def save_score():

    data = request.get_json()

    user_id = data.get("user_id")
    score = data.get("score")
    total_questions = data.get("total_questions")

    if score is None or total_questions is None:
        return jsonify({
            "success": False,
            "message": "Score information is missing"
        })

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO quiz_scores
        (user_id, score, total_questions)
        VALUES (?, ?, ?)
        """,
        (user_id, score, total_questions)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Quiz score saved successfully! 🎉"
    })
# ---------------- GET PROGRESS ----------------

@app.route("/progress/<int:user_id>", methods=["GET"])
def get_progress(user_id):

    connection = get_db_connection()

    scores = connection.execute(
        """
        SELECT score, total_questions
        FROM quiz_scores
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    ).fetchall()

    connection.close()

    total_quizzes = len(scores)

    if total_quizzes == 0:
        return jsonify({
            "success": True,
            "total_quizzes": 0,
            "average_score": 0,
            "latest_score": 0
        })

    percentages = []

    for row in scores:
        percentage = (row["score"] / row["total_questions"]) * 100
        percentages.append(percentage)

    average_score = round(sum(percentages) / len(percentages))
    latest_score = round(percentages[0])

    return jsonify({
        "success": True,
        "total_quizzes": total_quizzes,
        "average_score": average_score,
        "latest_score": latest_score
    })

@app.route("/api/ai-tutor", methods=["POST"])
def ai_tutor_api():

    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "success": False,
            "message": "Please enter a question."
        }), 400

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=question
            )

            return jsonify({
                "success": True,
                "answer": response.text
            })

        except Exception as e:

            print("Gemini attempt", attempt + 1, "failed:", e)

            if attempt == 2:
                return jsonify({
                    "success": False,
                    "message": "Gemini is temporarily busy. Please try again in a moment."
                }), 503

@app.route("/subjects")
def subjects():
    return render_template("subjects.html")

@app.route("/python")
def python():
    return render_template("python.html")

@app.route("/java")
def java():
    return render_template("java.html")

@app.route("/sql")
def sql():
    return render_template("sql.html")

@app.route("/html-css")
def html_css():
    return render_template("html-css.html")

@app.route("/javascript")
def javascript():
    return render_template("javascript.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

@app.route("/progress")
def progress():
    return render_template("progress.html")





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)