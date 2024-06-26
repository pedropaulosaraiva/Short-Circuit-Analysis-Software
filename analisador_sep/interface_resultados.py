from analisador_sep.elementos_rede import SEP, SEP_positivo, SEP_negativo, SEP_0
from analisador_sep.elementos_passivos import (Elemento2Terminais, Impedancia, LinhaTransmissao, Transformador2Enro,
                                               Transformador3Enro)
from analisador_sep.elementos_ativos import EquivalenteRede
from analisador_sep.numero_pu import crec
import numpy as np
from math import sqrt

class Iresultados:
    def __init__(self, sep: SEP):
        self.sep = sep
        self.nome_seq = ''
        self.nome_seq_abr = ''
        if type(self.sep) is SEP_positivo:
            self.nome_seq = ' (sequência positiva)'
            self.nome_seq_abr = '(+)'
        elif type(self.sep) is SEP_negativo:
            self.nome_seq = ' (sequência negativa)'
            self.nome_seq_abr = '(-)'
        elif type(self.sep) is SEP_0:
            self.nome_seq = ' (sequência zero)'
            self.nome_seq_abr = '(0)'

    def diagrama_impedancias(self):
        elementos = self.sep.elementos

        print(f"Valores do diagrama de impedancias{self.nome_seq}:")
        print("============================================")

        for elemento in elementos:
            elemento: Elemento2Terminais

            if isinstance(elemento, Impedancia):
                print(f'A impedância {elemento.nome} entre as barras #{elemento.id_barra1} e #{elemento.id_barra2} com '
                      f'{elemento.z_ohm} ohms, possui valor em pu: {elemento.z_pu}@{elemento.v_base/1000}kV, '
                      f'{elemento.s_base/10**6}MVA')

            elif isinstance(elemento, LinhaTransmissao):
                print(f'A linha {elemento.nome} entre as barras #{elemento.id_barra1} e #{elemento.id_barra2} com '
                      f'{elemento.z_ohm} ohms, possui valor em pu: {elemento.z_pu}@{elemento.v_base/1000}kV, '
                      f'{elemento.s_base/10**6}MVA')

            elif isinstance(elemento, Transformador2Enro):
                print(f'O transformador {elemento.nome} entre as barras #{elemento.id_barra1} e #{elemento.id_barra2},'
                      f'possui valor em pu: {elemento.z_pu}@{elemento.v_base/1000}kV, {elemento.s_base/10**6}MVA')

            elif isinstance(elemento, Transformador3Enro):
                if elemento.id_barra3 is None:
                    print(f'O transformador {elemento.nome} entre as barras #{elemento.id_barra1}, '
                          f'#{elemento.id_barra2} e terciário em aberto, possui valor em pu: '
                          f'{elemento.z_pu}@{elemento.v_base / 1000}kV, {elemento.s_base / 10 ** 6}MVA')

                else:
                    pass

            elif isinstance(elemento, EquivalenteRede):
                print(f'O equivalente de rede {elemento.nome} na barra #{elemento.id_barra1} com impedância Zth'
                      f'{elemento.id_barra1} em pu: {elemento.z_pu}@{elemento.v_base/1000}kV, '
                      f'{elemento.s_base/10**6}MVA')

        print("============================================\n")

    def matriz_admitancias(self, decimais=None):
        y: np.array = self.sep.matriz_admitancias
        print(f"Matriz de aditâncias{self.nome_seq}:")
        print("==============================")
        if decimais is None:
            print(y)
        else:
            print(np.around(y,decimals=decimais))
        print("==============================\n")

    def matriz_impedancias(self, decimais=None):
        z: np.array = self.sep.matriz_impedacias
        print(f"Matriz de impedâncias{self.nome_seq}:")
        print("===============================")
        if decimais is None:
            print(z)
        else:
            print(np.around(z, decimals=decimais))
        print("===============================\n")

    def curto_circuito(self):
        barras = self.sep.barras
        elementos = self.sep.elementos
        corrente_curto = crec(self.sep.corrente_curto)
        print(f"Resultados do curto em #{self.sep.id_barra_curto}, com impedância de falta"
              f" {self.sep.z_f_ohm} Ohms{self.nome_seq}:")
        print(f'If{self.nome_seq_abr} = {corrente_curto[0]}<{corrente_curto[1]}º')
        print("===============================================")
        print("Tensões nas barras:")
        for barra in barras[1:]:
            barra.Va_pu, barra.Vb_pu, barra.Vc_pu = (crec(barra.Va_pu),
                                                     crec(barra.Vb_pu), crec(barra.Vc_pu))
            barra.Va_volts, barra.Vb_volts, barra.Vc_volts = (crec(barra.Va_volts),
                                                              crec(barra.Vb_volts), crec(barra.Vc_volts))
            
            print(f"A barra #{barra.id_barra} possui as tensões de pós falta{self.nome_seq}:\n"
                f"    |Va_pu|{self.nome_seq_abr} = {barra.Va_pu[0]}@{barra.v_base/1000}kV, <Va_pu = {barra.Va_pu[1]}°\n"
                f"    |Vb_pu|{self.nome_seq_abr} = {barra.Vb_pu[0]}@{barra.v_base/1000}kV, <Vb_pu = {barra.Vb_pu[1]}°\n"
                f"    |Vc_pu|{self.nome_seq_abr} = {barra.Vc_pu[0]}@{barra.v_base/1000}kV, <Vc_pu = {barra.Vc_pu[1]}°\n"
                f"    |Va_volts|{self.nome_seq_abr} = {barra.Va_volts[0]/1000}kV, <Va_volts = {barra.Va_volts[1]}°\n"
                f"    |Vb_volts|{self.nome_seq_abr} = {barra.Vb_volts[0]/1000}kV, <Vb_volts = {barra.Vb_volts[1]}°\n"
                f"    |Vc_volts|{self.nome_seq_abr} = {barra.Vc_volts[0]/1000}kV, <Vc_volts = {barra.Vc_volts[1]}°\n")
        print("========================")
        print("Correntes nos elementos:")
        
        for elemento in elementos:
            elemento: Elemento2Terminais

            elemento.Ia_pu, elemento.Ib_pu, elemento.Ic_pu = (crec(elemento.Ia_pu),
                                                              crec(elemento.Ib_pu), crec(elemento.Ic_pu))
            elemento.Ia_amp, elemento.Ib_amp, elemento.Ic_amp = (crec(elemento.Ia_amp),
                                                                 crec(elemento.Ib_amp), crec(elemento.Ic_amp))

            if isinstance(elemento, (Impedancia, LinhaTransmissao)):
                print(f'O elemento {elemento.nome}, possui as correntes de falta{self.nome_seq}:')

            elif isinstance(elemento, (Transformador2Enro, Transformador3Enro)):
                print(f'O transformador {elemento.nome}, possui as correntes de falta no primário{self.nome_seq}:')

            elif isinstance(elemento, EquivalenteRede):
                continue
                
            print(f"(sentido #{elemento.id_barra1} -> #{elemento.id_barra2})\n"
                  f"    |Ia_pu|{self.nome_seq_abr} = {elemento.Ia_pu[0]}@{elemento.s_base / (sqrt(3) * elemento.v_base)}A,"
                  f" <Ia_pu = {elemento.Ia_pu[1]}°\n"
                  f"    |Ib_pu|{self.nome_seq_abr} = {elemento.Ib_pu[0]}@{elemento.s_base / (sqrt(3) * elemento.v_base)}A,"
                  f" <Ib_pu = {elemento.Ib_pu[1]}°\n"
                  f"    |Ic_pu|{self.nome_seq_abr} = {elemento.Ic_pu[0]}@{elemento.s_base / (sqrt(3) * elemento.v_base)}A,"
                  f" <Ic_pu = {elemento.Ic_pu[1]}°\n"
                  f"    |Ia_amp|{self.nome_seq_abr} = {elemento.Ia_amp[0]}A, <Ia_amp = {elemento.Ia_amp[1]}°\n"
                  f"    |Ib_amp|{self.nome_seq_abr} = {elemento.Ib_amp[0]}A, <Ib_amp = {elemento.Ib_amp[1]}°\n"
                  f"    |Ic_amp|{self.nome_seq_abr} = {elemento.Ic_amp[0]}A, <Ic_amp = {elemento.Ic_amp[1]}°\n")

    def curto_abertura_condutor(self):
        barras = self.sep.barras
        elementos = self.sep.elementos

        print(f"Resultados da abetura de fase(s) entre #{self.sep.id_aberto_1} e #{self.sep.id_aberto_2} "
              f"({self.nome_seq}):")

        print("===============================================")
        print("Tensões nas barras:")
        for barra in barras[1:]:
            barra.Va_pu, barra.Vb_pu, barra.Vc_pu = (crec(barra.Va_pu),
                                                     crec(barra.Vb_pu), crec(barra.Vc_pu))
            barra.Va_volts, barra.Vb_volts, barra.Vc_volts = (crec(barra.Va_volts),
                                                              crec(barra.Vb_volts), crec(barra.Vc_volts))

            print(f"A barra #{barra.id_barra} possui as tensões de pós falta{self.nome_seq}:\n"
                  f"    |Va_pu|{self.nome_seq_abr} = {barra.Va_pu[0]}@{barra.v_base / 1000}kV, <Va_pu = {barra.Va_pu[1]}°\n"
                  f"    |Vb_pu|{self.nome_seq_abr} = {barra.Vb_pu[0]}@{barra.v_base / 1000}kV, <Vb_pu = {barra.Vb_pu[1]}°\n"
                  f"    |Vc_pu|{self.nome_seq_abr} = {barra.Vc_pu[0]}@{barra.v_base / 1000}kV, <Vc_pu = {barra.Vc_pu[1]}°\n"
                  f"    |Va_volts|{self.nome_seq_abr} = {barra.Va_volts[0] / 1000}kV, <Va_volts = {barra.Va_volts[1]}°\n"
                  f"    |Vb_volts|{self.nome_seq_abr} = {barra.Vb_volts[0] / 1000}kV, <Vb_volts = {barra.Vb_volts[1]}°\n"
                  f"    |Vc_volts|{self.nome_seq_abr} = {barra.Vc_volts[0] / 1000}kV, <Vc_volts = {barra.Vc_volts[1]}°\n")
        print("========================")



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