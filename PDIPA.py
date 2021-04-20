#!/usr/bin/env python
# coding: utf-8

# # This is a program that runs the primal dual interior point algorithm given a function and a starting point  (and some other variables)
# ### by Abraham Holleran

#Anaconda
#cd /D C:\Users\Abraham\miniconda3\envs\snowflakes\Scripts
#streamlit run PDIPA.py

import numpy as np
import pandas as pd
import sympy
import math
import streamlit as st
from functools import reduce
from bokeh.plotting import figure


# Edit these meta values if necessary.



alpha = 0.8 #step size parameter for getting away from constraint
beta = 0.9 #step size it parameter
epsilon = 0.001 #erative parameter
gamma = 0.1 #duality gapstopping tolerance


# Carefully put your variables, functions, and constraints here.

st.sidebar.button("Re Run")
alpha = st.sidebar.number_input("Alpha", 0.8)
beta = st.sidebar.number_input("Beta", 0.9)
epsilon = st.sidebar.number_input("Epsilon", 0.001)
gamma = st.sidebar.number_input("Gamma", 0.1)

st.title("Primal-dual Interior Point Algorithm")
st.header("By Abraham Holleran")
st.write("Written from the book [Linear and Convex Optimization](https://www.wiley.com/go/veatch/convexandlinearoptimization) under the supervision of the author, Dr. Michael Veatch.")
option = st.selectbox('Which function do you want to optimize?', ('max 10+10*x1 - 8*x2 - 4*sympy.exp(x1)-sympy.exp(x1-x2)', 'max 10*x1 - sympy.exp(x1)'))
if option[-2] == "2":
    option = 1
else:
    option = 2
if option == 1:
    mu_value = st.sidebar.number_input("Mu", 1.0)
    x1,x2, mu = sympy.symbols('x1 x2 mu', real = True)
    X = sympy.Matrix([x1, x2])
    y1, y2 = sympy.symbols('y1 y2', real = True)
    Y = sympy.Matrix([y1, y2])
    all_vars = sympy.Matrix([x1, x2, y1, y2])
    dx1, dx2, dy1, dy2 = sympy.symbols('dx1 dx2 dy1 dy2', real = True)
    f, g1, g2 = sympy.symbols('f g1 g2', cls=sympy.Function)
    s1, s2 = sympy.symbols('s1 s2', real = True)     #one s_i for each g_i, b_i
    user_input =  st.text_input("Write the initial starting point with x first then y", "0.5 0.6 5 10")
    #point = [float(i) for i in user_input.split(' ')]
    #point = [0.5, 0.6, 5, 10] #the Initial point, as (x, y) with x values first, and y>0 values second.
    #point = [0.164, 0.066, 5, 10]
    f = 10+10*x1 - 8*x2 - 4*sympy.exp(x1)-sympy.exp(x1-x2)
    g1 = x2-x1**(0.5)
    g2 = -x2 + x1**(1.5)
    g = sympy.Matrix([g1, g2])
    b = sympy.Matrix([0,0])
    alist = ["k", "mu", "x1", "x2", "y1", "y2", "f(x)", "lambda", "||d||"]
elif option == 2:
    mu_value = st.sidebar.number_input("Mu", 2.0)
    x1, x2, mu = sympy.symbols('x1 x2 mu', real=True)
    X = sympy.Matrix([x1])
    mu_value = 2
    y1 = sympy.symbols('y1', real=True)
    Y = sympy.Matrix([y1])
    all_vars = sympy.Matrix([x1, y1])
    dx1, dy1 = sympy.symbols('dx1 dy1', real=True)
    f, g1 = sympy.symbols('f g1 ', cls=sympy.Function)
    s1 = sympy.symbols('s1', real=True)  # one s_i for each g_i, b_i
    f = 10 * x1 - sympy.exp(x1)
    g1 = x1
    g = sympy.Matrix([g1])
    b = sympy.Matrix([2])
    alist = ["k", "mu", "x1", "y1", "f(x)", "lambda", "||d||"]
    user_input = st.text_input("Write the initial starting point with x first then y", "1 0.5")
