import numpy as np
import analisador_sep.elementos_passivos as elementos_passivos
from analisador_sep.relacoes_sep import RelacoesSEP


class Barra:
    def __init__(self, id_barra: int):
        self.id_barra = id_barra

        self._v_base = None
        self._s_base = None

        self._v_barra_volts = None
        self.v_barra_pu = None

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
    def v_barra_volts(self):
        return self._v_barra_volts

    @v_barra_volts.setter
    def v_barra_volts(self, value):
        self._v_barra_volts = value


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


                    elif isinstance(elemento, elementos_passivos.Transformador3Enro):
                        elemento: elementos_passivos.Transformador3Enro
                        v_base = self.barras[elemento.id_barra1].v_base * (elemento.v_nom_sec / elemento.v_nom_pri)

                        barra: Barra = self.barras[elemento.id_barra2]
                        barra.v_base = v_base
                        barra.s_base = s_base

                    else:

                        barra: Barra = self.barras[elemento.id_barra2]
                        barra.v_base = self.barras[elemento.id_barra1].v_base
                        barra.s_base = s_base

    def definir_pu_elementos(self, elementos: list):

        for elemento in elementos:
            elemento: elementos_passivos.Elemento2Terminais
            barra_elemento: Barra = self.barras[elemento.id_barra1]

            elemento.v_base = barra_elemento.v_base
            elemento.s_base = barra_elemento.s_base
            elemento.calcular_pu()


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
