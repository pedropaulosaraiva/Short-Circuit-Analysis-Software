import copy
from math import sqrt
from analisador_sep.numero_pu import cpolar, crec

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

        self._v_pos_falta_pu = None
        self.v_pos_falta_volts = None
        self.i_pos_falta_pu = None
        self.i_pos_falta_amp = None

        self._grupo_vetorial = 0

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

    @property
    def v_pos_falta_pu(self):
        return self._v_pos_falta_pu

    @v_pos_falta_pu.setter
    def v_pos_falta_pu(self, value):
        self._v_pos_falta_pu = value
        self.v_pos_falta_volts = value * self.v_base
        self.i_pos_falta_pu = value/self.z_pu
        self.i_pos_falta_amp = self.i_pos_falta_pu * (self.s_base/(sqrt(3) * self.v_base))

    @property
    def grupo_vetorial(self):
        return self._grupo_vetorial

    @grupo_vetorial.setter
    def grupo_vetorial(self, value):
        self._grupo_vetorial = value

    def calcular_pu(self):
        self.z_pu = self.z_ohm / (self.v_base**2/self.s_base)

    def calcular_pos_falta_corrente(self):
        self.Ia_pu = self.i_pos_falta_pu * cpolar(1, self.grupo_vetorial)
        self.Ib_pu = self.Ia_pu * cpolar(1,-120)
        self.Ic_pu = self.Ia_pu * cpolar(1,120)

        self.Ia_amp = self.i_pos_falta_amp * cpolar(1, self.grupo_vetorial)
        self.Ib_amp = self.Ia_amp * cpolar(1,-120)
        self.Ic_amp = self.Ia_amp * cpolar(1,120)

        self.Ia_pu, self.Ib_pu, self.Ic_pu = crec(self.Ia_pu), crec(self.Ib_pu), crec(self.Ic_pu)
        self.Ia_amp, self.Ib_amp, self.Ic_amp = crec(self.Ia_amp), crec(self.Ib_amp), crec(self.Ic_amp)



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




class LinhaTransmissao(Impedancia):
    def __init__(self, z_densidade: complex, comprimento: float, nome: str, id_barra1: int, id_barra2: int):
        self.z_densidade = z_densidade
        self.comprimento = comprimento
        self.z_linha = z_densidade*comprimento

        super().__init__(self.z_linha, nome, id_barra1, id_barra2)


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
                 adiantamento_ps: float, adiantamento_pt: float, nome: str,lig: str, id_barra1: int, id_barra2: int,
                 id_barra3=None, z_n_pu=None):
        if id_barra3 is None:
            self.v_nom_pri = v_nom_pri*1000
            self.v_nom_sec = v_nom_sec*1000
            self.v_nom_ter = v_nom_ter*1000

            self.s_nom_pri = s_nom_pri*10**6
            self.s_nom_sec = s_nom_sec*10**6
            self.s_nom_ter = self.s_nom_pri - self.s_nom_sec

            self.z_ps_pu = complex(r_ps_pu, x_ps_pu)
            self.z_pt_pu = complex(r_pt_pu, x_pt_pu)
            self.z_st_pu = complex(r_st_pu, x_st_pu)

            self.lig = lig

            self.adiantamento_ps = adiantamento_ps

            z_pri = self.z_ps_pu * (v_nom_pri ** 2 / s_nom_pri)
            super().__init__(z_pri, nome, id_barra1, id_barra2)

            self.id_barra3 = id_barra3

        else:
            pass

    def transformar_seq0(self):
        # Mudança de base para a barra do primario
        self.z_ps_pu_base = self.z_ps_pu * ((self.v_nom_pri/self.v_base)**2)*(self.s_base/self.s_nom_pri)
        self.z_pt_pu_base = self.z_pt_pu * ((self.v_nom_pri/self.v_base)**2)*(self.s_base/self.s_nom_pri)
        self.z_st_pu_base_n_refletida = self.z_st_pu * ((self.v_nom_sec/self.v_base)**2)*(self.s_base/self.s_nom_sec)
        # Reflexão para o primário de z_st
        self.z_st_pu_base = self.z_st_pu_base_n_refletida*((self.v_nom_pri/self.v_nom_sec)**2)

        self.z_p_pu = (1 / 2) * (self.z_ps_pu_base + self.z_pt_pu_base - self.z_st_pu_base)
        self.z_s_pu = (1 / 2) * (self.z_ps_pu_base - self.z_pt_pu_base + self.z_st_pu_base)
        self.z_t_pu = (1 / 2) * (-self.z_ps_pu_base + self.z_pt_pu_base + self.z_st_pu_base)

        if self.lig == 'Ygdd':
            self.id_barra2 = 0
            self.z_pu = self.z_p_pu + (((self.z_s_pu) * (self.z_t_pu)) / ((self.z_s_pu) + (self.z_t_pu)))
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
