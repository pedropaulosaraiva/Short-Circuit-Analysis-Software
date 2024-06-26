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
        self.v_pos_falta_pu_gv = None
        self.i_pos_falta_pu = None
        self.i_pos_falta_pu_gv = None

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
        self.v_pos_falta_pu_gv = value * cpolar(1, self.grupo_vetorial)
        self.i_pos_falta_pu = value/self.z_pu
        self.i_pos_falta_pu_gv = self.i_pos_falta_pu * cpolar(1, self.grupo_vetorial)

    @property
    def grupo_vetorial(self):
        return self._grupo_vetorial

    @grupo_vetorial.setter
    def grupo_vetorial(self, value):
        self._grupo_vetorial = value

    def calcular_pu(self):
        self.z_pu = self.z_ohm / (self.v_base**2/self.s_base)

    def calcular_pos_falta_corrente_assimetrica(self, I_z, I_p, I_n):
        self.Ia_pu = I_z + I_p + I_n
        self.Ib_pu = I_z + I_p * cpolar(1, -120) + I_n * cpolar(1, 120)
        self.Ic_pu = I_z + I_p * cpolar(1, 120) + I_n * cpolar(1, -120)

        self.Ia_amp = self.Ia_pu * (self.s_base/(self.v_base*sqrt(3)))
        self.Ib_amp = self.Ib_pu * (self.s_base/(self.v_base*sqrt(3)))
        self.Ic_amp = self.Ic_pu * (self.s_base/(self.v_base*sqrt(3)))


class Elemento3Terminais(Elemento2Terminais):
    def __init__(self, z_ohm: complex, nome: str, id_barra1: int, id_barra2: int, id_barra3=None):
        if id_barra3 is None:
            super().__init__(z_ohm, nome, id_barra1, id_barra2)
        else:
            pass


class Impedancia(Elemento2Terminais):
    def __init__(self, z_ohm: complex, z_ohm_0: complex,nome: str, id_barra1: int, id_barra2: int):
        super().__init__(z_ohm, nome, id_barra1, id_barra2)
        self.z_ohm_0 = z_ohm_0
        # A barra não pode ser terra
        if self.id_barra1 == 0:
            self.id_barra1, self.id_barra2 = self.id_barra2, self.id_barra1

    def transformar_seq0(self):
        self.z_ohm = self.z_ohm_0

    def __truediv__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"O tipo dos elementos em paralelo não é igual: {type(other).__name__}")
        else:
            z_ohm = (self.z_ohm * other.z_ohm) / (self.z_ohm + other.z_ohm)

            impedancia_resultante = Impedancia(z_ohm, 0j, f"({self.nome}//{other.nome})",
                                               self.id_barra1, self.id_barra2)
            return impedancia_resultante

class LinhaTransmissao(Impedancia):
    def __init__(self, z_densidade_1: complex, z_densidade_0: complex, comprimento: float, nome: str,
                 id_barra1: int, id_barra2: int, z_densidade_mutua_0=0.0+0j):
        self.z_densidade_1 = z_densidade_1
        self.z_densidade_0 = z_densidade_0
        self.comprimento = comprimento

        self.z_linha_1 = z_densidade_1 * comprimento
        self.z_linha_0 = z_densidade_0 * comprimento

        super().__init__(self.z_linha_1, self.z_linha_0, nome, id_barra1, id_barra2)
        self.z_mutua_0 = z_densidade_mutua_0 * self.comprimento

    def transformar_seq0(self):
        self.z_ohm = self.z_linha_0 + self.z_mutua_0


    def __truediv__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"O tipo dos elementos em paralelo não é igual: {type(other).__name__}")
        else:
            z_linha = (self.z_ohm * other.z_ohm) / (self.z_ohm + other.z_ohm)
            
            linhaTransmissao_resultante = LinhaTransmissao(z_linha, 0j, 1,
                                                           f"({self.nome}//{other.nome})", self.id_barra1,
                                                           self.id_barra2)
            return linhaTransmissao_resultante


