try:
    import sympy as sp
except Exception:  # pragma: no cover
    sp = None


class SymbolicScalar(float):
    """
    Float-compatible scalar carrying a symbolic representation.

    The float value can be used as a default numeric value, while the symbolic
    expression is preserved and can be substituted numerically at solve time.
    """

    _active_substitutions = None

    def __new__(cls, value, symbol=None, _expr=None):
        obj = float.__new__(cls, float(value))
        if _expr is not None:
            obj._expr = _expr
        elif symbol is None:
            if sp is None:
                obj._expr = cls._format_number(value)
            else:
                obj._expr = sp.Float(float(value))
        else:
            if sp is None:
                obj._expr = str(symbol)
            else:
                obj._expr = sp.Symbol(str(symbol))
        return obj

    @staticmethod
    def _format_number(value):
        return "{:g}".format(float(value))

    @staticmethod
    def _is_numeric(value):
        return isinstance(value, (int, float))

    @classmethod
    def _expr_of(cls, value):
        if isinstance(value, SymbolicScalar):
            return value._expr
        if sp is None:
            return cls._format_number(value)
        if isinstance(value, int):
            return sp.Integer(value)
        return sp.Float(float(value))

    @classmethod
    def _wrap(cls, value, expr):
        return cls(float(value), _expr=expr)

    @property
    def symbol(self):
        if sp is None:
            return str(self._expr)
        return str(sp.simplify(self._expr))

    @classmethod
    def set_active_substitutions(cls, substitutions):
        cls._active_substitutions = substitutions

    @classmethod
    def get_active_substitutions(cls):
        return cls._active_substitutions

    def evaluate(self, substitutions=None):
        if substitutions is None:
            substitutions = self.get_active_substitutions()

        if substitutions is None:
            return float(self)

        if sp is None:
            symbol = self.symbol
            if symbol in substitutions:
                return float(substitutions[symbol])
            return float(self)

        formatted_subs = dict()
        for key, value in substitutions.items():
            if isinstance(key, str):
                formatted_subs[sp.Symbol(key)] = float(value)
            else:
                formatted_subs[key] = float(value)

        substituted = self._expr.subs(formatted_subs)
        return float(substituted)

    def __add__(self, other):
        if not self._is_numeric(other):
            return NotImplemented
        if sp is None:
            expr = "({} + {})".format(self._expr, self._expr_of(other))
        else:
            expr = sp.simplify(self._expr + self._expr_of(other))
        return self._wrap(float(self) + float(other), expr)

    def __radd__(self, other):
        if not self._is_numeric(other):
            return NotImplemented
        if sp is None:
            expr = "({} + {})".format(self._expr_of(other), self._expr)
        else:
            expr = sp.simplify(self._expr_of(other) + self._expr)
        return self._wrap(float(other) + float(self), expr)

    def __sub__(self, other):
        if not self._is_numeric(other):
            return NotImplemented
        if sp is None:
            expr = "({} - {})".format(self._expr, self._expr_of(other))
        else:
            expr = sp.simplify(self._expr - self._expr_of(other))
        return self._wrap(float(self) - float(other), expr)

    def __rsub__(self, other):
        if not self._is_numeric(other):
            return NotImplemented
        if sp is None:
            expr = "({} - {})".format(self._expr_of(other), self._expr)
        else:
            expr = sp.simplify(self._expr_of(other) - self._expr)
        return self._wrap(float(other) - float(self), expr)

    def __mul__(self, other):
        if not self._is_numeric(other):
            return NotImplemented
        if sp is None:
            expr = "({}*{})".format(self._expr, self._expr_of(other))
        else:
            expr = sp.simplify(self._expr * self._expr_of(other))
        return self._wrap(float(self) * float(other), expr)

    def __rmul__(self, other):
        if not self._is_numeric(other):
            return NotImplemented
        if sp is None:
            expr = "({}*{})".format(self._expr_of(other), self._expr)
        else:
            expr = sp.simplify(self._expr_of(other) * self._expr)
        return self._wrap(float(other) * float(self), expr)

    def __truediv__(self, other):
        if not self._is_numeric(other):
            return NotImplemented
        if sp is None:
            expr = "({}/{})".format(self._expr, self._expr_of(other))
        else:
            expr = sp.simplify(self._expr / self._expr_of(other))
        return self._wrap(float(self) / float(other), expr)

    def __rtruediv__(self, other):
        if not self._is_numeric(other):
            return NotImplemented
        if sp is None:
            expr = "({}/{})".format(self._expr_of(other), self._expr)
        else:
            expr = sp.simplify(self._expr_of(other) / self._expr)
        return self._wrap(float(other) / float(self), expr)

    def __neg__(self):
        if sp is None:
            expr = "(-{})".format(self._expr)
        else:
            expr = sp.simplify(-self._expr)
        return self._wrap(-float(self), expr)


def is_scalar(value):
    return isinstance(value, (int, float, SymbolicScalar))


def evaluate_scalar(value, substitutions=None):
    if isinstance(value, SymbolicScalar):
        return value.evaluate(substitutions=substitutions)
    return float(value)

