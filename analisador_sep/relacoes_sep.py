import copy

from analisador_sep.elementos_passivos import (Elemento2Terminais, Elemento3Terminais, Impedancia, LinhaTransmissao,
                                               Transformador2Enro, Transformador3Enro, TransformadorAterramento)
import analisador_sep.elementos_ativos as elementos_ativos
import numpy as np
from collections import defaultdict



class RelacoesSEP:
    #
    # Funções de topologia da rede
    #
    @staticmethod
    def _criar_matriz_incidencia_primitiva(elementos: list, quantidade_barras: int) -> np.array:
        """
        Cria uma matriz de incidencia sem levar em conta os ramos em paralelo, ou seja, com possibilidade de haver
        linhas iguais
        """
        # criação de uma matriz nula elementos x barras
        a0 = np.zeros((len(elementos), quantidade_barras))

        for indx, elemento in enumerate(elementos):
            if isinstance(elemento, Elemento2Terminais):
                if elemento.id_barra2 == 0:
                    coluna_barra_inicial = (elemento.id_barra1 - 1)

                    a0[indx][coluna_barra_inicial] = 1
                else:
                    coluna_barra_inicial = (elemento.id_barra1 - 1)
                    coluna_barra_final = (elemento.id_barra2 - 1)

                    a0[indx][coluna_barra_inicial] = 1
                    a0[indx][coluna_barra_final] = -1
            elif isinstance(elemento, Elemento3Terminais):
                pass

        return a0

    @staticmethod
    def criacao_matriz_incidencia(elementos_simplificados: list, quantidade_barras: int) -> np.array:
        # Cria de uma matriz nula elementos x barras
        a = np.zeros((len(elementos_simplificados),quantidade_barras))

        # Remove as linhas duplicadas e cria um array
        for indx, elemento in enumerate(elementos_simplificados):
            if isinstance(elemento, Elemento2Terminais):
                if elemento.id_barra2 == 0:
                    coluna_barra_inicial = (elemento.id_barra1 - 1)

                    a[indx][coluna_barra_inicial] = 1
                else:
                    coluna_barra_inicial = (elemento.id_barra1 - 1)
                    coluna_barra_final = (elemento.id_barra2 - 1)

                    a[indx][coluna_barra_inicial] = 1
                    a[indx][coluna_barra_final] = -1
            elif isinstance(elemento, Elemento3Terminais):
                pass

        return a

    #
    # Funções de caracteristicas da Rede
    #

    @staticmethod
    def simplificar_rede_de_elementos(elementos_originais: list, quantidade_barras: int) -> list:
        elementos = copy.deepcopy(elementos_originais)

        a0 = RelacoesSEP._criar_matriz_incidencia_primitiva(elementos, quantidade_barras)
        d = defaultdict(list)
        for i, elem in enumerate(a0):
            d[str(elem)].append(i)

        index_elementos_em_paralelos = [v for v in d.values()]

        elementos_simplificados = []
        for paralelo in index_elementos_em_paralelos:
            if len(paralelo) == 1:
                elementos_simplificados.append(elementos[paralelo[0]])
            else:  # Há elementos em paralelo na conexão entre as barras
                if isinstance(elementos[paralelo[0]], LinhaTransmissao):
                    linha_resultante: LinhaTransmissao = elementos[paralelo[0]]

                    for index in paralelo[1:]:
                        linha_resultante /= elementos[index]

                    elementos_simplificados.append(linha_resultante)
                elif isinstance(elementos[paralelo[0]], Transformador3Enro):
                    trans_resultante: Transformador3Enro = elementos[paralelo[0]]

                    for index in paralelo[1:]:
                        trans_resultante /= elementos[index]

                    elementos_simplificados.append(trans_resultante)
                else:
                    # Elemento genérico em caso de transformadores em paralelo com redes (exemplo em seq 0)
                    elemento = elementos[paralelo[0]]
                    impedancia_resultante = Impedancia(elemento.z_ohm,0j,f"{elemento.nome}",
                                                       elemento.id_barra1, elemento.id_barra2)

                    for index in paralelo[1:]:
                        elemento = elementos[index]
                        impedancia_elemento = Impedancia(elemento.z_ohm, 0j, f"{elemento.nome}",
                                                           elemento.id_barra1, elemento.id_barra2)

                        impedancia_resultante /= impedancia_elemento

                    elementos_simplificados.append(impedancia_resultante)

        return elementos_simplificados

    def criacao_matriz_admitancias(self):
        pass


if __name__ == '__main__':
    elementos = [LinhaTransmissao(1+1j, 2,'a', 1, 2),
                 LinhaTransmissao(2+2j,1,'a', 1, 2),
                 LinhaTransmissao(3j, 1,'a', 2, 3),
                 LinhaTransmissao(3j,1,'a', 2, 3),
                 LinhaTransmissao(1j, 3,'a', 2, 3),
                 LinhaTransmissao(5+1j,1,'a', 3, 4),
                 LinhaTransmissao(5 + 5j, 1,'a', 2, 4),
                 Transformador3Enro(230, 69,13.8, 100, 40,
                                                       0.0398,8.3214, 0.0756, 15.5472,
                                                       0.0401, 5.0101, 30, 30,
                                                       'a',4, 5),
                 Transformador3Enro(230, 69, 13.8, 100, 40,
                                                       0.0398, 8.3214, 0.0756, 15.5472,
                                                       0.0401, 5.0101, 30, 30,
                                                       'a',4, 5),
                 LinhaTransmissao(4, 1, 'a',5, 6),
                 ]
    quantidade_barras = 6

    elementos_simplificados = RelacoesSEP.simplificar_rede_de_elementos(elementos, quantidade_barras)
    for elemento in elementos_simplificados:
        print(elemento.z_ohm)
    print(RelacoesSEP.criacao_matriz_incidencia(elementos_simplificados, quantidade_barras))
