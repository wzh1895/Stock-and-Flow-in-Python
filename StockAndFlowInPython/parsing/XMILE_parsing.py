"""Parsing Utility for XMILE file"""
from StockAndFlowInPython.graph_sd.graph_based_engine import LINEAR, SUBTRACTION, DIVISION, ADDITION, MULTIPLICATION


def parsing_multiplication(equation):
    factors = equation.split('*')
    return [[factor, 0] for factor in factors]


def parsing_division(equation):
    factors = equation.split('/')
    return [[factor, 0] for factor in factors]


def parsing_subtract(equation):
    factors = equation.split('-')
    return [[factor, 0] for factor in factors]


def is_number(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def parsing_equation(equation):
    '''
    This equation could be
    1) a constant number
    2) a variable's name
    3) another equation
    '''
    if is_number(equation):
        return [float(equation)]

    elif '*' in equation:
        factors = parsing_multiplication(equation)
        return [MULTIPLICATION] + factors

    elif '/' in equation:
        factors = parsing_division(equation)
        return [DIVISION] + factors

    elif '-' in equation:
        factors = parsing_subtract(equation)
        return [SUBTRACTION] + factors

    else:
        return equation

