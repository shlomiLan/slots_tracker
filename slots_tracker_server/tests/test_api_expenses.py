from datetime import datetime
import json

from slots_tracker_server.api.expenses import ExpenseAPI
from slots_tracker_server.models import Expense, PayMethods, Categories
from slots_tracker_server.tests.conftest import AMOUNT_1, AMOUNT_3, EXPENSES_WITH_AMOUNT_3
from slots_tracker_server.utils import clean_api_object


# Expense
def test_get_expenses(client):
    rv = client.get('/expenses/')
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert all(x.get('active') for x in r_data)
    for name, _ in ExpenseAPI.api_class.get_all_reference_fields():
        assert all(isinstance(x[name], dict) for x in r_data)


def test_get_expense(client):
    expense = Expense.objects[0]
    rv = client.get('/expenses/{}'.format(expense.id))
    assert isinstance(json.loads(rv.get_data(as_text=True))[0], dict)


def test_filtered_expenses(client):
    rv = client.get(f'/expenses/?amount={AMOUNT_1}')
    data = json.loads(rv.get_data(as_text=True))
    assert isinstance(data[0], dict)
    assert len(data) == 1


def test_multi_filters_expenses(client):
    pay_method_id = PayMethods.objects().first().id
    category_id = Categories.objects().first().id

    rv = client.get(f'/expenses/?amount={AMOUNT_3}&pay_method={pay_method_id}&category={category_id}')
    data = json.loads(rv.get_data(as_text=True))
    assert len(data) == EXPENSES_WITH_AMOUNT_3

    pay_method_2_id = PayMethods.objects()[1].id
    rv = client.get(f'/expenses/?amount={AMOUNT_3}&pay_method={pay_method_2_id}&category={category_id}')
    data = json.loads(rv.get_data(as_text=True))
    assert len(data) == 0


def test_get_deleted_expense(client):
    expense = Expense(amount=200, pay_method=PayMethods.objects().first(),
                      timestamp=datetime.utcnow(), active=False, category=Categories.objects().first()).save()
    rv = client.get('/expenses/{}'.format(expense.id))
    assert rv.status_code == 404


def test_get_expense_404(client):
    invalid_id = '5b6d42132c8884b302632182'
    rv = client.get('/expenses/{}'.format(invalid_id))
    assert rv.status_code == 404


# @given(amount=st.floats(min_value=-10000, max_value=10000),
#        timestamp=st.datetimes(min_value=datetime(1900, 1, 1, 0, 0)), active=st.booleans(),
#        one_time=st.booleans(), payments=st.integers(2, 10))
# @settings(deadline=None)
# def test_post_expenses(client, amount, timestamp, active, one_time, payments):
#     pay_method = PayMethods.objects().first()
#     category = Categories.objects().first()
#
#     data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': timestamp,
#             'category': category.to_json(), 'active': active, 'one_time': one_time}
#
#     rv = client.post(f'/expenses/?payments={payments}', json=data)
#     result = json.loads(rv.get_data(as_text=True))
#     assert len(result) == payments
#     assert rv.status_code == 201
#
#     for i, r in enumerate(result):
#         # Clean the Expense
#         clean_api_object(r)
#         data['pay_method']['instances'] += 1
#         data['category']['instances'] += 1
#         expected_data = {'amount': ExpenseAPI.calc_amount(amount, payments), 'pay_method': data['pay_method'],
#                          'timestamp': date_to_str(next_payment_date(date_to_str(timestamp), payment=i)),
#                          'active': active, 'category': data['category'], 'one_time': one_time}
#         assert r == expected_data
#

def test_delete_expense(client):
    expense = Expense(amount=200, pay_method=PayMethods.objects().first(),
                      timestamp=datetime.utcnow(), category=Categories.objects().first()).save()
    rv = client.delete('/expenses/{}'.format(expense.id))
    assert rv.status_code == 200


