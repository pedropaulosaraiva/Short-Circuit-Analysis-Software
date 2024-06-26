import copy

import numpy as np
from math import sqrt

from analisador_sep.elementos_passivos import Elemento2Terminais, Transformador2Enro, Transformador3Enro
from analisador_sep.relacoes_sep import RelacoesSEP
from analisador_sep.numero_pu import cpolar, crec


class Barra:
    def __init__(self, id_barra: int):
        self.id_barra = id_barra

        self._v_base = None
        self._s_base = None

        self._v_barra_pre_falta_pu = None
        self._v_barra_pos_falta_pu = None
        self.v_barra_pre_falta_volts = None

        self.v_barra_pos_falta_pu_gv = None

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
        self.v_barra_pos_falta_pu_gv = value * cpolar(1, self.grupo_vetorial)

    @property
    def grupo_vetorial(self):
        return self._grupo_vetorial

    @grupo_vetorial.setter
    def grupo_vetorial(self, value):
        self._grupo_vetorial = value

    def calcular_tensoes_pos_falta_assimetricas(self, V_z, V_p, V_n):
        self.Va_pu = V_z + V_p + V_n
        self.Vb_pu = V_z + V_p * cpolar(1, -120) + V_n * cpolar(1, 120)
        self.Vc_pu = V_z + V_p * cpolar(1, 120) + V_n * cpolar(1, -120)

        self.Va_volts = self.Va_pu * self.v_base
        self.Vb_volts = self.Vb_pu * self.v_base
        self.Vc_volts = self.Vc_pu * self.v_base


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

        # Impede a criação de sequencias para os próprios diagramas de sequência
        if type(self) is SEP:
            self._sep_seq_positiva = SEP_positivo(quantidade_barras, s_base, v_base_barra_1)
            self._sep_seq_negativa = SEP_negativo(quantidade_barras, s_base, v_base_barra_1)
            self._sep_seq_zero = SEP_0(quantidade_barras, s_base, v_base_barra_1)

        # Parâmetros de Curto
        self._corrente_curto = None
        self.z_f_pu = None

        self._criar_barras()
        self._definir_barra_ref()

        
    @property
    def sep_seq_positiva(self):
        return self._sep_seq_positiva
    
    @sep_seq_positiva.setter
    def sep_seq_positiva(self, sep):
        self._sep_seq_positiva = sep

    @property
    def sep_seq_negativa(self):
        return self._sep_seq_negativa

    @sep_seq_negativa.setter
    def sep_seq_negativa(self, sep):
        self._sep_seq_negativa = sep

    @property
    def sep_seq_zero(self):
        return self._sep_seq_zero

    @sep_seq_zero.setter
    def sep_seq_zero(self, sep):
        self._sep_seq_zero = sep
        
    @property
    def corrente_curto(self):
        return self._corrente_curto
    
    @corrente_curto.setter
    def corrente_curto(self, corrente):
        self._corrente_curto = corrente
        

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
        elementos_organizados = sorted(elementos, key=lambda elemento: (elemento.id_barra1, elemento.id_barra2))
        return elementos_organizados

    def criacao_matriz_incidencia(self):
        self.matriz_incidencia = RelacoesSEP.criacao_matriz_incidencia(self.elementos_simplificados,
                                                                       self.quantidade_barras)

    def definir_base_barras(self):
        v_base = self.v_base_barra_1

        for elemento in self.elementos_simplificados:
            elemento: Elemento2Terminais
            index_barra_adjacente = elemento.id_barra2

            if isinstance(elemento, (Transformador2Enro, Transformador3Enro)):
                v_base = self.barras[elemento.id_barra1].v_base * (elemento.v_nom_sec / elemento.v_nom_pri)

                barra: Barra = self.barras[elemento.id_barra2]

                barra.v_base = v_base
                barra.s_base = self.s_base
            else:
                barra: Barra = self.barras[index_barra_adjacente]
                barra.v_base = v_base
                barra.s_base = self.s_base

    def definir_grupo_vetorial_barras(self):
        for elemento in self.elementos_simplificados:
            elemento: Elemento2Terminais
            index_barra_anterior = elemento.id_barra1
            index_barra_posterior = elemento.id_barra2

            if isinstance(elemento, (Transformador2Enro, Transformador3Enro)):
                adiantamento_tr_ps = elemento.adiantamento_ps

                barra: Barra = self.barras[index_barra_posterior]

                barra.grupo_vetorial = self.barras[index_barra_anterior].grupo_vetorial - adiantamento_tr_ps
            else:
                barra: Barra = self.barras[index_barra_posterior]

                barra.grupo_vetorial = self.barras[index_barra_anterior].grupo_vetorial


    def definir_pu_elementos(self, elementos: list):

        for elemento in elementos:
            elemento: Elemento2Terminais
            barra_elemento: Barra = self.barras[elemento.id_barra1]


            elemento.v_base = barra_elemento.v_base
            elemento.s_base = barra_elemento.s_base
            elemento.calcular_pu()

            elemento.grupo_vetorial = barra_elemento.grupo_vetorial


    def criacao_matriz_primitiva_admitancias(self):
        y_prim = np.zeros((len(self.elementos_simplificados), len(self.elementos_simplificados)), dtype=complex)

        for index, elemento in enumerate(self.elementos_simplificados):
            elemento: Elemento2Terminais
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

    def solve_z_barra_sequencias(self):
        elementos_seq_positiva = copy.deepcopy(self.elementos)
        self.sep_seq_positiva.adicionar_elementos(elementos_seq_positiva)
        self.sep_seq_positiva.copiar_barras(self.barras)
        self.sep_seq_positiva.solve_z_barra()

        elementos_seq_negativa = copy.deepcopy(self.elementos)
        self.sep_seq_negativa.adicionar_elementos(elementos_seq_negativa)
        self.sep_seq_negativa.copiar_barras(self.barras)
        self.sep_seq_negativa.solve_z_barra()

        elementos_seq_zero = copy.deepcopy(self.elementos)
        self.sep_seq_zero.adicionar_elementos(elementos_seq_zero)
        self.sep_seq_zero.copiar_barras(self.barras)
        self.sep_seq_zero.solve_z_barra()

    def solve_z_barra(self):
        self.criacao_matriz_incidencia()

        self.definir_base_barras()
        self.definir_grupo_vetorial_barras()

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

        self.tensoes_to_menos_nref = copy.deepcopy(self.tensoes_to_menos)
        barra_terra: Barra = self.barras[0]
        barra_terra.v_barra_pre_falta_pu = 0

    #
    # Cálculos de curto circuito
    #

    def referenciar_sistema_no_curto(self, id_barra_curto: int, z_f_ohm=0j):
        # Barra de curto
        self.id_barra_curto = id_barra_curto
        barra_curto: Barra = self.barras[self.id_barra_curto]
        self.z_f_ohm = z_f_ohm

        # Mudança do referencial de t0_menos e grupos das barras do sistema para o curto
        self.grupo_referencial_curto = barra_curto.grupo_vetorial
        for index, barra in enumerate(self.barras[1:]):
            self.tensoes_to_menos[index][0] = (self.tensoes_to_menos[index][0] *
                                               cpolar(1, self.grupo_referencial_curto))
            barra.v_barra_pre_falta_pu = self.tensoes_to_menos[index][0]

            barra.grupo_vetorial = barra.grupo_vetorial - self.grupo_referencial_curto

        # Mudança do referencial dos elementos do sistema para o curto
        for elemento in self.elementos:
            elemento: Elemento2Terminais

            elemento.grupo_vetorial = elemento.grupo_vetorial - self.grupo_referencial_curto
        for elemento in self.elementos_simplificados:
            elemento: Elemento2Terminais

            elemento.grupo_vetorial = elemento.grupo_vetorial - self.grupo_referencial_curto

    def calcular_corrente_curto_trifasica(self):
        # Cálculo da impedância de falta em pu
        barra_curto: Barra = self.barras[self.id_barra_curto]

        v_base = barra_curto.v_base
        s_base = barra_curto.s_base
        self.z_f_pu = self.z_f_ohm / (v_base ** 2 / s_base)

        # Cálculo da corrente de curto
        tensao_t0_menos = barra_curto.v_barra_pre_falta_pu
        zth_barra_curto = self.matriz_impedacias[self.id_barra_curto - 1][self.id_barra_curto - 1]

        self.corrente_curto = (tensao_t0_menos) / (self.z_f_pu + zth_barra_curto)

    def calcular_corrente_curto_fase_terra(self):
        # Cálculo da impedância de falta em pu
        barra_curto: Barra = self.barras[self.id_barra_curto]

        v_base = barra_curto.v_base
        s_base = barra_curto.s_base
        self.z_f_pu = self.z_f_ohm / (v_base ** 2 / s_base)

        # Cálculo da corrente de curto
        tensao_t0_menos = barra_curto.v_barra_pre_falta_pu

        zth_barra_positivo = self.sep_seq_positiva.matriz_impedacias[self.id_barra_curto - 1][self.id_barra_curto - 1]
        zth_barra_negativo = self.sep_seq_negativa.matriz_impedacias[self.id_barra_curto - 1][self.id_barra_curto - 1]
        zth_barra_zero = self.sep_seq_zero.matriz_impedacias[self.id_barra_curto - 1][self.id_barra_curto - 1]

        Ia0 = (tensao_t0_menos) / (3*self.z_f_pu+zth_barra_positivo+zth_barra_negativo+zth_barra_zero)
        Ia1 = (tensao_t0_menos) / (3*self.z_f_pu+zth_barra_positivo+zth_barra_negativo+zth_barra_zero)
        Ia2 = (tensao_t0_menos) / (3*self.z_f_pu+zth_barra_positivo+zth_barra_negativo+zth_barra_zero)

        self.corrente_curto = Ia0, Ia1, Ia2

    def calcular_corrente_curto_fase_fase(self):
        # Cálculo da impedância de falta em pu
        barra_curto: Barra = self.barras[self.id_barra_curto]

        v_base = barra_curto.v_base
        s_base = barra_curto.s_base
        self.z_f_pu = self.z_f_ohm / (v_base ** 2 / s_base)

        # Cálculo da corrente de curto
        tensao_t0_menos = barra_curto.v_barra_pre_falta_pu

        zth_barra_positivo = self.sep_seq_positiva.matriz_impedacias[self.id_barra_curto - 1][self.id_barra_curto - 1]
        zth_barra_negativo = self.sep_seq_negativa.matriz_impedacias[self.id_barra_curto - 1][self.id_barra_curto - 1]
        zth_barra_zero = self.sep_seq_zero.matriz_impedacias[self.id_barra_curto - 1][self.id_barra_curto - 1]

        Ia0 = 0
        Ia1 = (tensao_t0_menos) / (self.z_f_pu + zth_barra_positivo + zth_barra_negativo)
        Ia2 = -Ia1

        self.corrente_curto = Ia0, Ia1, Ia2

    def calcular_corrente_curto_fase_fase_terra(self):
        # Cálculo da impedância de falta em pu
        barra_curto: Barra = self.barras[self.id_barra_curto]

        v_base = barra_curto.v_base
        s_base = barra_curto.s_base
        self.z_f_pu = self.z_f_ohm / (v_base ** 2 / s_base)

        # Cálculo da corrente de curto
        tensao_t0_menos = barra_curto.v_barra_pre_falta_pu

        zth_barra_positivo = self.sep_seq_positiva.matriz_impedacias[self.id_barra_curto - 1][self.id_barra_curto - 1]
        zth_barra_negativo = self.sep_seq_negativa.matriz_impedacias[self.id_barra_curto - 1][self.id_barra_curto - 1]
        zth_barra_zero = self.sep_seq_zero.matriz_impedacias[self.id_barra_curto - 1][self.id_barra_curto - 1]

        Ia1 = ((tensao_t0_menos) /
                               (zth_barra_positivo+((zth_barra_negativo*(zth_barra_zero+3*self.z_f_pu))/
                                                    (zth_barra_negativo+3*self.z_f_pu+zth_barra_zero))))
        Ia2 = -Ia1 * ((zth_barra_zero+3*self.z_f_pu) / (zth_barra_negativo + 3 * self.z_f_pu + zth_barra_zero))
        Ia0 = -Ia1 * ((zth_barra_negativo) / (zth_barra_negativo+3*self.z_f_pu+zth_barra_zero))


        self.corrente_curto = Ia0, Ia1, Ia2

    def calcular_matriz_corrente_curto(self):
        matriz_corrente_curto = np.zeros((self.quantidade_barras,1), dtype=complex)
        matriz_corrente_curto[self.id_barra_curto - 1][0] = -self.corrente_curto
        return matriz_corrente_curto

    def calcular_tensoes_pos_falta(self):
        matriz_corrente_curto = self.calcular_matriz_corrente_curto()

        self.tensoes_to_mais = self.tensoes_to_menos + np.matmul(self.matriz_impedacias, matriz_corrente_curto)

        for index, barra in enumerate(self.barras[1:]):
            barra.v_barra_pos_falta_pu = self.tensoes_to_mais[index]

            if type(self) is SEP_negativo:
                barra.calcular_tensoes_pos_falta_assimetricas(0, 0, barra.v_barra_pos_falta_pu_gv)
            elif type(self) is SEP_0:
                barra.calcular_tensoes_pos_falta_assimetricas(barra.v_barra_pos_falta_pu_gv, 0,0)
            else:
                barra.calcular_tensoes_pos_falta_assimetricas(0, barra.v_barra_pos_falta_pu_gv, 0)

        barra_terra: Barra = self.barras[0]
        barra_terra.v_barra_pos_falta_pu = 0

    def atribuir_correntes_pos_falta(self, elementos):

        for elemento in elementos:
            elemento: Elemento2Terminais
            barra_elemento_inicial: Barra = self.barras[elemento.id_barra1]
            barra_elemento_final: Barra = self.barras[elemento.id_barra2]

            elemento.v_pos_falta_pu = (barra_elemento_inicial.v_barra_pos_falta_pu -
                                       barra_elemento_final.v_barra_pos_falta_pu)


            if type(self) is SEP_negativo:
                elemento.calcular_pos_falta_corrente_assimetrica(0, 0, elemento.i_pos_falta_pu_gv)
            elif type(self) is SEP_0:
                elemento.calcular_pos_falta_corrente_assimetrica(elemento.i_pos_falta_pu_gv, 0, 0)
            else:
                elemento.calcular_pos_falta_corrente_assimetrica(0, elemento.i_pos_falta_pu_gv, 0)

    def criar_curto_trifasico(self, id_barra_curto: int, z_f_ohm=0):

        self.referenciar_sistema_no_curto(id_barra_curto, z_f_ohm)
        self.calcular_corrente_curto_trifasica()

        self.calcular_tensoes_pos_falta()
        self.atribuir_correntes_pos_falta(self.elementos)

        return copy.deepcopy(self)

    def criar_curto_fase_terra(self, id_barra_curto: int, z_f_ohm=0):

        sep_ft = copy.deepcopy(self)

        sep_ft.referenciar_sistema_no_curto(id_barra_curto, z_f_ohm)

        sep_ft.calcular_corrente_curto_fase_terra()

        sep_ft.sep_seq_zero.corrente_curto = sep_ft.corrente_curto[0]
        sep_ft.sep_seq_positiva.corrente_curto = sep_ft.corrente_curto[1]
        sep_ft.sep_seq_negativa.corrente_curto = sep_ft.corrente_curto[2]
        sep_ft.corrente_curto = sep_ft.corrente_curto[0] + sep_ft.corrente_curto[1] + sep_ft.corrente_curto[2]

        sep_ft.criar_curto_assimetrico(id_barra_curto, z_f_ohm)

        return copy.deepcopy(sep_ft)

    def criar_curto_fase_fase(self, id_barra_curto: int, z_f_ohm=0):

        sep_ff = copy.deepcopy(self)

        sep_ff.referenciar_sistema_no_curto(id_barra_curto, z_f_ohm)

        sep_ff.calcular_corrente_curto_fase_fase()

        sep_ff.sep_seq_zero.corrente_curto = sep_ff.corrente_curto[0]
        sep_ff.sep_seq_positiva.corrente_curto = sep_ff.corrente_curto[1]
        sep_ff.sep_seq_negativa.corrente_curto = sep_ff.corrente_curto[2]
        sep_ff.corrente_curto = sep_ff.corrente_curto[0] + sep_ff.corrente_curto[1] + sep_ff.corrente_curto[2]

        sep_ff.criar_curto_assimetrico(id_barra_curto, z_f_ohm)

        return sep_ff

    def criar_curto_fase_fase_terra(self, id_barra_curto: int, z_f_ohm=0):

        sep_fft = copy.deepcopy(self)
        
        sep_fft.referenciar_sistema_no_curto(id_barra_curto, z_f_ohm)

        sep_fft.calcular_corrente_curto_fase_fase_terra()

        sep_fft.sep_seq_zero.corrente_curto = sep_fft.corrente_curto[0]
        sep_fft.sep_seq_positiva.corrente_curto = sep_fft.corrente_curto[1]
        sep_fft.sep_seq_negativa.corrente_curto = sep_fft.corrente_curto[2]
        sep_fft.corrente_curto = sep_fft.corrente_curto[0] + sep_fft.corrente_curto[1] + sep_fft.corrente_curto[2]

        sep_fft.criar_curto_assimetrico(id_barra_curto, z_f_ohm)

        return sep_fft

    def abrir_uma_fase(self, id_aberto_1: int, id_aberto_2: int):
        
        sep_1a = copy.deepcopy(self)
        
        sep_1a.is_umafase = True
        sep_1a.id_aberto_1 = id_aberto_1
        sep_1a.id_aberto_2 = id_aberto_2
        sep_1a.sep_seq_positiva.id_aberto_1 = id_aberto_1
        sep_1a.sep_seq_positiva.id_aberto_2 = id_aberto_2
        sep_1a.sep_seq_negativa.id_aberto_1 = id_aberto_1
        sep_1a.sep_seq_negativa.id_aberto_2 = id_aberto_2
        sep_1a.sep_seq_zero.id_aberto_1 = id_aberto_1
        sep_1a.sep_seq_zero.id_aberto_2 = id_aberto_2

        sep_1a.referenciar_sistema_no_curto(id_aberto_1)

        sep_1a.sep_seq_positiva.adicionar_tensoes_pre_falta(sep_1a.tensoes_to_menos_nref)
        sep_1a.sep_seq_positiva.referenciar_sistema_no_curto(id_aberto_1)

        sep_1a.sep_seq_negativa.adicionar_tensoes_pre_falta(sep_1a.tensoes_to_menos_nref * 0)
        sep_1a.sep_seq_negativa.referenciar_sistema_no_curto(id_aberto_1)

        sep_1a.sep_seq_zero.adicionar_tensoes_pre_falta(sep_1a.tensoes_to_menos_nref * 0)
        sep_1a.sep_seq_zero.referenciar_sistema_no_curto(id_aberto_1)
        sep_1a._calcular_zmn_aberto(id_aberto_1, id_aberto_2)

        return sep_1a

    def abrir_duas_fases(self, id_aberto_1: int, id_aberto_2: int):

        sep_2a = copy.deepcopy(self)
        
        sep_2a.is_umafase = False
        sep_2a.id_aberto_1 = id_aberto_1
        sep_2a.id_aberto_2 = id_aberto_2
        sep_2a.sep_seq_positiva.id_aberto_1 = id_aberto_1
        sep_2a.sep_seq_positiva.id_aberto_2 = id_aberto_2
        sep_2a.sep_seq_negativa.id_aberto_1 = id_aberto_1
        sep_2a.sep_seq_negativa.id_aberto_2 = id_aberto_2
        sep_2a.sep_seq_zero.id_aberto_1 = id_aberto_1
        sep_2a.sep_seq_zero.id_aberto_2 = id_aberto_2

        sep_2a.referenciar_sistema_no_curto(id_aberto_1)

        sep_2a.sep_seq_positiva.adicionar_tensoes_pre_falta(sep_2a.tensoes_to_menos_nref)
        sep_2a.sep_seq_positiva.referenciar_sistema_no_curto(id_aberto_1)

        sep_2a.sep_seq_negativa.adicionar_tensoes_pre_falta(sep_2a.tensoes_to_menos_nref * 0)
        sep_2a.sep_seq_negativa.referenciar_sistema_no_curto(id_aberto_1)

        sep_2a.sep_seq_zero.adicionar_tensoes_pre_falta(sep_2a.tensoes_to_menos_nref * 0)
        sep_2a.sep_seq_zero.referenciar_sistema_no_curto(id_aberto_1)

        sep_2a._calcular_zmn_aberto(id_aberto_1, id_aberto_2)

        return sep_2a


    def _calcular_zmn_aberto(self, id_aberto_1: int, id_aberto_2: int):
        Z_LT_mn_0 = 1 / (self.sep_seq_zero.matriz_admitancias[id_aberto_1 - 1][id_aberto_2 - 1])
        Z_LT_mn_1 = 1 / (self.sep_seq_positiva.matriz_admitancias[id_aberto_1 - 1][id_aberto_2 - 1])
        Z_LT_mn_2 = 1 / (self.sep_seq_negativa.matriz_admitancias[id_aberto_1 - 1][id_aberto_2 - 1])

        Z_TH_mn_0 = (self.sep_seq_zero.matriz_impedacias[id_aberto_1 - 1][id_aberto_1 - 1] +
                     self.sep_seq_zero.matriz_impedacias[id_aberto_2 - 1][id_aberto_2 - 1] -
                     2 * self.sep_seq_zero.matriz_impedacias[id_aberto_1 - 1][id_aberto_2 - 1])
        Z_TH_mn_1 = (self.sep_seq_positiva.matriz_impedacias[id_aberto_1 - 1][id_aberto_1 - 1] +
                     self.sep_seq_positiva.matriz_impedacias[id_aberto_2 - 1][id_aberto_2 - 1] -
                     2 * self.sep_seq_positiva.matriz_impedacias[id_aberto_1 - 1][id_aberto_2 - 1])
        Z_TH_mn_2 = (self.sep_seq_negativa.matriz_impedacias[id_aberto_1 - 1][id_aberto_1 - 1] +
                     self.sep_seq_negativa.matriz_impedacias[id_aberto_2 - 1][id_aberto_2 - 1] -
                     2 * self.sep_seq_negativa.matriz_impedacias[id_aberto_1 - 1][id_aberto_2 - 1])

        self.Z_mn_0 = -((Z_LT_mn_0)**2/(Z_TH_mn_0-Z_LT_mn_0))
        self.Z_mn_1 = -((Z_LT_mn_1) ** 2 / (Z_TH_mn_1 - Z_LT_mn_1))
        self.Z_mn_2 = -((Z_LT_mn_2) ** 2 / (Z_TH_mn_2 - Z_LT_mn_2))

        self.I_mn_to_mais = (self.tensoes_to_menos[id_aberto_1 - 1] - self.tensoes_to_menos[id_aberto_2 - 1]) / Z_LT_mn_1
        
        if self.is_umafase:
            self._tensoes_assimetricas_uma_fase()
        else:
            self._tensoes_assimetricas_duas_fases()
        
        self.I_m_0 = -self.Va_0 / Z_LT_mn_0
        self.I_n_0 = self.Va_0 / Z_LT_mn_0
        self.I_m_1 = -self.Va_1 / Z_LT_mn_1
        self.I_n_1 = self.Va_1 / Z_LT_mn_1
        self.I_m_2 = -self.Va_2 / Z_LT_mn_2
        self.I_n_2 = self.Va_2 / Z_LT_mn_2

        matriz_corrente_curto_0 = np.zeros((self.quantidade_barras, 1), dtype=complex)
        matriz_corrente_curto_0[id_aberto_1 - 1][0] = -self.I_m_0
        matriz_corrente_curto_0[id_aberto_2][0] = -self.I_n_0

        matriz_corrente_curto_1 = np.zeros((self.quantidade_barras, 1), dtype=complex)
        matriz_corrente_curto_1[id_aberto_1 - 1][0] = -self.I_m_1
        matriz_corrente_curto_1[id_aberto_2 - 1][0] = -self.I_n_1

        matriz_corrente_curto_2 = np.zeros((self.quantidade_barras, 1), dtype=complex)
        matriz_corrente_curto_2[id_aberto_1 - 1][0] = -self.I_m_2
        matriz_corrente_curto_2[id_aberto_2 - 1][0] = -self.I_n_2

        self.sep_seq_zero.tensoes_to_mais = np.matmul(self.sep_seq_zero.matriz_impedacias,
                                                                              matriz_corrente_curto_0)
        self.sep_seq_positiva.tensoes_to_mais = self.tensoes_to_menos+np.matmul(self.sep_seq_positiva.matriz_impedacias,
                                                                              matriz_corrente_curto_1)
        self.sep_seq_negativa.tensoes_to_mais= np.matmul(self.sep_seq_negativa.matriz_impedacias,
                                                                              matriz_corrente_curto_2)

        for sep in [self.sep_seq_zero, self.sep_seq_positiva, self.sep_seq_negativa]:
            for index, barra in enumerate(sep.barras[1:]):
                barra.v_barra_pos_falta_pu = sep.tensoes_to_mais[index]

                if sep is SEP_negativo:
                    barra.calcular_tensoes_pos_falta_assimetricas(0, 0, barra.v_barra_pos_falta_pu_gv)
                elif sep is SEP_0:
                    barra.calcular_tensoes_pos_falta_assimetricas(barra.v_barra_pos_falta_pu_gv, 0, 0)
                else:
                    barra.calcular_tensoes_pos_falta_assimetricas(0, barra.v_barra_pos_falta_pu_gv, 0)
        barra_terra: Barra = self.barras[0]
        barra_terra.v_barra_pos_falta_pu = 0

        self.atribuir_tensoes_pos_falta_assimetricas()

        
    def _tensoes_assimetricas_uma_fase(self):
        I_1 = (self.I_mn_to_mais *
               (self.Z_mn_1 / (self.Z_mn_1 + ((self.Z_mn_0 * self.Z_mn_2)/(self.Z_mn_0 +self.Z_mn_2)))))
        self.Va_0 = I_1 * ((self.Z_mn_0 * self.Z_mn_2)/(self.Z_mn_0 +self.Z_mn_2))
        self.Va_1 = self.Va_0
        self.Va_2 = self.Va_0

    def _tensoes_assimetricas_duas_fases(self):
        I_1 = (self.I_mn_to_mais *
               (self.Z_mn_1 / (self.Z_mn_1 + self.Z_mn_2 + self.Z_mn_0)))

        self.Va_0 = -I_1 * ((self.Z_mn_0))
        self.Va_1 = I_1 * ((self.Z_mn_0 + self.Z_mn_2))
        self.Va_2 = -I_1 * ((self.Z_mn_2))
        
    

    def criar_curto_assimetrico(self, id_barra_curto: int, z_f_ohm=0):
        self.sep_seq_positiva.adicionar_tensoes_pre_falta(self.tensoes_to_menos_nref)
        self.sep_seq_positiva.referenciar_sistema_no_curto(id_barra_curto, z_f_ohm)
        self.sep_seq_positiva.alterar_v_base_p_monofasico()
        self.sep_seq_positiva.calcular_tensoes_pos_falta()
        self.sep_seq_positiva.atribuir_correntes_pos_falta(self.sep_seq_positiva.elementos)

        self.sep_seq_negativa.adicionar_tensoes_pre_falta(self.tensoes_to_menos_nref * 0)
        self.sep_seq_negativa.referenciar_sistema_no_curto(id_barra_curto, z_f_ohm)
        self.sep_seq_negativa.alterar_v_base_p_monofasico()
        self.sep_seq_negativa.calcular_tensoes_pos_falta()
        self.sep_seq_negativa.atribuir_correntes_pos_falta(self.sep_seq_negativa.elementos)

        self.sep_seq_zero.adicionar_tensoes_pre_falta(self.tensoes_to_menos_nref * 0)
        self.sep_seq_zero.referenciar_sistema_no_curto(id_barra_curto, z_f_ohm)
        self.sep_seq_zero.alterar_v_base_p_monofasico()
        self.sep_seq_zero.calcular_tensoes_pos_falta()
        self.sep_seq_zero.atribuir_correntes_pos_falta(self.sep_seq_zero.elementos)

        self.atribuir_tensoes_pos_falta_assimetricas()
        self.atribuir_correntes_pos_falta_assimetricas()


    def atribuir_tensoes_pos_falta_assimetricas(self):
        for index, barra in enumerate(self.barras[1:], start=1):
            v_barra_positiva = self.sep_seq_positiva.barras[index].Va_pu
            v_barra_negativa = self.sep_seq_negativa.barras[index].Va_pu
            v_barra_zero= self.sep_seq_zero.barras[index].Va_pu
            barra.calcular_tensoes_pos_falta_assimetricas(v_barra_zero, v_barra_positiva, v_barra_negativa)

    def atribuir_correntes_pos_falta_assimetricas(self):
        for index, elemento in enumerate(self.elementos):
            i_elemento_positiva = self.sep_seq_positiva.elementos[index].Ia_pu
            i_elemento_negativa = self.sep_seq_negativa.elementos[index].Ia_pu
            i_elemento_zero = self.sep_seq_zero.elementos[index].Ia_pu

            elemento.calcular_pos_falta_corrente_assimetrica(i_elemento_zero, i_elemento_positiva, i_elemento_negativa)


        
