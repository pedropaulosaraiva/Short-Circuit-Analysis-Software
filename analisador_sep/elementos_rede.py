import copy

import numpy as np
import analisador_sep.elementos_passivos as elementos_passivos
from analisador_sep.relacoes_sep import RelacoesSEP
from analisador_sep.numero_pu import cpolar, crec
from math import sqrt


class Barra:
    def __init__(self, id_barra: int):
        self.id_barra = id_barra

        self._v_base = None
        self._s_base = None

        self._v_barra_pre_falta_pu = None
        self._v_barra_pos_falta_pu = None
        self.v_barra_pre_falta_volts = None
        self.v_barra_pos_falta_volts = None

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
    def v_barra_pre_falta_pu(self):
        return self._v_barra_pre_falta_pu

    @v_barra_pre_falta_pu.setter
    def v_barra_pre_falta_pu(self, value):
        # Desconsideração dos grupos vetoriais
        self._v_barra_pre_falta_pu = value
        self.v_barra_pre_falta_volts = value * self.v_base

    @property
    def v_barra_pos_falta_pu(self):
        return self._v_barra_pos_falta_pu

    @v_barra_pos_falta_pu.setter
    def v_barra_pos_falta_pu(self, value):
        self._v_barra_pos_falta_pu = value
        self.v_barra_pos_falta_volts = value * self.v_base

    @property
    def grupo_vetorial(self):
        return self._grupo_vetorial

    @grupo_vetorial.setter
    def grupo_vetorial(self, value):
        self._grupo_vetorial = value

    def calcular_tensoes_pos_falta(self):
        self.Va_pu = self.v_barra_pos_falta_pu * cpolar(1, self.grupo_vetorial)
        self.Vb_pu = self.Va_pu * cpolar(1, -120)
        self.Vc_pu = self.Va_pu * cpolar(1, 120)

        self.Va_volts = (self.v_barra_pos_falta_volts * cpolar(1, self.grupo_vetorial))
        self.Vb_volts = self.Va_volts * cpolar(1, -120)
        self.Vc_volts = self.Va_volts * cpolar(1, 120)

        self.Va_pu, self.Vb_pu, self.Vc_pu = crec(self.Va_pu), crec(self.Vb_pu), crec(self.Vc_pu)
        self.Va_volts, self.Vb_volts, self.Vc_volts = crec(self.Va_volts), crec(self.Vb_volts), crec(self.Vc_volts)


