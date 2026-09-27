from app import app, db, User, Lesson, Challenge, Badge, UserBadge
from werkzeug.security import generate_password_hash
import json

def seed():
    db.drop_all()
    db.create_all()

    badges = [
        ("First Step", "Complete your first challenge.", "🌱"),
        ("Bug Hunter", "Complete a debugging challenge.", "🐛"),
        ("Loop Master", "Complete the Loop Mountain world.", "🔄"),
        ("Function Wizard", "Complete the Function Castle world.", "🧙"),
        ("Python Master", "Defeat the final boss.", "👑"),
    ]
    for name, desc, icon in badges:
        db.session.add(Badge(name=name, description=desc, icon=icon))

    lesson_data = [
        ("Variable Village", "🌱", "Learn how variables store information.", "Beginner", 500),
        ("Data Type Docks", "🧩", "Discover strings, integers, floats and booleans.", "Beginner", 500),
        ("Operator Factory", "⚙️", "Use arithmetic, comparison and logical operators.", "Beginner", 500),
        ("Logic Forest", "🌲", "Teach your programs to make decisions with if and else.", "Beginner", 500),
        ("Loop Mountain", "🔄", "Repeat actions using for and while loops.", "Intermediate", 500),
        ("Function Castle", "🧙", "Build reusable blocks of code with functions.", "Intermediate", 500),
        ("List Kingdom", "📦", "Store and work with collections using lists.", "Intermediate", 500),
        ("Final Boss", "👑", "Combine your Python skills in a final challenge.", "Boss", 1000),
    ]
    lessons = []
    for i, (title, icon, desc, diff, xp) in enumerate(lesson_data, 1):
        l = Lesson(title=title, icon=icon, description=desc, difficulty=diff, xp_reward=xp, order_num=i)
        db.session.add(l)
        lessons.append(l)
    db.session.commit()

    challenges = [
        (1, "Which value is stored in name?\n\nname = 'Alex'", "mcq", ["Alex", "name", "Python", "Nothing"], "Alex", "Correct! The variable name stores the string Alex.", "Think about the value on the right side of the assignment.", 50),
        (1, "Complete the code:\n\nscore ___ 100", "mcq", [">", "<", "=", "!="], "=", "Correct! = assigns a value.", "Assignment uses a single equals sign.", 50),
        (2, "What is the type of 42?", "mcq", ["str", "int", "float", "bool"], "int", "Correct! 42 is an integer.", "It is a whole number.", 50),
        (2, "What is the type of 'hello'?", "mcq", ["str", "int", "list", "bool"], "str", "Correct! Text in quotes is a string.", "Look at the quotation marks.", 50),
        (3, "What is 5 + 3?", "mcq", ["6", "7", "8", "9"], "8", "Correct! 5 + 3 = 8.", "Add the two numbers.", 50),
        (3, "Which operator means 'equal to'?", "mcq", ["=", "==", "!=", ">"], "==", "Correct! == compares values.", "Assignment and comparison use different operators.", 50),
        (4, "Complete:\n\nif age >= 18___\n    print('Adult')", "mcq", [":", ";", ".", ","], ":", "Correct! A colon begins the indented block.", "Python uses a colon after an if condition.", 75),
        (4, "Which branch runs when the if condition is false?", "mcq", ["if", "else", "for", "def"], "else", "Correct! else handles the alternative.", "Think of the alternative path.", 50),
        (5, "Which keyword creates a loop over items?", "mcq", ["for", "if", "def", "class"], "for", "Correct! for iterates over a sequence.", "It starts with the same letter as 'repeat for each'.", 75),
        (5, "Which loop continues while a condition is true?", "mcq", ["for", "while", "if", "return"], "while", "Correct! while repeats while its condition is true.", "The keyword describes the condition.", 75),
        (6, "Which keyword defines a function?", "mcq", ["func", "function", "def", "make"], "def", "Correct! def defines a Python function.", "It is a short keyword.", 75),
        (6, "What keyword sends a value back from a function?", "mcq", ["send", "return", "back", "yield"], "return", "Correct! return sends a result back.", "It literally returns the result.", 75),
        (7, "Which brackets create a list?", "mcq", ["()", "{}", "[]", "<>"], "[]", "Correct! Lists use square brackets.", "Think of a shopping list inside square brackets.", 75),
        (7, "What is the first index of a Python list?", "mcq", ["0", "1", "-1", "first"], "0", "Correct! Python uses zero-based indexing.", "Counting starts at zero.", 75),
        (8, "BOSS: Which statement prints 'Python'?\n\nname = 'Python'", "mcq", ["print(name)", "echo(name)", "display name", "show(name)"], "print(name)", "Boss defeated! You combined variables and output.", "Use Python's built-in output function.", 150),
        (8, "BOSS: Fix the condition:\n\nif score ___ 100:\n    print('Win')", "mcq", [">=", "=>", "=", "><"], ">=", "Boss defeated! >= means greater than or equal to.", "The greater-than symbol comes first.", 150),
        (8, "BOSS: Which keyword creates a reusable function?", "mcq", ["def", "loop", "fun", "create"], "def", "Final boss complete! You know how functions begin.", "Functions begin with a three-letter keyword.", 150),
    ]
    for lesson_id, q, typ, opts, ans, exp, hint, xp in challenges:
        db.session.add(Challenge(
            lesson_id=lesson_id, question=q, challenge_type=typ,
            options_json=json.dumps(opts), answer=ans,
            explanation=exp, hint=hint, xp_reward=xp,
            difficulty="Boss" if lesson_id == 8 else ("Medium" if lesson_id >= 5 else "Easy")
        ))
    db.session.commit()

    demo = User(username="DemoPlayer", email="demo@codequest.local", password_hash=generate_password_hash("demo1234"), xp=1250, level=3, streak=5)
    db.session.add(demo)
    db.session.commit()
    award = Badge.query.filter_by(name="First Step").first()
    db.session.add(UserBadge(user_id=demo.id, badge_id=award.id))
    db.session.commit()
    print("Database seeded successfully.")
    print("Demo login: demo@codequest.local / demo1234")

if __name__ == "__main__":
    with app.app_context():
        seed()
