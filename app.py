from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
import os

app = Flask(__name__)
db_url = os.environ.get("DATABASE_URL", "").strip()
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
# Vercel's deployed filesystem is not a persistent writable disk.
# Use an external DATABASE_URL (recommended for production). If none is
# configured, use /tmp only as a temporary fallback so the function can boot.
sqlite_fallback = "/tmp/codequest.db" if os.environ.get("VERCEL") else "codequest.db"
app.config["SQLALCHEMY_DATABASE_URI"] = db_url or f"sqlite:///{sqlite_fallback}"

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-codequest-change-me")
app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///codequest.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak = db.Column(db.Integer, default=0)
    last_active = db.Column(db.String(20), nullable=True)
    badges = db.relationship("UserBadge", backref="user", lazy=True, cascade="all, delete-orphan")
    progress = db.relationship("Progress", backref="user", lazy=True, cascade="all, delete-orphan")

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    icon = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(30), default="Beginner")
    xp_reward = db.Column(db.Integer, default=500)
    order_num = db.Column(db.Integer, unique=True, nullable=False)
    challenges = db.relationship("Challenge", backref="lesson", lazy=True, cascade="all, delete-orphan")

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lesson.id"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    challenge_type = db.Column(db.String(30), default="mcq")
    options_json = db.Column(db.Text, nullable=True)
    answer = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    hint = db.Column(db.Text, nullable=False)
    xp_reward = db.Column(db.Integer, default=50)
    difficulty = db.Column(db.String(20), default="Easy")

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lesson.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    attempts = db.Column(db.Integer, default=0)
    lesson = db.relationship("Lesson")

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(10), nullable=False)

class UserBadge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badge.id"), nullable=False)
    badge = db.relationship("Badge")

def current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None

def update_level(user):
    user.level = min(8, max(1, user.xp // 500 + 1))

def award_badge(user, name):
    badge = Badge.query.filter_by(name=name).first()
    if not badge or UserBadge.query.filter_by(user_id=user.id, badge_id=badge.id).first():
        return False
    db.session.add(UserBadge(user_id=user.id, badge_id=badge.id))
    return True

@app.context_processor
def inject_user():
    return {"current_user": current_user()}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        if not username or not email or len(password) < 6:
            flash("Please enter valid details. Password must be at least 6 characters.", "error")
            return redirect(url_for("register"))
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists.", "error")
            return redirect(url_for("register"))
        user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        award_badge(user, "First Step")
        db.session.commit()
        session["user_id"] = user.id
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"].strip().lower()).first()
        if user and check_password_hash(user.password_hash, request.form["password"]):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    lessons = Lesson.query.order_by(Lesson.order_num).all()
    progress = {p.lesson_id: p for p in user.progress}
    completed = sum(1 for p in progress.values() if p.completed)
    return render_template("dashboard.html", user=user, lessons=lessons, progress=progress, completed=completed)

@app.route("/map")
def learning_map():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    lessons = Lesson.query.order_by(Lesson.order_num).all()
    progress = {p.lesson_id: p for p in user.progress}
    return render_template("map.html", lessons=lessons, progress=progress)

@app.route("/lesson/<int:lesson_id>")
def lesson(lesson_id):
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    lesson_obj = db.session.get(Lesson, lesson_id)
    if not lesson_obj:
        return "Lesson not found", 404
    if lesson_obj.order_num > 1:
        previous = Lesson.query.filter_by(order_num=lesson_obj.order_num - 1).first()
        prev_progress = Progress.query.filter_by(user_id=user.id, lesson_id=previous.id).first()
        if not prev_progress or not prev_progress.completed:
            flash("Complete the previous world to unlock this one.", "error")
            return redirect(url_for("learning_map"))
    challenges = lesson_obj.challenges
    return render_template("lesson.html", lesson=lesson_obj, challenges=challenges)

@app.route("/challenge/<int:challenge_id>", methods=["GET", "POST"])
def challenge(challenge_id):
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    ch = db.session.get(Challenge, challenge_id)
    if not ch:
        return "Challenge not found", 404
    progress = Progress.query.filter_by(user_id=user.id, lesson_id=ch.lesson_id).first()
    if not progress:
        progress = Progress(user_id=user.id, lesson_id=ch.lesson_id)
        db.session.add(progress)
        db.session.commit()
    result = None
    if request.method == "POST":
        submitted = request.form.get("answer", "").strip()
        progress.attempts += 1
        correct = submitted.lower() == ch.answer.lower()
        if correct:
            progress.score += ch.xp_reward
            user.xp += ch.xp_reward
            update_level(user)
            result = {"correct": True, "message": ch.explanation, "xp": ch.xp_reward}
            award_badge(user, "Bug Hunter" if ch.challenge_type == "debug" else "First Step")
            if progress.score >= sum(c.xp_reward for c in ch.lesson.challenges):
                progress.completed = True
                user.xp += ch.lesson.xp_reward
                update_level(user)
        else:
            result = {"correct": False, "message": "Not quite. Use the hint and try again.", "xp": 0}
        db.session.commit()
    options = []
    if ch.options_json:
        import json
        options = json.loads(ch.options_json)
    return render_template("challenge.html", challenge=ch, options=options, result=result, progress=progress)

@app.route("/leaderboard")
def leaderboard():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    users = User.query.order_by(User.xp.desc()).limit(20).all()
    return render_template("leaderboard.html", users=users)

@app.route("/profile")
def profile():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    badges = UserBadge.query.filter_by(user_id=user.id).all()
    completed = Progress.query.filter_by(user_id=user.id, completed=True).count()
    return render_template("profile.html", user=user, badges=badges, completed=completed)

@app.get("/api/lessons")
def api_lessons():
    return jsonify([{"id": l.id, "title": l.title, "order": l.order_num, "xp": l.xp_reward} for l in Lesson.query.order_by(Lesson.order_num)])

@app.post("/api/challenges/<int:challenge_id>/submit")
def api_submit(challenge_id):
    if not current_user():
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"message": "Use the web challenge page for the MVP submission flow."})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)


