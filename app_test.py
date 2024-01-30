import pytest
from flask import Flask, session
from app import app, db, User, LeaveRequest


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_index_route_authenticated(client):
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        if not user:
            user = User(username="testuser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

    client.post(
        "/login",
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )

    response = client.get("/")
    assert b"Leave Requests" in response.data


def test_login_route(client):
    response = client.get("/login")
    assert b"Login" in response.data


def test_login_functionality(client):
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        if not user:
            user = User(username="testuser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

    response = client.post(
        "/login",
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )
    assert b"You were successfully logged in!" in response.data


def test_logout_functionality(client):
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        if not user:
            user = User(username="testuser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

    client.post(
        "/login",
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )
    response = client.get("/logout", follow_redirects=True)
    assert b"Login" in response.data


def test_register_route(client):
    response = client.get("/register")
    assert b"Register" in response.data


def test_register_functionality(client):
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        if user:
            db.session.delete(user)
            db.session.commit()

    response = client.post(
        "/register",
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )
    assert b"Successfully registered! You can now login." in response.data


def test_request_leave_route(client):
    response = client.get("/request_leave")
    assert response.status_code == 405


def test_request_leave_functionality(client):
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        if not user:
            user = User(username="testuser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

    client.post(
        "/login",
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )
    response = client.post(
        "/request_leave",
        data=dict(username="testuser", leave_date="2020-01-01", reason="Vacation"),
        follow_redirects=True,
    )
    assert b"Leave Requests" in response.data
    assert b"Vacation" in response.data


def test_delete_leave_request_route(client):
    response = client.get("/delete_leave_request/1")
    assert response.status_code == 405


def test_delete_leave_request_functionality(client):
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        if not user:
            user = User(username="testuser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

        leave_request = LeaveRequest.query.filter_by(username="testuser").first()
        if not leave_request:
            leave_request = LeaveRequest(
                username="testuser", leave_date="2020-01-01", reason="Vacation"
            )
            db.session.add(leave_request)
            db.session.commit()

    client.post(
        "/login",
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )
    response = client.post("/delete_leave_request/1", follow_redirects=True)
    assert b"Leave Requests" in response.data
