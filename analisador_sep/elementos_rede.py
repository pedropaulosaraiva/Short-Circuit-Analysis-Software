import numpy as np


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

        self._criar_barras()
        self._definir_barra_ref()

    def _criar_barras(self):
        # Cria uma barra de Terra com id = 0 e uma lista com os id's a partir de 1 para as barras do sistema
        barra_terra = Barra(0)
        self.barras = [barra_terra] + [Barra(id+1) for id in range(self.quantidade_barras)]

    def _definir_barra_ref(self):
        barra_ref: Barra = self.barras[self.id_barra_ref]
        barra_ref.v_base = self.v_base_ref
