import numpy as np
import elementos_passivos
import elementos_ativos
from numero_pu import Zona
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
    def __init__(self, quantidade_barras: int, s_base: float, id_barra_ref: int, v_base_ref: float):
        self.quantidade_barras = quantidade_barras
        self.s_base = s_base
        self.id_barra_ref = id_barra_ref
        self.v_base_ref = v_base_ref

        self.matriz_incidencia = [0]*quantidade_barras
        self.matriz_primitiva_admitancias = []
        self.matriz_admitancias = []

        self._criar_barras()
        self._definir_barra_ref()

    def _criar_barras(self):
        # Cria uma barra de Terra com id = 0 e uma lista com os id's a partir de 1 para as barras do sistema
        barra_terra = Barra(0)
        self.barras = [barra_terra] + [Barra(id+1) for id in range(self.quantidade_barras)]

    def _definir_barra_ref(self):
        barra_ref: Barra = self.barras[self.id_barra_ref]
        barra_ref.v_base = self.v_base_ref
        barra_ref.s_base = self.s_base

    def adicionar_elementos(self, elementos: list):
        self.elementos = elementos
        self.elementos_simplificados = RelacoesSEP.simplificar_rede_de_elementos(elementos, self.quantidade_barras)
    def criacao_matriz_incidencia(self):
        self.matriz_incidencia = RelacoesSEP.criacao_matriz_incidencia(self.elementos, self.quantidade_barras)

    def definir_base_barras(self, elementos: list, v_base: float, s_base: float, quantidade_barras: int):
        a0 = RelacoesSEP._criar_matriz_incidencia_primitiva(elementos, quantidade_barras)

        for id_barra in range(1, quantidade_barras):
            for index, elemento in enumerate(elementos):
                if (a0[index][id_barra] == -a0[index][id_barra + 1]):
                    if isinstance(elemento, elementos_passivos.Transformador2Enro):
                        elemento: elementos_passivos.Transformador2Enro
                        v_base = v_base*(elemento.v_nom_sec/elemento.v_nom_pri)

                        barra: Barra = self.barras[id_barra + 1]
                        barra.v_base = v_base
                        barra.s_base = s_base

                        break
                    elif isinstance(elemento, elementos_passivos.Transformador3Enro):
                        elemento: elementos_passivos.Transformador3Enro
                        v_base = v_base * (elemento.v_nom_sec / elemento.v_nom_pri)

                        barra: Barra = self.barras[id_barra + 1]
                        barra.v_base = v_base
                        barra.s_base = s_base
                        break
                    else:
                        barra: Barra = self.barras[id_barra + 1]
                        barra.v_base = v_base
                        barra.s_base = s_base
                        break

    def definir_pu_elementos(self, elementos: list):

        for elemento in elementos:
            elemento: elementos_passivos.Passivo1Porta
            barra_elemento: Barra = self.barras[elemento.id_barra1]

            elemento.v_base = barra_elemento.v_base
            elemento.s_base = barra_elemento.s_base
            elemento.calcular_pu()


    def criacao_matriz_primitiva_admitancias(self):
        pass