@app.post("/api/ai-tutor")
def ai_tutor():
    if not session.get("user_id"):
        return jsonify({"error":"Unauthorized"}),401
    data=request.get_json(silent=True) or {}
    question=(data.get("question") or "").strip()
    code=(data.get("code") or "").strip()
    key=os.environ.get("OPENAI_API_KEY","").strip()
    if key:
        try:
            from openai import OpenAI
            client=OpenAI(api_key=key)
            r=client.responses.create(
                model=os.environ.get("OPENAI_MODEL","gpt-4.1-mini"),
                input=f"You are a beginner Python tutor. Give a short hint, not the final answer. Question: {question}. Student code: {code}. Keep it under 100 words."
            )
            return jsonify({"answer":r.output_text,"source":"ai"})
        except Exception:
            pass
    q=(question+" "+code).lower()
    if "loop" in q or "for " in q: ans="Identify what repeats, then choose a range containing exactly the values you need."
    elif "if " in q: ans="Check the condition first. Python uses a colon and indentation for the body."
    elif "def " in q or "function" in q: ans="A function starts with def, a name, optional parameters, then an indented body."
    else: ans="Break the problem into input, operation, and expected output. Solve one small step at a time."
    return jsonify({"answer":ans,"source":"fallback"})

@app.post("/api/run-code")
def run_code():
    if not session.get("user_id"): return jsonify({"error":"Unauthorized"}),401
    data=request.get_json(silent=True) or {}
    code=" ".join((data.get("code") or "").split()).lower()
    ok="for i in range(1, 6)" in code and "print(i)" in code
    return jsonify({"ok":ok,"output":"1\n2\n3\n4\n5" if ok else "",
                    "message":"Challenge complete! +100 XP" if ok else "Try a for-loop with range(1, 6) and print(i)."})

@app.get("/health")
def health():
    return jsonify({"status":"ok","service":"codequest"})
