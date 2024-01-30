import pytest
from flask import Flask, session
from app import app, db, User, LeaveRequest

LOGIN_ROUTE = "/login"
LEAVE_REQUESTS = "Leave Requests"

@pytest.fixture
def clean_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

def test_load_user(client, clean_database):
    with app.app_context():
        user = User(username="testuser4")
        db.session.add(user)
        db.session.commit()

        loaded_user = User.query.filter_by(username="testuser4").first()
        assert user == loaded_user

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
        LOGIN_ROUTE,
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )

    response = client.get("/")
    assert LEAVE_REQUESTS.encode() in response.data

def test_index_route_unauthenticated(client):
    response = client.get("/")
    assert response.status_code == 302

def test_login_route(client):
    response = client.get(LOGIN_ROUTE)
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
        LOGIN_ROUTE,
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )
    assert b"You were successfully logged in!" in response.data

def test_logout_route(client):
    response = client.get("/logout")
    assert response.status_code == 302


def test_logout_functionality(client):
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        if not user:
            user = User(username="testuser")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()

    client.post(
        LOGIN_ROUTE,
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
        LOGIN_ROUTE,
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )
    response = client.post(
        "/request_leave",
        data=dict(username="testuser", leave_date="2020-01-01", reason="Vacation"),
        follow_redirects=True,
    )
    assert LEAVE_REQUESTS.encode() in response.data
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
        LOGIN_ROUTE,
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )
    response = client.post("/delete_leave_request/1", follow_redirects=True)
    assert LEAVE_REQUESTS.encode() in response.data

def test_already_requested_functionality(client):
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
        LOGIN_ROUTE,
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )
    response = client.post(
    "/request_leave",
    data=dict(leave_date="2022-12-31", reason="Vacation"),
    follow_redirects=True,
    )
    assert LEAVE_REQUESTS.encode() in response.data

def test_prove_leave_date_functionality(client):
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
        LOGIN_ROUTE,
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )
    response = client.post(
    "/request_leave",
    data=dict(leave_date="2022-12-31", reason="Vacation"),
    follow_redirects=True,
    )
    assert LEAVE_REQUESTS.encode() in response.data

def test_leave_requests_count_functionality(client):
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
        LOGIN_ROUTE,
        data=dict(username="testuser", password="testpassword"),
        follow_redirects=True,
    )
    response = client.post(
    "/request_leave",
    data=dict(leave_date="2022-12-31", reason="Vacation"),
    follow_redirects=True,
    )
    assert LEAVE_REQUESTS.encode() in response.data

def test_main():
    assert __name__ == "app_test"