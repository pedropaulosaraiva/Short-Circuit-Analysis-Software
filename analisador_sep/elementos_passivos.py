import numpy as np
from elementos_rede import Barra


class Passivo1Porta:
    def __init__(self, id_barra1: int, id_barra2: int):
        self.id_barra1 = id_barra1
        self.id_barra2 = id_barra2

        self.v_base = None
        self.s_base = None
        self.v_volts = None
        self.v_pu = None
        self.i_amp = None
        self.i_pu = None


class LinhaTransmissao:
    def __init__(self, z_densidade: complex, comprimento: float, id_barra1: int, id_barra2: int):
        self.z_densidade = z_densidade
        self.comprimento = comprimento
        self.z_linha = z_densidade*comprimento

        self.id_barra1 = id_barra1
        self.id_barra2 = id_barra2


class Transformador2Enro:
    def __init__(self, v_nom_pri: float, v_nom_sec: float, s_nom, r_pu: float, x_pu: float, adiantamento_ps: float,
                 id_barra1: int, id_barra2: int):
        self.v_nom_pri = v_nom_pri
        self.v_nom_sec = v_nom_sec

        self.s_nom = s_nom

        self.z_ps_pu = complex(r_pu, x_pu)

        self.adiantamento_ps = adiantamento_ps

        self.id_barra1 = id_barra1
        self.id_barra2 = id_barra2

        self._definicao_z_ohm()

    def _definicao_z_ohm(self):
        z_nom_pri_base = (self.v_nom_pri**2)/self.s_nom
        z_nom_sec_base = (self.v_nom_sec**2)/self.s_nom
        self.z_pri_ohm = self.z_ps_pu * z_nom_pri_base
        self.z_sec_ohm = self.z_ps_pu * z_nom_sec_base

    def mudar_base_z_pu(self, V_base, S_base):
        pass



class Transformador3Enro:
    def __init__(self, v_nom_pri: float, v_nom_sec: float, v_nom_ter: float, s_nom_pri: float, s_nom_sec: float,
                 r_ps_pu: float, x_ps_pu: float, r_pt_pu: float, x_pt_pu: float, r_st_pu: float, x_st_pu: float,
                 adiantamento_ps: float, adiantamento_pt: float, id_barra1: int, id_barra2: int, id_barra3: int = 0):
        self.v_nom_pri = v_nom_pri
        self.v_nom_sec = v_nom_sec
        self.v_nom_ter = v_nom_ter

        self.s_nom_pri = s_nom_pri
        self.s_nom_sec = s_nom_sec
        self.s_nom_ter = (s_nom_pri - s_nom_sec)

        self.z_ps_pu = complex(r_ps_pu, x_ps_pu)
        self.z_ps_pu = complex(r_pt_pu, x_pt_pu)
        self.z_st_pu = complex(r_st_pu, x_st_pu)

        self.adiantamento_ps = adiantamento_ps
        self.adiantamento_pt = adiantamento_pt

        self.id_barra1 = id_barra1
        self.id_barra2 = id_barra2
        self.id_barra3 = id_barra3
