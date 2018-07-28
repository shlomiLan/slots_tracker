import pytest

from slots_tracker_server import app as flask_app
from slots_tracker_server.expense import Expense, PayMethods


@pytest.fixture
def client():
    flask_client = flask_app.test_client()
    # Clean the DB
    Expense.objects.delete()
    PayMethods.objects.delete()

    # create fake PayMethods
    PayMethods('Visa').save()
    yield flask_client
