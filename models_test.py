import pytest
import models as models
from datetime import datetime
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


def test_user_model(client):
    with app.app_context():
        User.query.filter_by(username="testuser1").delete()
        db.session.commit()

        user = User(username="testuser1")
        user.set_password("testpassword")
        db.session.add(user)
        db.session.commit()

        assert user.username == "testuser1"
        assert user.check_password("testpassword") == True


def test_leave_request_model(client):
    with app.app_context():
        leave_request = LeaveRequest(
            username="testuser1",
            leave_date=datetime.strptime("2021-01-01", "%Y-%m-%d").date(),
            reason="test reason",
        )
        db.session.add(leave_request)
        db.session.commit()

        assert leave_request.username == "testuser1"
        assert leave_request.leave_date.strftime("%Y-%m-%d") == "2021-01-01"
        assert leave_request.reason == "test reason"
