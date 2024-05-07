from math import cos, sin, radians, degrees
from numpy import angle

def cpolar(modulo, angulo):
    return modulo * (1 * (cos(radians(angulo)) + 1j * sin(radians(angulo))))

def crec(x: complex):
    return abs(x), degrees(angle(x))


class PU:
    def __init__(self, valor_pu: complex, v_base: float = 1, s_base: float = 1):
        self.valor_pu = valor_pu
        self.v_base = v_base
        self.s_base = s_base

    def mudar_base(self, v_base_nova, s_base_nova):
        self.valor_pu = self.valor_pu*(self.v_base/v_base_nova)**2*(s_base_nova/self.s_base)

    def __str__(self):
        return f"{self.valor_pu}@{self.v_base/(10**3)} kV / {self.s_base/(10**6)} MVA"

    def __add__(self, other):
        if isinstance(other, PU):
            return self.valor_pu + other.valor_pu
        elif isinstance(other, int | float | complex):
            return self.valor_pu + other
        else:
            raise TypeError(f"Erro ao (+) o valor do tipo pu com valor do tipo {type(other).__name__}")

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, PU):
            return self.valor_pu - other.valor_pu
        elif isinstance(other, int | float | complex):
            return self.valor_pu - other
        else:
            raise TypeError(f"Erro ao (-) o valor do tipo pu com valor do tipo {type(other).__name__}")

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        if isinstance(other, PU):
            return self.valor_pu * other.valor_pu
        elif isinstance(other, int | float | complex):
            return self.valor_pu * other
        else:
            raise TypeError(f"Erro ao (*) o valor do tipo pu com valor do tipo {type(other).__name__}")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, PU):
            return self.valor_pu / other.valor_pu
        elif isinstance(other, int | float | complex):
            return self.valor_pu / other
        else:
            raise TypeError(f"Erro ao (/) o valor do tipo pu com valor do tipo {type(other).__name__}")

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __pow__(self, power, modulo=None):
        if isinstance(power, int):
            return self.valor_pu ** power
        else:
            raise TypeError(f"Erro ao (**) o valor do tipo pu com valor do tipo {type(power).__name__}")

    def __rpow__(self, other):
        return self.__rpow__(other)