class SEP:
    def __init__(self, quantidade_barras: int, s_base: float, v_base_barra_1: float):
        self.quantidade_barras = quantidade_barras
        self.s_base = s_base*10**6

        self.v_base_barra_1 = v_base_barra_1*1000

        self.matriz_incidencia = [0]*quantidade_barras
        self.matriz_primitiva_admitancias = []
        self.matriz_admitancias = []
        self.matriz_impedacias = []

        self.elementos = []
        self.elementos_simplificados = []

        self._criar_barras()
        self._definir_barra_ref()

    def _criar_barras(self):
        # Cria uma barra de Terra com id = 0 e uma lista com os id's a partir de 1 para as barras do sistema
        barra_terra = Barra(0)
        self.barras = [barra_terra] + [Barra(id+1) for id in range(self.quantidade_barras)]

    def _definir_barra_ref(self):
        barra_ref: Barra = self.barras[1]
        barra_ref.v_base = self.v_base_barra_1
        barra_ref.s_base = self.s_base

    def adicionar_elementos(self, elementos: list):
        self.elementos = self.organizar_elementos(elementos)
        self.elementos_simplificados = RelacoesSEP.simplificar_rede_de_elementos(self.elementos, self.quantidade_barras)

    def organizar_elementos(self, elementos: list):
        "Organiza os elementos da menor barra para maior"
        elementos = sorted(elementos, key=lambda tup: (tup.id_barra1, tup.id_barra2))
        return elementos

    def criacao_matriz_incidencia(self):
        self.matriz_incidencia = RelacoesSEP.criacao_matriz_incidencia(self.elementos_simplificados,
                                                                       self.quantidade_barras)

    def definir_base_barras(self):
        elementos = self.elementos
        v_base = self.v_base_barra_1
        s_base = self.s_base
        quantidade_barras = self.quantidade_barras

        a0 = RelacoesSEP._criar_matriz_incidencia_primitiva(elementos, quantidade_barras)

        for id_barra in range(1, quantidade_barras + 1):
            for index, elemento in enumerate(elementos):
                if elemento.id_barra1 == id_barra:
                    if isinstance(elemento, elementos_passivos.Transformador2Enro):
                        elemento: elementos_passivos.Transformador2Enro
                        v_base = self.barras[elemento.id_barra1].v_base * (elemento.v_nom_sec/elemento.v_nom_pri)

                        barra: Barra = self.barras[elemento.id_barra2]
                        barra.v_base = v_base
                        barra.s_base = s_base

                        adiantamento_sp = self.barras[elemento.id_barra1].grupo_vetorial - elemento.adiantamento_ps
                        barra.grupo_vetorial = adiantamento_sp


                    elif isinstance(elemento, elementos_passivos.Transformador3Enro):
                        elemento: elementos_passivos.Transformador3Enro
                        v_base = self.barras[elemento.id_barra1].v_base * (elemento.v_nom_sec / elemento.v_nom_pri)

                        barra: Barra = self.barras[elemento.id_barra2]
                        barra.v_base = v_base
                        barra.s_base = s_base

                        adiantamento_sp = self.barras[elemento.id_barra1].grupo_vetorial - elemento.adiantamento_ps
                        barra.grupo_vetorial = adiantamento_sp
                    else:

                        barra: Barra = self.barras[elemento.id_barra2]
                        barra.v_base = self.barras[elemento.id_barra1].v_base
                        barra.s_base = s_base

                        barra.grupo_vetorial = self.barras[elemento.id_barra1].grupo_vetorial


    def definir_pu_elementos(self, elementos: list):

        for elemento in elementos:
            elemento: elementos_passivos.Elemento2Terminais
            barra_elemento: Barra = self.barras[elemento.id_barra1]


            elemento.v_base = barra_elemento.v_base
            elemento.s_base = barra_elemento.s_base
            elemento.calcular_pu()

            elemento.grupo_vetorial = barra_elemento.grupo_vetorial


    def criacao_matriz_primitiva_admitancias(self):
        y_prim = np.zeros((len(self.elementos_simplificados), len(self.elementos_simplificados)), dtype=complex)

        for index, elemento in enumerate(self.elementos_simplificados):
            elemento: elementos_passivos.Elemento2Terminais
            y_elemento = 1/elemento.z_pu
            y_prim[index][index] = y_elemento

        self.matriz_primitiva_admitancias = y_prim

    def criacao_matriz_admitancias(self):
        a_transposta = np.transpose(self.matriz_incidencia)
        y_prim = self.matriz_primitiva_admitancias
        a = self.matriz_incidencia

        y = np.matmul(np.matmul(a_transposta, y_prim), a)

        self.matriz_admitancias = y

    def criacao_matriz_impedacias(self):
        self.matriz_impedacias = np.linalg.inv(self.matriz_admitancias)

    def solve(self):
        self.criacao_matriz_incidencia()
        self.definir_base_barras()
        self.definir_pu_elementos(self.elementos)
        self.definir_pu_elementos(self.elementos_simplificados)
        self.criacao_matriz_primitiva_admitancias()
        self.criacao_matriz_admitancias()
        self.criacao_matriz_impedacias()

    def adicionar_tensoes_pre_falta(self, tensoe_t0_menos):
        self.tensoes_to_menos = np.zeros((self.quantidade_barras,1), dtype=complex)
        for index, barra in enumerate(self.barras[1:]):
            barra.v_barra_pre_falta_pu = tensoe_t0_menos[index]
            self.tensoes_to_menos[index][0] = barra.v_barra_pre_falta_pu

        barra_terra: Barra = self.barras[0]
        barra_terra.v_barra_pre_falta_pu = 0

    #
    # Cálculos de curto circuito
    #

    def refereciar_vto_menos_no_curto(self, id_barra_curto: int):
        barra_curto: Barra = self.barras[id_barra_curto]
        grupo_referencial = barra_curto.grupo_vetorial
        self.grupo_referencial_curto = grupo_referencial

        # Mudança do referencial em vto_menos
        for index, barra in enumerate(self.barras[1:]):

            self.tensoes_to_menos[index][0] = self.tensoes_to_menos[index][0] * cpolar(1, grupo_referencial)

            barra.grupo_vetorial = barra.grupo_vetorial - grupo_referencial
            barra.v_barra_pre_falta_pu = self.tensoes_to_menos[index][0]


    def referenciar_grupo_elementos_no_curto(self, elementos):
        # Mudança do referencial nos grupos vetoriais dos elementos
        for elemento in elementos:
            elemento: elementos_passivos.Elemento2Terminais

            elemento.grupo_vetorial = elemento.grupo_vetorial - self.grupo_referencial_curto
    def calcular_matriz_corrente_curto(self, id_barra_curto: int, z_f_ohm=0):
        barra_curto: Barra = self.barras[id_barra_curto]

        v_base = barra_curto.v_base
        s_base = barra_curto.s_base
        z_f_pu = z_f_ohm/(v_base**2/s_base)

        self.refereciar_vto_menos_no_curto(id_barra_curto)

        tensao_t0_menos = barra_curto.v_barra_pre_falta_pu
        zth_barra_curto = self.matriz_impedacias[id_barra_curto - 1][id_barra_curto - 1]

        self.corrente_curto = (tensao_t0_menos)/(z_f_pu + zth_barra_curto)

        matriz_corrente_curto = np.zeros((self.quantidade_barras,1), dtype=complex)
        matriz_corrente_curto[id_barra_curto - 1][0] = -self.corrente_curto
        return matriz_corrente_curto

    def calcular_tensoes_pos_falta(self, id_barra_curto: int, z_f_ohm=0):
        matriz_corrente_curto = self.calcular_matriz_corrente_curto(id_barra_curto, z_f_ohm)
        self.tensoes_to_mais = self.tensoes_to_menos + np.matmul(self.matriz_impedacias, matriz_corrente_curto)

        for index, barra in enumerate(self.barras[1:]):
            barra.v_barra_pos_falta_pu = self.tensoes_to_mais[index]

        barra_terra: Barra = self.barras[0]
        barra_terra.v_barra_pos_falta_pu = 0

    def atribuir_correntes_pos_falta(self, elementos):
        self.referenciar_grupo_elementos_no_curto(elementos)

        for elemento in elementos:
            elemento: elementos_passivos.Elemento2Terminais
            barra_elemento_inicial: Barra = self.barras[elemento.id_barra1]
            barra_elemento_final: Barra = self.barras[elemento.id_barra2]

            elemento.v_pos_falta_pu = (barra_elemento_inicial.v_barra_pos_falta_pu -
                                       barra_elemento_final.v_barra_pos_falta_pu)

            elemento.calcular_pos_falta_corrente()

        for barra in self.barras[1:]:
            barra.calcular_tensoes_pos_falta()

    def criar_curto_simetrico(self, id_barra_curto: int, z_f_ohm=0):
        self.id_barra_curto = id_barra_curto
        self.z_f_ohm = z_f_ohm
        self.calcular_tensoes_pos_falta(id_barra_curto, z_f_ohm)
        self.atribuir_correntes_pos_falta(self.elementos)

        return copy.deepcopy(self)
