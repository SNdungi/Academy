#MATHEMATICS
# The content features different levels of learning in the competency bases curriculum.

#Elementary

#Lesson 2 counting
TOPIC='NUMBER STRUCTURE'
LEVEL='elementary'
#CELLS
def get_place_values(number):
    number_str = str(number)
    total_values = {}
    decimal=int(number_str.find('.'))
    integer_place_value_names = ['ones', 'tens', 'hundreds', 'thousands', 'ten thousands', 'hundred thousands', 'millions']
    decimal_place_value_names = ['tenths', 'hundredths', 'thousandths', 'ten thousandths', 'hundred thousandths']

    for i, digit_char in enumerate(number_str):
        if i<decimal:
            place_value = 10 ** (decimal-1- i)
            name = integer_place_value_names[decimal - i - 1] 
            total_values[digit_char+name] = {'value': place_value * int(digit_char), 'name': name}

        elif i>decimal:
            place_value=10 ** (decimal-i)
            name = decimal_place_value_names[i - decimal-1] 
            total_values[digit_char+name] = {'value': place_value * int(digit_char), 'name': name}
        else:
            place_value=None

    return total_values

#Lesson 2 counting
TOPIC='NUMBER OPERATIONS'

class MathOperations:
    def __init__(self, max_number):
        self.max_number = max_number

    def add(self, num1, num2):
        if num1 > self.max_number or num2 > self.max_number:
            return 'select a higher level to work with large numbers'
        return num1 + num2

    def subtract(self, num1, num2):
        if num1 > self.max_number or num2 > self.max_number:
            return 'select a higher level to work with large numbers'
        return num1 - num2

    def multiply(self, num1, num2):
        if num1 > self.max_number or num2 > self.max_number:
            return 'select a higher level to work with large numbers'
        return num1 * num2

    def divide(self, num1, num2):
        if num1 > self.max_number or num2 > self.max_number:
            return 'select a higher level to work with large numbers'
        if num2 == 0:
            raise ZeroDivisionError("Division by zero")
        return num1 / num2


class Elementary (MathOperations):
    def __init__(self):
        super().__init__(1000)

class Intermediate (MathOperations):
    def __init__(self):
        super().__init__(100000)

class Advanced (MathOperations):
    def __init__(self):
        super().__init__(float('inf'))

# Example usage
a= Elementary()
b= Intermediate()
c= Advanced()

result = a.add(1100, 300)
print(result)


import streamlit as st
import time

def add_with_steps(num1, num2):
    result = ""
    carry = 0
    while num1 or num2 or carry:
        digit1 = num1 % 10 if num1 else 0
        digit2 = num2 % 10 if num2 else 0
        total = digit1 + digit2 + carry
        carry = total // 10
        result = f"{digit1} + {digit2} + {carry} = {total % 10}\n{result}"
        num1 //= 10
        num2 //= 10
    return result

st.title('Animated Addition with Carrying Over')

num1 = st.number_input('Enter the first number:', value=123)
num2 = st.number_input('Enter the second number:', value=456)

if st.button('Add'):
    result = add_with_steps(int(num1), int(num2))
    for step in result.split('\n'):
        st.write(step)
        time.sleep(1)



