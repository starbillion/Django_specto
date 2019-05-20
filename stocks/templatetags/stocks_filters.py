from random import random

from django import template
from datetime import datetime
import math
from decimal import Decimal

register = template.Library()


@register.filter(name='min')
def min(value, arg):
    '''
    Divides the value; argument is the divisor.
    Returns empty string on any error.
    '''
    try:
        value = int(value)
        arg = int(arg)
        if arg: return value + arg
    except:
        pass
    return ''


@register.filter(name='datefilter')
def datefilter(value):
    '''
    Divides the value; argument is the divisor.
    Returns empty string on any error.
    '''
    try:
        temp = value.split(" ")
        return temp[0]
    except:
        pass
    return ''


"""
converting string date into YY-mm-dd format
"""


@register.filter(name='date_convert')
def date_convert(date):
    return datetime.fromtimestamp(int(date)).strftime("%Y-%m-%d %I:%M:%S")


@register.filter(name='point_round')
def point_round(n):
    try:
        return round(Decimal(n), 2)
    except:
        pass
    return ''


@register.filter(name='point_round_percent')
def point_round_percent(n):
    try:
        temp = round(Decimal(n * 100), 2)
        if temp > 0:
            temp = "+" + str(temp)
        return temp
    except:
        pass
    return ''


@register.filter(name='millify')
def millify(n):
    try:
        return str(round(Decimal(n / 1000000000), 3)) + "B"
    except:
        pass
    return ''


def accu_of_date(stock, date):
    return random.randint(70, 100)


@register.filter(name='calc_err_of_date')
def calc_err_of_date(stock, date):
    return (100 - accu_of_date(stock, date))

"""
converting True/False to Yes/No
"""


@register.filter(name='date_convert')
def change_yes_no(false_or_yes):
    if not false_or_yes:
        return "No"
    else:
        return "Yes"
