from analisador_sep.elementos_rede import SEP
from analisador_sep.elementos_passivos import Elemento2Terminais
import numpy as np

class Iresultados:
    def __init__(self, sep: SEP):
        self.sep = sep

    def diagrama_impedancias(self):
        elementos = self.sep.elementos
        print("Exibindo valores do diagrama de impedancias:")
        print("============================================")
        for elemento in elementos:
            print(elemento)
        print("============================================\n")

    def matriz_admitancias(self, decimais=None):
        y: np.array = self.sep.matriz_admitancias
        print("Exibindo matriz de aditâncias:")
        print("==============================")
        if decimais is None:
            print(y)
        else:
            print(np.around(y,decimals=decimais))
        print("==============================\n")

    def matriz_impedancias(self, decimais=None):
        z: np.array = self.sep.matriz_impedacias
        print("Exibindo matriz de impedâncias:")
        print("===============================")
        if decimais is None:
            print(z)
        else:
            print(np.around(z, decimals=decimais))
        print("===============================\n")

    def curto_circuito_simetrico(self):
        barras = self.sep.barras
        elementos = self.sep.elementos
        print(f"Exibindo resultados do curto simétrico em #{self.sep.id_barra_curto}, com impedância de falta"
              f" {self.sep.z_f_ohm} Ohms")
        print(f'If = {self.sep.corrente_curto}')
        print("===============================================")
        print("Tensões nas barras:")
        for barra in barras[1:]:
            print(barra)
        print("========================")
        print("Correntes nos elementos:")
        for elemento in elementos:
            elemento: Elemento2Terminais
            elemento.print_curto_simetrico()


