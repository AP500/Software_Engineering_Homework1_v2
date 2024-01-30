import pytest
from flask import Flask, session
from app import app, db, User, LeaveRequest
from datetime import datetime


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_index_html_rendering(client):
    with app.app_context():
        User.query.filter_by(username="testuser2").delete()
        db.session.commit()

        user = User(username="testuser2")
        user.set_password("testpassword")
        db.session.add(user)
        db.session.commit()

        leave_request = LeaveRequest(
            username="testuser2",
            leave_date=datetime.strptime("2022-12-31", "%Y-%m-%d").date(),
            reason="Vacation",
        )
        db.session.add(leave_request)
        db.session.commit()

    client.post(
        "/login",
        data=dict(username="testuser2", password="testpassword"),
        follow_redirects=True,
    )


def test_login_html_rendering(client):
    response = client.get("/login")
    assert b"Login" in response.data


def test_register_html_rendering(client):
    response = client.get("/register")
    assert b"Register" in response.data
