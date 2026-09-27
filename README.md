# ⚡ CodeQuest — Gamified Interactive Learning Platform

CodeQuest turns beginner Python learning into an adventure. Learners explore worlds, solve challenges, earn XP, unlock levels and collect badges.

## Features

- Python learning adventure map
- 8 beginner-friendly worlds
- Interactive challenges
- XP and levels
- Badges
- Streak-ready user model
- Leaderboard
- Profile
- Login/register with hashed passwords
- SQLite database
- Responsive dark game-style UI
- REST-style API starter endpoints
- Demo account
- Automated tests

## Stack

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- SQLite
- Jinja2
- HTML/CSS/JavaScript
- pytest

## Windows setup

From the project folder:

```powershell
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe seed.py
venv\Scripts\python.exe app.py
```

If PowerShell allows activation:

```powershell
venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python app.py
```

Open:

http://127.0.0.1:5000

## Demo account

Email: `demo@codequest.local`

Password: `demo1234`

## Tests

```powershell
venv\Scripts\python.exe -m pytest -q
```

## Hackathon demo flow

1. Open landing page.
2. Login with the demo account.
3. Show dashboard XP, level, streak and adventure.
4. Open Adventure Map.
5. Enter Variable Village.
6. Complete a challenge.
7. Show instant feedback and XP.
8. Open leaderboard.
9. Open profile and show achievements.
10. Explain that the architecture can be extended with an AI tutor and adaptive difficulty.

## Future roadmap

- AI tutor with progressive hints
- Adaptive difficulty
- More challenge types including code execution sandboxing
- Multiplayer competitions
- Daily quests
- Classroom/teacher dashboard
- Cloud deployment
- More programming languages

## Hackathon pitch

> CodeQuest transforms programming education from passive learning into an interactive adventure. Students don't simply read about Python — they explore worlds, solve coding challenges, earn XP, unlock levels and collect badges. The platform is designed to make programming more engaging for beginners while keeping the learning experience measurable and practical.

## Hackathon-ready upgrade
AI Tutor, browser Python editor, animated rewards, Gunicorn, Render configuration, environment variables, PostgreSQL-ready configuration, and `/health` are included.

The editor uses a curated evaluator and does not execute arbitrary Python on the Flask server. For production code execution, use an isolated sandbox.

## Vercel
See `VERCEL_DEPLOYMENT.md` for GitHub → Vercel deployment and environment-variable setup.
