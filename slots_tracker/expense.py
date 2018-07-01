# system modules
import datetime

# 3rd party modules
from flask import abort
from mongoengine import *

from slots_tracker.utils import convert_to_object_id


# Find way to add data with migration script
class PayMethods(Document):
    name = StringField(required=True, max_length=200)


class Expense(Document):
    amount = IntField()
    descreption = StringField(required=True, max_length=200)
    pay_method = ReferenceField(PayMethods, required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)


def create(expense):
    new_expense = Expense(**expense).save()
    return read_one(new_expense.id), 201


def read_all():
    return Expense.objects.to_json()


@convert_to_object_id
def read_one(expense_id):
    """
    This function responds to a request for /api/expense/{expenses_id}
    with one matching expense from expenses list
    :param expense_id: id of the expense to find
    :return:           expense matching id
    """
    try:
        # Does the expense exist in the DB
        return Expense.objects.get(id=expense_id).to_json()
    except DoesNotExist:
        abort(404, 'Expense with id {} not found'.format(expense_id))