point = []
for i in user_input.split(' '):
    try:
        point.append(int(i))
    except:
        point.append(float(i))
s = sympy.Matrix([b[i] - g[i].subs([*zip(X, point[:len(X)])]).evalf() for i in range(len(g))])
#st.write(sympy.Matrix([b[0] - g[0].subs([*zip(X, point[:len(X)])]).evalf()]))
st.write(f"Maximize {f} \n subject to")
for i in range(len(g)):
    st.write(f"{g[i]} + s_{i} = {b[i]}")


#H = sympy.Matrix(len(X),len(X), lambda i,j: sympy.diff(sympy.diff(f, X[i]), X[j]))
gradient = lambda f, v: sympy.Matrix([f]).jacobian(v)

H = sympy.hessian(f,X)
Z = sympy.zeros(len(X))
thing = [y_i*sympy.hessian(g_i, X)for y_i, g_i in zip(Y,g)]
sum_M = reduce((lambda x, y: x + y), thing)
Q = -H + sum_M


m = sympy.Matrix([mu/y_i for y_i in Y])
RHSB = b - g-m
J = g.jacobian(X)
RHST = gradient(f,X).T-J.T*Y
RHS = sympy.Matrix([RHST,RHSB])



S = sympy.diag(*[(b_i - g_i)/y_i for b_i, g_i, y_i in zip(b, g, Y)])
LHS = sympy.Matrix([[Q, J.T], [J, S]])



solv = LHS.LUsolve(RHS)
k = 0
done = False
data = []
while not done and k < 14:

    solv_eval = solv.subs([*zip(all_vars, point), (mu, mu_value)]).evalf()
    f_eval = f.subs([*zip(X, point[:len(X)])])
    l_max =min(1,min([y_i/-dy_i if dy_i < 0 else 1 for y_i, dy_i in zip(point[-len(Y):], solv_eval[-len(Y):])]))
    assert(all([y_i + l_max*dy_i >= 0 for y_i, dy_i in zip(point[-len(Y):], solv_eval[-len(Y):])]))
    l= l_max
    all_constraints_satisfied = False
    violation = False
    while not all_constraints_satisfied:
        test_x = [i+l*j for i, j in zip(point[:len(X)], solv_eval[:len(X)])]
        for g_i, b_i in zip(g, b):
            g_eval = g_i.subs([*zip(all_vars[:len(X)], test_x)])
            if g_eval > b_i:
                violation = True
        if violation:
            l *= beta
        else:
            all_constraints_satisfied = True
    l *= alpha
    dnorm = math.sqrt(sum(map(lambda i : l*i * l*i, solv_eval[:len(X)])))
    if k == 0:
        value_list = [k, mu_value, *[round(float(i),4) for i in point], round(f_eval,3), l, dnorm]
    else:
        value_list = [k, mu_value, *[round(float(i),4) for i in point], f_eval, l, dnorm]
    data.append(value_list)
    point = [i+l*j for i,j in zip(point, solv_eval)]
    mu_value *= gamma
    k +=1
    if math.sqrt(sum(map(lambda i : l*i * l*i, solv_eval[:len(X)]))) <= epsilon:
        st.write(f"We're close enough as ||lambda*d^x|| <= epsilon. {round(dnorm, 6)} <= {epsilon}")
        done = True
df = pd.DataFrame(data, columns=alist)
st.write(df)
    #if k >= 5:
    #    st.write(l_max, type(l_max), alpha, beta, gamma, epsilon, mu_value)
rounded_point = [round(i, 4) for i in point]
st.write(f"The approximately optimal point is: {rounded_point}")
st.write(f"It has a value of: {f.subs([*zip(X, point[:len(X)])])}")
#%matplotlib inline
#xspace = np.linspace(-5, 5, 200)
#yspace = np.linspace(-5, 5, 200)
#Xmesh, Ymesh = np.meshgrid(xspace, yspace)
#Z = f.subs(np.vstack([Xmesh.ravel(), Ymesh.ravel()])).evalf().reshape((200,200))
#plt.pyplot.contour(X, Y, Z)


