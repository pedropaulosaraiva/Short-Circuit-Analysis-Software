from analisador_sep.elementos_rede import SEP
from analisador_sep.elementos_passivos import (LinhaTransmissao, Transformador2Enro, Transformador3Enro,
                                               TransformadorAterramento)
from analisador_sep.elementos_ativos import EquivalenteRede
from analisador_sep.interface_resultados import Iresultados, Interface_latex
from analisador_sep.numero_pu import cpolar, crec


# Número da equipe
NA = 4

# Definição do sistema de potência utilizado
sep = SEP(quantidade_barras=9, s_base=100, v_base_barra_1=230)

# Definição dos elementos do SEP analisado
elementos = [
    LinhaTransmissao(z_densidade_1=0.08953 + 0.53092j, z_densidade_0=0.44957 + 1.59869j, comprimento=300 + NA,
                     nome='LT 01C1', id_barra1=1, id_barra2=2, z_densidade_mutua_0=0.04547 + 0.58106j),
    LinhaTransmissao(z_densidade_1=0.08953 + 0.53092j, z_densidade_0=0.44957 + 1.59869j, comprimento=300 + NA,
                     nome='LT 01C2', id_barra1=1, id_barra2=2, z_densidade_mutua_0=0.04547 + 0.58106j),
    LinhaTransmissao(z_densidade_1=0.02898 + 0.47598j, z_densidade_0=0.47056 + 1.71587j, comprimento=(300 + NA) / 10,
                     nome='LT 03J1', id_barra1=3, id_barra2=4),
    LinhaTransmissao(z_densidade_1=0.02898 + 0.47598j, z_densidade_0=0.47056 + 1.71587j, comprimento=(450 + NA) / 10,
                     nome='LT 02J1', id_barra1=3, id_barra2=7, z_densidade_mutua_0=0.03902 + 0.41824j),
    LinhaTransmissao(z_densidade_1=0.02898 + 0.47598j, z_densidade_0=0.47056 + 1.71587j, comprimento=(450 + NA) / 10,
                     nome='LT 02J2', id_barra1=3, id_barra2=7, z_densidade_mutua_0=0.03902 + 0.41824j),
    LinhaTransmissao(z_densidade_1=0.02898 + 0.47598j, z_densidade_0=0.47056 + 1.71587j, comprimento=(350 + NA) / 10,
                     nome='LT 05J1', id_barra1=4, id_barra2=7),
    LinhaTransmissao(z_densidade_1=0.03752 + 0.50121j, z_densidade_0=0.56212 + 1.80475j, comprimento=(700 + NA) / 10,
                     nome='LT 04J1', id_barra1=4, id_barra2=5),
    LinhaTransmissao(z_densidade_1=0.02682 + 0.49327j, z_densidade_0=0.48713 + 1.79787j, comprimento=(60 + NA) / 10,
                     nome='LT 06K1', id_barra1=8, id_barra2=9),

    Transformador3Enro(v_nom_pri=230, v_nom_sec=69, v_nom_ter=13.8, s_nom_pri=100, s_nom_sec=40,
                       r_ps_pu=(0.0398 + NA*10**(-4))*10**(-2), x_ps_pu=(8.3214 + NA*10**(-2))*10**(-2),
                       r_pt_pu=(0.0756 + NA*10**(-4))*10**(-2), x_pt_pu=(15.5472 + NA*10**(-2))*10**(-2),
                       r_st_pu=(0.0401 + NA*10**(-4))*10**(-2), x_st_pu=(5.0101 + NA*10**(-2))*10**(-2),
                       adiantamento_ps=30, adiantamento_pt=30, nome='TR 01T1', lig = 'Ygdd', id_barra1=2, id_barra2=3),
    Transformador3Enro(v_nom_pri=230, v_nom_sec=69, v_nom_ter=13.8, s_nom_pri=100, s_nom_sec=40,
                       r_ps_pu=(0.0398 + NA*10**(-4))*10**(-2), x_ps_pu=(8.3214 + NA*10**(-2))*10**(-2),
                       r_pt_pu=(0.0756 + NA*10**(-4))*10**(-2), x_pt_pu=(15.5472 + NA*10**(-2))*10**(-2),
                       r_st_pu=(0.0401 + NA*10**(-4))*10**(-2), x_st_pu=(5.0101 + NA*10**(-2))*10**(-2),
                       adiantamento_ps=30, adiantamento_pt=30, nome='TR 01T2', lig = 'Ygdd', id_barra1=2, id_barra2=3),

    Transformador2Enro(v_nom_pri=69, v_nom_sec=34.5, s_nom=30, r_pu=0, x_pu=(6 + NA/100)*10**(-2), adiantamento_ps=30,
                       nome='TR 02T1', lig='Dyg', id_barra1=5, id_barra2=6),
    Transformador2Enro(v_nom_pri=69, v_nom_sec=13.8, s_nom=15, r_pu=0, x_pu=(5.5 + NA/100)*10**(-2), adiantamento_ps=30,
                       nome='TR 03C1', lig='Dyg', id_barra1=7, id_barra2=8),

    EquivalenteRede.paramScc(v_base=230, s_base=100, nome="Eq1", id_barra1=1,
                             Scc3=cpolar(19890.734, 87.0666),
                             Scc1=cpolar(8848.9946, 87.0790)),
    EquivalenteRede(v_base=34.5, s_base=100, nome="Eq2", id_barra1=6, z_1_pu=cpolar(0.086764, 89.4313),
                    z_0_pu=cpolar(4.7718, 90)),

    TransformadorAterramento(z_pu_at=(5.8j*NA*10**(-2)), nome='TR 01A1', id_barra1=3, v_nom=69, s_nom=20)
]