class SEP_positivo(SEP):

    def __init__(self, quantidade_barras: int, s_base: float, v_base_barra_1: float):
        super().__init__(quantidade_barras, s_base, v_base_barra_1)

    def copiar_barras(self, barras: list[Barra]):
        self.barras = copy.deepcopy(barras)

    def definir_base_barras(self):
        pass

    def definir_grupo_vetorial_barras(self):
        pass

    def alterar_v_base_p_monofasico(self):
        for barra in self.barras:
            # barra.v_base = barra.v_base/sqrt(3)
            pass


class SEP_negativo(SEP):

    def __init__(self, quantidade_barras: int, s_base: float, v_base_barra_1: float):
        super().__init__(quantidade_barras, s_base, v_base_barra_1)

    def adicionar_elementos(self, elementos: list):
        # Inversão dos grupos vetoriais
        for elemento in elementos:
            if isinstance(elemento, (Transformador2Enro, Transformador3Enro)):
                elemento.adiantamento_ps = -elemento.adiantamento_ps
            else:
                pass
        
        self.elementos = self.organizar_elementos(elementos)
        self.elementos_simplificados = RelacoesSEP.simplificar_rede_de_elementos(self.elementos, self.quantidade_barras)

    def copiar_barras(self, barras: list[Barra]):
        self.barras = copy.deepcopy(barras)

    def definir_base_barras(self):
        pass

    def alterar_v_base_p_monofasico(self):
        for barra in self.barras:
            # barra.v_base = barra.v_base/sqrt(3)
            pass

class SEP_0(SEP):

    def __init__(self, quantidade_barras: int, s_base: float, v_base_barra_1: float):
        super().__init__(quantidade_barras, s_base, v_base_barra_1)
        
    def adicionar_elementos(self, elementos: list):
        # Seleciona o esquema em seq. zero
        for elemento in elementos:
            elemento.transformar_seq0()

            if isinstance(elemento, (Transformador2Enro, Transformador3Enro)):
                elemento.adiantamento_ps = 0
            else:
                pass

        self.elementos = self.organizar_elementos(elementos)
        self.elementos_simplificados = RelacoesSEP.simplificar_rede_de_elementos(self.elementos, self.quantidade_barras)

    def copiar_barras(self, barras: list[Barra]):
        self.barras = copy.deepcopy(barras)

    def definir_base_barras(self):
        pass

    def definir_grupo_vetorial_barras(self):
        for barra in self.barras:
            barra: Barra
            barra.grupo_vetorial = 0

    def alterar_v_base_p_monofasico(self):
        for barra in self.barras:
            # barra.v_base = barra.v_base/sqrt(3)
            pass