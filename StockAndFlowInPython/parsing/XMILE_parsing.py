"""Parsing Utility for XMILE file"""
from StockAndFlowInPython.graph_sd.graph_based_engine import LINEAR, SUBTRACTION, DIVISION, ADDITION, MULTIPLICATION


name_operator_mapping = {ADDITION: '+', SUBTRACTION: '-', MULTIPLICATION: '*', DIVISION: '/'}


def text_to_digit(text):
    try:
        digit = float(text)
        return digit
    except ValueError:
        return text


def parsing_addition(equation):
    factors = equation.split('+')
    for i in range(len(factors)):
        factors[i] = text_to_digit(factors[i])
    return factors


def parsing_multiplication(equation):
    factors = equation.split('*')
    for i in range(len(factors)):
        factors[i] = text_to_digit(factors[i])
    return factors


def parsing_division(equation):
    factors = equation.split('/')
    for i in range(len(factors)):
        factors[i] = text_to_digit(factors[i])
    return factors


def parsing_subtract(equation):
    factors = equation.split('-')
    for i in range(len(factors)):
        factors[i] = text_to_digit(factors[i])
    return factors


def is_number(text):
    outcome = True
    for i in range(len(text)):  # filter out conditions like '0-0', '1-4', etc.
        try:
            float(text[i])
        except ValueError:
            outcome = False
            break
    try:  # filter in conditions like '0.05'
        float(text)
        outcome = True
    except ValueError:
        pass

    return outcome


def text_to_equation(equation_text):
    '''
    This equation could be
    1) a constant number
    2) a variable's name
    3) another equation
    '''
    if is_number(equation_text):
        return [float(equation_text)]

    elif '+' in equation_text:
        factors = parsing_addition(equation_text)
        return [ADDITION] + factors

    elif '*' in equation_text:
        factors = parsing_multiplication(equation_text)
        return [MULTIPLICATION] + factors

    elif '/' in equation_text:
        factors = parsing_division(equation_text)
        return [DIVISION] + factors

    elif '-' in equation_text:
        factors = parsing_subtract(equation_text)
        return [SUBTRACTION] + factors

    else:
        return equation_text


def equation_to_text(equation):
    if type(equation) == int or type(equation) == float:
        return str(equation)
    try:
        equation[0].isdigit()  # if it's a number
        return str(equation)
    except AttributeError:
        if equation[0] in [ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION]:
            return str(equation[1]) + name_operator_mapping[equation[0]] + str(equation[2])
        elif equation[0] == LINEAR:
            return str(equation[1])