class Transformador2Enro(Elemento2Terminais):
    def __init__(self, v_nom_pri: float, v_nom_sec: float, s_nom, r_pu: float, x_pu: float, adiantamento_ps: float,
                 nome: str, lig: str, id_barra1: int, id_barra2: int):
        self.v_nom_pri = v_nom_pri*1000
        self.v_nom_sec = v_nom_sec*1000

        self.s_nom = s_nom*10**6

        self.z_ps_pu = complex(r_pu, x_pu)
        self.lig = lig

        self.adiantamento_ps = adiantamento_ps

        z_pri = self.z_ps_pu*(v_nom_pri**2/s_nom)
        super().__init__(z_pri, nome, id_barra1, id_barra2)

    def transformar_seq0(self):
        if self.lig == 'Dyg':
            # Reflexão da impedancia
            self.z_ohm = self.z_ohm * (self.v_nom_sec/self.v_nom_pri)**2
            self.id_barra1 = self.id_barra2
            self.id_barra2 = 0
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
            self.z_st_pu = complex(r_st_pu, x_st_pu) * (self.s_nom_pri/self.s_nom_sec)
            self._calcular_modelo_estrela()

            self.lig = lig

            self.adiantamento_ps = adiantamento_ps

            z_pri = self.z_ps_pu * (v_nom_pri ** 2 / s_nom_pri)
            super().__init__(z_pri, nome, id_barra1, id_barra2)

            self.id_barra3 = id_barra3
        else:
            pass
        
    def _calcular_modelo_estrela(self):
        self.z_p_pu = (1 / 2) * (self.z_ps_pu + self.z_pt_pu - self.z_st_pu)
        self.z_s_pu = (1 / 2) * (self.z_ps_pu - self.z_pt_pu + self.z_st_pu)
        self.z_t_pu = (1 / 2) * (-self.z_ps_pu + self.z_pt_pu + self.z_st_pu)

    def transformar_seq0(self):
        if self.lig == 'Ygdd':
            self.id_barra2 = 0
            self.z_pu_base_tr = self.z_p_pu + (((self.z_s_pu) * (self.z_t_pu)) / ((self.z_s_pu) + (self.z_t_pu)))
            self.z_ohm = self.z_pu_base_tr * (self.v_nom_pri ** 2 / self.s_base)
        else:
            pass


    def __truediv__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"O tipo dos elementos em paralelo não é igual: {type(other).__name__}")
        elif not (self.v_nom_pri == other.v_nom_pri and self.v_nom_sec == other.v_nom_sec):
            pass
        else:
            transformador_resultante = copy.deepcopy(self)
            # Impedâncias
            transformador_resultante.z_ps_pu = (self.z_ps_pu * other.z_ps_pu)/(self.z_ps_pu + other.z_ps_pu)
            transformador_resultante.z_pt_pu = (self.z_pt_pu * other.z_pt_pu) / (self.z_pt_pu + other.z_pt_pu)
            transformador_resultante.z_st_pu = (self.z_st_pu * other.z_st_pu) / (self.z_st_pu + other.z_st_pu)
            transformador_resultante._calcular_modelo_estrela()
            
            transformador_resultante.z_ohm = (self.z_ohm * other.z_ohm)/(self.z_ohm + other.z_ohm)
            transformador_resultante.nome = f"({self.nome}//{other.nome})"
            return transformador_resultante

class TransformadorAterramento(Impedancia):

    def __init__(self, z_pu_at: complex, nome: str, id_barra1: int, v_nom: float, s_nom: float, z_n_pu=None):
        self.z_pu_0 = z_pu_at

        self.v_nom_pri = v_nom*1000
        self.s_nom = s_nom*10**6

        self.z_ohm_0 = z_pu_at * (v_nom ** 2 / s_nom)

        super().__init__(float('inf'), self.z_ohm_0, nome, id_barra1, 0)
