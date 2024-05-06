from analisador_sep.elementos_rede import SEP
import numpy as np

class Iresultados:
    def __init__(self, sep: SEP):
        self.sep = sep

    def diagrama_impedancias(self):
        elementos = self.sep.elementos
        print("Exibindo valores do diagrama de impedancias:")
        print("===================")
        for elemento in elementos:
            print(elemento)
        print("===================")

    def matriz_admitancias(self, decimais=None):
        y: np.array = self.sep.matriz_admitancias
        print("Exibindo matriz de aditâncias:")
        print("===================")
        if decimais is None:
            print(y)
        else:
            print(np.around(y,decimals=decimais))
        print("===================")

    def matriz_impedancias(self, decimais=None):
        z: np.array = self.sep.matriz_impedacias
        print("Exibindo matriz de impedâncias:")
        print("===================")
        if decimais is None:
            print(z)
        else:
            print(np.around(z, decimals=decimais))
        print("===================")
