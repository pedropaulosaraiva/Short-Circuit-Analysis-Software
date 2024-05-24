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
        print(f'If = {self.sep.corrente_curto[0]}<{self.sep.corrente_curto[1]}º')
        print("===============================================")
        print("Tensões nas barras:")
        for barra in barras[1:]:
            print(barra)
        print("========================")
        print("Correntes nos elementos:")
        for elemento in elementos:
            elemento: Elemento2Terminais
            elemento.print_curto_simetrico()


    def salvar_matriz_impedancia_csv(self):
        z: np.array = self.sep.matriz_impedacias

        np.savetxt('matriz_impedancias.csv', z, delimiter=' & ', fmt='%3.5e', newline=' \\\\\n')

    
            
    
    def salvar_circuito_simetrico(self):
        barras = self.sep.barras
        elementos = self.sep.elementos
        print(f"Exibindo resultados do curto simétrico em #{self.sep.id_barra_curto}, com impedância de falta"
              f" {self.sep.z_f_ohm} Ohms")
        print(f'If = {self.sep.corrente_curto[0]}<{self.sep.corrente_curto[1]}º')
        print("===============================================")
        print("Tensões nas barras:")
        with open('dog_breeds_reversed.txt', 'w') as writer:
            for barra in barras[1:]:
                print(barra)

        for barra in barras[1:]:
            print(barra)
        print("========================")
        print("Correntes nos elementos:")
        for elemento in elementos:
            elemento: Elemento2Terminais
            elemento.print_curto_simetrico()


class Interface_latex(Iresultados):
    
    def __init__(self, sep: SEP, sep_curto_4: SEP, sep_curto_8: SEP):
        super().__init__(sep)
        self.sep_4 = sep_curto_4
        self.sep_8 = sep_curto_8
    
    def matriz_barras_a(self, indx_1, indx_2):
        barras = self.sep.barras
        V_barras = np.zeros((18, (indx_2 - indx_1) * 2), dtype=float)
        for n, sep in enumerate([self.sep, self.sep_4, self.sep_8]):
            barras = sep.barras
            indx = 0
            for barra in barras[indx_1:indx_2]:
                # Pu

                V_barras[6 * n + 0][indx] = barra.Va_pu[0]
                V_barras[6 * n + 0][indx + 1] = barra.Va_pu[1]

                V_barras[6 * n + 1][indx] = barra.Vb_pu[0]
                V_barras[6 * n + 1][indx + 1] = barra.Vb_pu[1]

                V_barras[6 * n + 2][indx] = barra.Vc_pu[0]
                V_barras[6 * n + 2][indx + 1] = barra.Vc_pu[1]

                #Si
                V_barras[6 * n + 3][indx] = barra.Va_volts[0]/1000
                V_barras[6 * n + 3][indx + 1] = barra.Va_volts[1]

                V_barras[6 * n + 4][indx] = barra.Vb_volts[0]/1000
                V_barras[6 * n + 4][indx + 1] = barra.Vb_volts[1]

                V_barras[6 * n + 5][indx] = barra.Vc_volts[0]/1000
                V_barras[6 * n + 5][indx + 1] = barra.Vc_volts[1]

                indx = indx + 2
        return V_barras

    def salvar_matriz_barras_latex(self, idx_1,idx_2):
        B = self.matriz_barras_a(idx_1,idx_2)
        np.savetxt('matriz_barras.csv', B, delimiter=' & ', fmt='%4.4f', newline=' \\\\\n')
