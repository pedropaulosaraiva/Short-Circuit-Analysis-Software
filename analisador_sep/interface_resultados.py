from analisador_sep.elementos_rede import SEP
from analisador_sep.elementos_passivos import Elemento2Terminais
from analisador_sep.numero_pu import crec
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
        corrente_curto = crec(self.sep.corrente_curto)
        print(f"Exibindo resultados do curto simétrico em #{self.sep.id_barra_curto}, com impedância de falta"
              f" {self.sep.z_f_ohm} Ohms")
        print(f'If = {corrente_curto[0]}<{corrente_curto[1]}º')
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

        z_3 = z[0:9, 0:3]
        z_7 = z[0:9, 3:6]
        z_9 = z[0:9, 6:9]
        print(z)
        print(z_3)
        np.savetxt('matriz_impedancias3.csv', z_3, delimiter=' & ', fmt='%3.4e', newline=' \\\\\n')
        np.savetxt('matriz_impedancias7.csv', z_7, delimiter=' & ', fmt='%3.4e', newline=' \\\\\n')
        np.savetxt('matriz_impedancias9.csv', z_9, delimiter=' & ', fmt='%3.4e', newline=' \\\\\n')

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
    
    def matriz_elementos(self, indx_1, indx_2):
        I_elementos = np.zeros((18, (indx_2 - indx_1) * 2), dtype=float)
        for n, sep in enumerate([self.sep, self.sep_4, self.sep_8]):
            elementos = sep.elementos
            indx = 0
            for elemento in elementos[indx_1:indx_2]:
                # Pu

                I_elementos[6 * n + 0][indx] = elemento.Ia_pu[0]
                I_elementos[6 * n + 0][indx + 1] = elemento.Ia_pu[1]

                I_elementos[6 * n + 1][indx] = elemento.Ib_pu[0]
                I_elementos[6 * n + 1][indx + 1] = elemento.Ib_pu[1]

                I_elementos[6 * n + 2][indx] = elemento.Ic_pu[0]
                I_elementos[6 * n + 2][indx + 1] = elemento.Ic_pu[1]

                # Si
                I_elementos[6 * n + 3][indx] = elemento.Ia_amp[0]
                I_elementos[6 * n + 3][indx + 1] = elemento.Ia_amp[1]

                I_elementos[6 * n + 4][indx] = elemento.Ib_amp[0]
                I_elementos[6 * n + 4][indx + 1] = elemento.Ib_amp[1]

                I_elementos[6 * n + 5][indx] = elemento.Ic_amp[0]
                I_elementos[6 * n + 5][indx + 1] = elemento.Ic_amp[1]

                indx = indx + 2
        return I_elementos

    def matriz_elementos_v_2(self, indx_1, indx_2):
        I_elementos = np.zeros((18, 4), dtype=float)
        for n, sep in enumerate([self.sep, self.sep_4, self.sep_8]):
            elementos = sep.elementos
            indx = 0
            for elemento in [elementos[indx_1], elementos[indx_2]]:
                # Pu

                I_elementos[6 * n + 0][indx] = elemento.Ia_pu[0]
                I_elementos[6 * n + 0][indx + 1] = elemento.Ia_pu[1]

                I_elementos[6 * n + 1][indx] = elemento.Ib_pu[0]
                I_elementos[6 * n + 1][indx + 1] = elemento.Ib_pu[1]

                I_elementos[6 * n + 2][indx] = elemento.Ic_pu[0]
                I_elementos[6 * n + 2][indx + 1] = elemento.Ic_pu[1]

                # Si
                I_elementos[6 * n + 3][indx] = elemento.Ia_amp[0]
                I_elementos[6 * n + 3][indx + 1] = elemento.Ia_amp[1]

                I_elementos[6 * n + 4][indx] = elemento.Ib_amp[0]
                I_elementos[6 * n + 4][indx + 1] = elemento.Ib_amp[1]

                I_elementos[6 * n + 5][indx] = elemento.Ic_amp[0]
                I_elementos[6 * n + 5][indx + 1] = elemento.Ic_amp[1]

                indx = indx + 2
        return I_elementos

    def salvar_matriz_barras_latex(self, idx_1,idx_2):
        B = self.matriz_barras_a(idx_1,idx_2)
        np.savetxt('matriz_barras.csv', B, delimiter=' & ', fmt='%4.4f', newline=' \\\\\n')

    def salvar_matriz_elementos_latex(self, idx_1,idx_2):
        A = self.matriz_elementos_v_2(idx_1,idx_2)

        with open('teste.txt', 'w') as f:
            tabela_2 = """   \\multirow{{6}}{{*}}{{1a) i}} & \\multirow{{3}}{{*}}{{PU}}& A & {}   & {}    & {}   & {}\\\\\n
                    &                   & B & {}             & {}           & {}           & {} \\\\\n
                    &                   & C & {}             & {}           & {}           & {} \\\\\\cline{{2-7}}\n
                    & \\multirow{{3}}{{*}}{{SI (A)}}& A & {}             & {}           & {}           & {} \\\\\n
                    &                   & B & {}             & {}           & {}           & {} \\\\\n
                    &                   & C & {}             & {}           & {}           & {} \\\\\\cline{{1-7}}\n
                    \\multirow{{6}}{{*}}{{1a) ii}} & \\multirow{{3}}{{*}}{{PU}}& A & {}         & {}         & {}     & {}\\\\\n
                    &                   & B & {}             & {}           & {}           & {} \\\\\n
                    &                   & C & {}             & {}           & {}           & {} \\\\\\cline{{2-7}}\n
                    & \\multirow{{3}}{{*}}{{SI (A)}}& A & {}             & {}           & {}           & {} \\\\\n
                    &                   & B & {}             & {}           & {}           & {} \\\\\n
                    &                   & C & {}             & {}           & {}           & {} \\\\\\cline{{1-7}}\n
                    \\multirow{{6}}{{*}}{{1a) iii}} & \\multirow{{3}}{{*}}{{PU}}& A & {}      & {}          & {}       & {}\\\\\n
                    &                   & B & {}             & {}           & {}           & {} \\\\\n
                    &                   & C & {}             & {}           & {}           & {} \\\\\\cline{{2-7}}\n
                    & \\multirow{{3}}{{*}}{{SI (A)}}& A & {}             & {}           & {}           & {} \\\\\n
                    &                   & B & {}             & {}           & {}           & {} \\\\\n
                    &                   & C & {}             & {}           & {}           & {} \\\\\\cline{{1-7}}\n"""
            str_tabela = []
            for row in A:
                for column in row:
                    str_tabela.append("%4.4f" % column)

            f.write(tabela_2.format(*str_tabela))