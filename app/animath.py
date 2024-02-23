
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



