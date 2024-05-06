import copy


class Elemento2Terminais:
    def __init__(self, z_ohm: complex, nome: str, id_barra1: int, id_barra2: int):
        if id_barra1 == id_barra2:
            raise ConnectionError(f"O elemento {nome} está em curto na barra #{id_barra1}")
        elif id_barra1 > id_barra2:
            id_barra1, id_barra2 = id_barra2, id_barra1
        self.z_ohm = z_ohm
        self.id_barra1 = id_barra1
        self.id_barra2 = id_barra2
        self.nome = nome

        self._v_base = None
        self._s_base = None

        self.z_pu = None

    @property
    def v_base(self):
        return self._v_base

    @v_base.setter
    def v_base(self, value):
        self._v_base = value

    @property
    def s_base(self):
        return self._s_base

    @s_base.setter
    def s_base(self, value):
        self._s_base = value

    def calcular_pu(self):
        self.z_pu = self.z_ohm / (self.v_base**2/self.s_base)

class Elemento3Terminais(Elemento2Terminais):
    def __init__(self, z_ohm: complex, nome: str, id_barra1: int, id_barra2: int, id_barra3=None):
        if id_barra3 is None:
            super().__init__(z_ohm, nome, id_barra1, id_barra2)
        else:
            pass


class Impedancia(Elemento2Terminais):
    def __init__(self, z_ohm: complex, nome: str, id_barra1: int, id_barra2: int):
        super().__init__(z_ohm, nome, id_barra1, id_barra2)
        # A barra não pode ser terra
        if self.id_barra1 == 0:
            self.id_barra1, self.id_barra2 = self.id_barra2, self.id_barra1


    def __str__(self):
        return (f'A impedância {self.nome} entre as barras #{self.id_barra1} e #{self.id_barra2} com '
                f'{self.z_ohm} ohms, possui valor em pu: {self.z_pu}@{self.v_base/1000}kV, {self.s_base/10**6}MVA')


class LinhaTransmissao(Impedancia):
    def __init__(self, z_densidade: complex, comprimento: float, nome: str, id_barra1: int, id_barra2: int):
        self.z_densidade = z_densidade
        self.comprimento = comprimento
        self.z_linha = z_densidade*comprimento

        super().__init__(self.z_linha, nome, id_barra1, id_barra2)

    def __str__(self):
        return (f'A linha {self.nome} entre as barras #{self.id_barra1} e #{self.id_barra2} com '
                f'{self.z_ohm} ohms, possui valor em pu: {self.z_pu}@{self.v_base/1000}kV, {self.s_base/10**6}MVA')

    def __truediv__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"O tipo dos elementos em paralelo não é igual: {type(other).__name__}")
        else:
            return LinhaTransmissao((self.z_linha*other.z_linha)/(self.z_linha + other.z_linha), 1,
                                    f"({self.nome}//{other.nome})", self.id_barra1, self.id_barra2)


class Transformador2Enro(Elemento2Terminais):
    def __init__(self, v_nom_pri: float, v_nom_sec: float, s_nom, r_pu: float, x_pu: float, adiantamento_ps: float,
                 nome: str, id_barra1: int, id_barra2: int):
        self.v_nom_pri = v_nom_pri*1000
        self.v_nom_sec = v_nom_sec*1000

        self.s_nom = s_nom*10**6

        self.z_ps_pu = complex(r_pu, x_pu)

        self.adiantamento_ps = adiantamento_ps

        z_pri = self.z_ps_pu*(v_nom_pri**2/s_nom)
        super().__init__(z_pri, nome, id_barra1, id_barra2)

    def __str__(self):
        return (f'O transformador {self.nome} entre as barras #{self.id_barra1} e #{self.id_barra2},'
                f'possui valor em pu: {self.z_pu}@{self.v_base/1000}kV, {self.s_base/10**6}MVA')

    def __truediv__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"O tipo dos elementos em paralelo não é igual: {type(other).__name__}")
        elif not (self.v_nom_pri == other.v_nom_pri and self.v_nom_sec == other.v_nom_sec):
            pass
        else:
            transformador_resultante = copy.deepcopy(self)
            transformador_resultante.z_ps_pu = (self.z_ps_pu * other.z_ps_pu)/(self.z_ps_pu + other.z_ps_pu)
            transformador_resultante.z_ohm = (self.z_ohm * other.z_ohm)/(self.z_ohm + other.z_ohm)
            transformador_resultante.nome = f"({self.nome}//{other.nome})"
            return transformador_resultante


class Transformador3Enro(Elemento3Terminais):
    def __init__(self, v_nom_pri: float, v_nom_sec: float, v_nom_ter: float, s_nom_pri: float, s_nom_sec: float,
                 r_ps_pu: float, x_ps_pu: float, r_pt_pu: float, x_pt_pu: float, r_st_pu: float, x_st_pu: float,
                 adiantamento_ps: float, adiantamento_pt: float, nome: str, id_barra1: int, id_barra2: int,
                 id_barra3=None):
        if id_barra3 is None:
            self.v_nom_pri = v_nom_pri*1000
            self.v_nom_sec = v_nom_sec*1000

            self.s_nom_pri = s_nom_pri*10**6
            self.s_nom_sec = s_nom_sec*10**6

            self.z_ps_pu = complex(r_ps_pu, x_ps_pu)

            self.adiantamento_ps = adiantamento_ps

            z_pri = self.z_ps_pu * (v_nom_pri ** 2 / s_nom_pri)
            super().__init__(z_pri, nome, id_barra1, id_barra2)

            self.id_barra3 = id_barra3

        else:
            pass

    def __str__(self):
        if self.id_barra3 is None:
            return (f'O transformador {self.nome} entre as barras #{self.id_barra1}, #{self.id_barra2} e terciário '
                    f'em aberto, possui valor em pu: {self.z_pu}@{self.v_base/1000}kV, {self.s_base/10**6}MVA')
        else:
            pass

    def __truediv__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"O tipo dos elementos em paralelo não é igual: {type(other).__name__}")
        elif not (self.v_nom_pri == other.v_nom_pri and self.v_nom_sec == other.v_nom_sec):
            pass
        else:
            transformador_resultante = copy.deepcopy(self)
            transformador_resultante.z_ps_pu = (self.z_ps_pu * other.z_ps_pu)/(self.z_ps_pu + other.z_ps_pu)
            transformador_resultante.z_ohm = (self.z_ohm * other.z_ohm)/(self.z_ohm + other.z_ohm)
            transformador_resultante.nome = f"({self.nome}//{other.nome})"
            return transformador_resultante
