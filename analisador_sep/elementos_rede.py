import numpy as np
import elementos_passivos
import elementos_ativos


class Barra:
    def __init__(self, id_barra: int):
        self.id_barra = id_barra
        self._v_base = None
        self._v_barra_volts = None
        self.v_barra_pu = None

    @property
    def v_base(self):
        return self._v_base

    @v_base.setter
    def v_base(self, value):
        self._v_base = value

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

    def adicionar_elementos(self, elementos: list):
        self.elementos = elementos


        for indx, elemento in enumerate(elementos):
            coluna_negativa = (elemento.id_barra1 - 1)
            coluna_positiva = (elemento.id_barra2 - 1)

            A0[indx][coluna_negativa] = -1
            A0[indx][coluna_positiva] = 1

    def criacao_matriz_incidencia(self, elementos: list):
        # criação de uma matriz nula elementos x barras
        A0 = [[0] * self.quantidade_barras] * len(elementos)

        for indx, elemento in enumerate(elementos):
            if isinstance(elemento, elementos_passivos.LinhaTransmissao | elementos_passivos.Transformador2Enro):
                coluna_negativa = (elemento.id_barra1 - 1)
                coluna_positiva = (elemento.id_barra2 - 1)

                A0[indx][coluna_negativa] = -1
                A0[indx][coluna_positiva] = 1
            elif isinstance(elemento, elementos_passivos.Transformador3Enro):
                coluna_negativa_p = (elemento.id_barra1 - 1)
                coluna_positiva_s = (elemento.id_barra2 - 1)
                coluna_positiva_t = (elemento.id_barra3 - 1)

                A0[indx][coluna_negativa_p] = -1
                A0[indx][coluna_positiva_s] = 1
                A0[indx][coluna_positiva_t] = 1
            elif isinstance(elemento, elementos_ativos.EquivalenteRede):
                coluna_positiva = (elemento.id_barra2 - 1)

                A0[indx][coluna_positiva] = -1

    def criacao_matriz_primitiva_admitancias(self):
        pass