sep.adicionar_elementos(elementos)

sep.solve_z_barra()

# iresultados = Iresultados(sep)
#
# iresultados.diagrama_impedancias()
#
# iresultados.matriz_admitancias()
# iresultados.matriz_impedancias()

# Diagramas de sequência
sep.solve_z_barra_sequencias()

# iresultados_positiva = Iresultados(sep.sep_seq_positiva)
#
# iresultados_positiva.diagrama_impedancias()
#
# iresultados_positiva.matriz_admitancias()
# iresultados_positiva.matriz_impedancias()

iresultados_negativa = Iresultados(sep.sep_seq_negativa)

iresultados_negativa.diagrama_impedancias()

iresultados_negativa.matriz_admitancias()
iresultados_negativa.matriz_impedancias()

iresultados_zero = Iresultados(sep.sep_seq_zero)

iresultados_zero.diagrama_impedancias()

iresultados_zero.matriz_admitancias()
iresultados_zero.matriz_impedancias()

v_t0_menos_bar_1 = [
    cpolar(1.0290, 11.5276),
    cpolar(0.9852, 6.0130),
    cpolar(0.9824, 4.6215),
    cpolar(0.9817, 3.8909),
    cpolar(0.9859, 4.0049),
    cpolar(1.0355, 9.6164),
    cpolar(0.9740, 3.2654),
    cpolar(0.9636, -0.9988),
    cpolar(0.9434, -7.2417),
]

sep.adicionar_tensoes_pre_falta(v_t0_menos_bar_1)

sep_curto_ft_7 = sep.criar_curto_fase_terra(7, 1.029)

iresultados_curto = Iresultados(sep_curto_ft_7)
iresultados_curto_p = Iresultados(sep_curto_ft_7.sep_seq_positiva)
iresultados_curto_n = Iresultados(sep_curto_ft_7.sep_seq_negativa)
iresultados_curto_z = Iresultados(sep_curto_ft_7.sep_seq_zero)


iresultados_curto_p.curto_circuito()
iresultados_curto_n.curto_circuito()
iresultados_curto_z.curto_circuito()
iresultados_curto.curto_circuito()

sep_curto_ff_2 = sep.criar_curto_fase_fase(2, 0.917)

iresultados_curto = Iresultados(sep_curto_ff_2)
iresultados_curto_p = Iresultados(sep_curto_ff_2.sep_seq_positiva)
iresultados_curto_n = Iresultados(sep_curto_ff_2.sep_seq_negativa)
iresultados_curto_z = Iresultados(sep_curto_ff_2.sep_seq_zero)


iresultados_curto_p.curto_circuito()
iresultados_curto_n.curto_circuito()
iresultados_curto_z.curto_circuito()
iresultados_curto.curto_circuito()

sep_curto_fft_9 = sep.criar_curto_fase_fase_terra(9, 1.429)

iresultados_curto = Iresultados(sep_curto_fft_9)
iresultados_curto_p = Iresultados(sep_curto_fft_9.sep_seq_positiva)
iresultados_curto_n = Iresultados(sep_curto_fft_9.sep_seq_negativa)
iresultados_curto_z = Iresultados(sep_curto_fft_9.sep_seq_zero)


iresultados_curto_p.curto_circuito()
iresultados_curto_n.curto_circuito()
iresultados_curto_z.curto_circuito()
iresultados_curto.curto_circuito()