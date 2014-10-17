from blaze.expr import *
from blaze.expr.broadcast2 import *
from blaze.compatibility import builtins
from toolz import isdistinct

x = Symbol('x', '5 * 3 * int32')
xx = Symbol('xx', 'int32')

y = Symbol('y', '5 * 3 * int32')
yy = Symbol('yy', 'int32')

a = Symbol('a', 'int32')


def test_broadcast_basic():
    b = Broadcast((x, y), (xx, yy), xx + yy)

    assert b.shape == x.shape
    assert b.schema == (xx + yy).dshape

    assert eval(str(b)).isidentical(b)


def test_scalar_symbols():
    exprs = [x, y]
    scalars = scalar_symbols(exprs)

    assert len(scalars) == len(exprs)
    assert isdistinct([s._name for s in scalars])
    assert builtins.all(s.dshape == e.schema for s, e in zip(scalars, exprs))


def test_broadcast_function():
    expr =  Pow(Add(x, Mult(2, y)), 2)  # (x + (2 * y)) ** 2
    b = broadcast(expr, [x, y])
    xx, yy = b._scalars
    assert b._scalar_expr.isidentical((xx + (2 * yy)) ** 2)

    # A different set of leaves
    b = broadcast(expr, [x, Mult(2, y)])
    xx, yy = b._scalars
    assert b._scalar_expr.isidentical((xx + yy) ** 2)


t = Symbol('t', 'var * {x: int, y: int, z: int}')


def test_tabular_case():
    expr = Add(x, Mult(y, 2))

    b = broadcast(expr, [t])
    tt, = b._scalars

    assert b._scalar_expr.isidentical(tt.x + tt.y * 2)
