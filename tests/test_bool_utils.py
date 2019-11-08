# Copyright 2019 MIT Probabilistic Computing Project.
# See LICENSE.txt

import pytest

from sympy import FiniteSet
from sympy import Interval
from sympy import S as Singletons
from sympy import Union
from sympy import exp
from sympy import log
from sympy import oo
from sympy import sqrt
from sympy import symbols
from sympy import to_dnf

from sum_product_dsl.contains import Contains
from sum_product_dsl.contains import NotContains
from sum_product_dsl.distributions import factor_dnf_symbols
from sum_product_dsl.distributions import get_symbols
from sum_product_dsl.distributions import solver

(X0, X1, X2, X3, X4, X5, X6, X7, X8, X9) = symbols('X:10')

def test_get_symbols():
    syms = get_symbols((X0 > 3) & (X1 < 4))
    assert len(syms) == 2
    assert X0 in syms
    assert X1 in syms

    syms = get_symbols((exp(X0) > log(X1)+10) & (X2 < 4))
    assert len(syms) == 3
    assert X0 in syms
    assert X1 in syms
    assert X2 in syms

def test_solver():
    expr = log(X0) > 2
    interval = solver(expr)
    assert interval.start == exp(2)
    assert interval.end == oo

    expr = (log(X0) > 2) & (X0 < exp(2))
    interval = solver(expr)
    assert interval == Singletons.EmptySet

    expr = (log(X0) >= 2) & (X0 <= exp(2))
    interval = solver(expr)
    assert interval == FiniteSet(exp(2))

    expr = (X0 >= 0) | (X0 <= 0)
    interval = solver(expr)
    assert interval == Singletons.Reals

    expr = ((2*X0 + 10) < 4) & (X0 + 10 > 3)
    interval = solver(expr)
    assert interval.start == 3 - 10
    assert interval.end == (4-10)/2

    expr = (X0**2 - 2*X0) > 10
    interval = solver(expr)
    assert interval == Union(
        Interval.open(-oo, 1 - sqrt(11)),
        Interval.open(1 + sqrt(11), oo))

    expr = (X0**2 - 2*X0 + exp(X0)) > 10
    with pytest.raises(ValueError):
        solver(expr)

    expr = (X0 + X1 < 3)
    with pytest.raises(ValueError):
        solver(expr)

def test_factor_dnf_symbols():
    lookup = {X0:0, X1:0, X2:0, X3:1, X4:1, X5:2}

    expr = (
        (exp(X0) > 0)
            & (X0 < 10)
            & (X1 < 10)
            & NotContains(X2, FiniteSet(10, 11)))
    expr_dnf = to_dnf(expr)
    dnf = factor_dnf_symbols(expr_dnf, lookup)
    assert len(dnf) == 1
    assert dnf[0] == expr

    expr = (X0 < 1) & (X4 < 1) & (X5 < 1)
    expr_dnf = to_dnf(expr)
    dnf = factor_dnf_symbols(expr_dnf, lookup)
    assert len(dnf) == 3
    assert dnf[0] == (X0 < 1)
    assert dnf[1] == (X4 < 1)
    assert dnf[2] == (X5 < 1)

    expr = (
        (exp(X0) > 0)
            & (X0 < 10)
            & (X1 < 10)
            & Contains(X4, FiniteSet(10, 11))) \
        | (
            ((X2**2 - X2/2) < 0)
            & ((10*log(X5) + 9) > 5)
            & NotContains(X4, FiniteSet(5, 6)))

    expr_dnf = to_dnf(expr)
    dnf = factor_dnf_symbols(expr_dnf, lookup)

    assert dnf[0] == ((exp(X0) > 0)
            & (X0 < 10)
            & (X1 < 10)) \
        | ((X2**2 - X2/2) < 0)