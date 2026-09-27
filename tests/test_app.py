import os
import tempfile
import pytest
from app import app, db, User, Lesson, Challenge

@pytest.fixture()
def client():
    db_fd, path = tempfile.mkstemp()
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///" + path)
    with app.app_context():
        db.drop_all()
        db.create_all()
    with app.test_client() as client:
        yield client
    os.close(db_fd)
    os.unlink(path)

def test_index(client):
    assert client.get("/").status_code == 200

def test_register(client):
    r = client.post("/register", data={"username":"tester","email":"test@example.com","password":"secret1"}, follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        assert User.query.filter_by(email="test@example.com").first() is not None

def test_api_lessons(client):
    with app.app_context():
        db.session.add(Lesson(title="Variables", icon="🌱", description="Learn", order_num=1, xp_reward=500))
        db.session.commit()
    r = client.get("/api/lessons")
    assert r.status_code == 200
    assert r.json[0]["title"] == "Variables"
