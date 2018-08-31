import datetime
import json

from slots_tracker_server.models import Expense, PayMethods
from slots_tracker_server.utils import object_id_to_str, date_to_str


# Expense
def test_get_expenses(client):
    rv = client.get('/expenses/')
    assert isinstance(json.loads(rv.get_data(as_text=True)), list)


def test_get_expense(client):
    expense = Expense.objects[0]
    rv = client.get('/expenses/{}'.format(expense.id))
    assert isinstance(json.loads(rv.get_data(as_text=True)), dict)


def test_get_expense_404(client):
    invalid_id = '5b6d42132c8884b302632182'
    rv = client.get('/expenses/{}'.format(invalid_id))
    assert rv.status_code == 404


def test_post_expenses(client):
    pay_method = PayMethods.objects().first()
    date = datetime.datetime.utcnow()
    data = {'amount': 200, 'description': 'Random stuff', 'pay_method': pay_method.to_json(), 'timestamp': date}
    expected_data = {'amount': 200, 'description': 'Random stuff', 'pay_method': object_id_to_str(pay_method.id),
                     'timestamp': date_to_str(date)}

    rv = client.post('/expenses/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    # Remove the Expense ID
    del result['_id']

    assert rv.status_code == 201
    assert result == expected_data


def test_delete_expense(client):
    expense = Expense(amount=200, description='Random stuff', pay_method=PayMethods.objects().first(),
                      timestamp=datetime.datetime.utcnow()).save()
    rv = client.delete('/expenses/{}'.format(expense.id))
    assert rv.status_code == 200


def test_update_expense(client):
    expense = Expense(amount=200, description='Random stuff', pay_method=PayMethods.objects().first(),
                      timestamp=datetime.datetime.utcnow()).save()
    expense.amount = 100
    rv = client.put('/expenses/{}'.format(expense.id), json=expense.to_json())
    assert rv.status_code == 200


# Pay method
def test_post_pay_method(client):
    data = {'name': 'New visa'}
    expected_data = {'name': 'New visa'}

    rv = client.post('/pay_methods/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    # Remove the Expense ID
    del result['_id']

    assert rv.status_code == 201
    assert result == expected_data


def test_post_duplicate_pay_method(client):
    data = {'name': 'New visa'}
    _ = client.post('/pay_methods/', json=data)
    # Create another pay method with the same name
    rv = client.post('/pay_methods/', json=data)
    assert rv.status_code == 400


def test_update_pay_method(client):
    pay_method = PayMethods('Random pay method').save()
    pay_method.name = '{}11111'.format(pay_method.name)

    rv = client.put('/pay_methods/{}'.format(pay_method.id), json=pay_method.to_json())
    assert rv.status_code == 200


def test_update_duplicate_pay_method(client):
    name1 = 'Random random pay method'
    _ = PayMethods(name1).save()

    name2 = 'Random random random pay method'
    pay_method = PayMethods(name2).save()

    pay_method.name = name1
    rv = client.put('/pay_methods/{}'.format(pay_method.id), json=pay_method.to_json())
    assert rv.status_code == 400