def test_update_expense(client):
    pay_method = PayMethods.objects().first()
    category = Categories.objects().first()

    amount, timestamp, active, one_time = test_expense()
    data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': timestamp,
            'category': category.to_json(), 'active': active, 'one_time': one_time}

    rv = client.post('/expenses/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    assert len(result) == 1
    result = result[0]
    result['amount'] = 100
    obj_id = result.get('_id')
    clean_api_object(result)

    rv = client.put('/expenses/{}'.format(obj_id), json=result)
    result = json.loads(rv.get_data(as_text=True))
    assert len(result) == 1
    result = result[0]

    # reload pay method and category
    pay_method = pay_method.reload()
    category = category.reload()

    assert rv.status_code == 200
    assert result.get('amount') == 100
    # Increase because of the post
    assert data.get('pay_method').get('instances') + 1 == pay_method.instances
    assert data.get('category').get('instances') + 1 == category.instances


def test_update_expense_change_ref_filed(client):
    pay_method = PayMethods.objects().first()
    category = Categories.objects().first()

    amount, timestamp, active, one_time = test_expense()
    data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': timestamp,
            'category': category.to_json(), 'active': active, 'one_time': one_time}

    rv = client.post('/expenses/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    assert len(result) == 1
    result = result[0]
    old_pay_method = pay_method.to_json()

    new_pay_method = PayMethods(name='Very random text 1111').save()
    result['pay_method'] = new_pay_method.to_json()
    obj_id = result.get('_id')
    clean_api_object(result)

    rv = client.put('/expenses/{}'.format(obj_id), json=result)
    _ = json.loads(rv.get_data(as_text=True))

    # reload pay method and category
    pay_method = pay_method.reload()
    new_pay_method = new_pay_method.reload()
    category = category.reload()

    assert rv.status_code == 200
    assert new_pay_method.instances == 1
    # Increase because of the post
    assert old_pay_method.get('instances') == pay_method.instances
    assert data.get('category').get('instances') + 1 == category.instances


# Pay method
def test_get_pay_methods(client):
    rv = client.get('/pay_methods/')
    r_data = json.loads(rv.get_data(as_text=True))
    assert isinstance(r_data, list)
    assert all(x.get('active') for x in r_data)
    instances = [x.get('instances') for x in r_data]
    assert sorted(instances, reverse=True) == instances


def test_get_pay_method(client):
    pay_method = PayMethods.objects[0]
    rv = client.get('/pay_methods/{}'.format(pay_method.id))
    assert isinstance(json.loads(rv.get_data(as_text=True)), dict)


def test_get_deleted_pay_method(client):
    pay_method = PayMethods(name='Very random text', active=False).save()
    rv = client.get('/pay_methods/{}'.format(pay_method.id))
    assert rv.status_code == 404


def test_post_pay_method(client):
    data = {'name': 'New visa'}
    expected_data = {'name': 'New visa', 'active': True, 'instances': 0}

    rv = client.post('/pay_methods/', json=data)
    result = json.loads(rv.get_data(as_text=True))
    # Clean the Expense
    clean_api_object(result)

    assert rv.status_code == 201
    assert result == expected_data


def test_post_duplicate_pay_method(client):
    data = {'name': 'New visa'}
    _ = client.post('/pay_methods/', json=data)
    # Create another pay method with the same name
    rv = client.post('/pay_methods/', json=data)
    assert rv.status_code == 400


def test_update_pay_method(client):
    pay_method = PayMethods(name='Random pay method').save()
    pay_method.name = '{}11111'.format(pay_method.name)

    rv = client.put('/pay_methods/{}'.format(pay_method.id), json=pay_method.to_json())
    assert rv.status_code == 200


def test_update_duplicate_pay_method(client):
    name1 = 'Random random pay method'
    _ = PayMethods(name=name1).save()

    name2 = 'Random random random pay method'
    pay_method = PayMethods(name=name2).save()

    pay_method.name = name1
    rv = client.put('/pay_methods/{}'.format(pay_method.id), json=pay_method.to_json())
    assert rv.status_code == 400


def test_delete_pay_method(client):
    pay_method = PayMethods(name='New pay method').save()
    rv = client.delete('/pay_methods/{}'.format(pay_method.id))
    assert rv.status_code == 200
    assert pay_method.reload().active is False


def test_post_expenses_with_payments(client):
    amount, timestamp, active, one_time = test_expense()
    pay_method = PayMethods.objects().first()
    category = Categories.objects().first()

    data = {'amount': amount, 'pay_method': pay_method.to_json(), 'timestamp': timestamp,
            'category': category.to_json(), 'active': active, 'one_time': one_time}

    payments = 3
    rv = client.post(f'/expenses/?payments={payments}', json=data)
    result = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 201
    assert isinstance(result, list)
    assert len(result) == payments


def test_expense():
    return 100, datetime.utcnow(), True, False


def test_calc_amount():
    assert ExpenseAPI.calc_amount(100, 3) == 33.333333333333336
    assert ExpenseAPI.calc_amount(62, 4) == 15.5
    assert ExpenseAPI.calc_amount(63, 5) == 12.6
