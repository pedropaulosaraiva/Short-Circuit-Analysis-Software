from analisador_sep.elementos_rede import SEP
from analisador_sep.elementos_passivos import LinhaTransmissao, Transformador2Enro, Transformador3Enro
from analisador_sep.elementos_ativos import EquivalenteRede
from analisador_sep.interface_resultados import Iresultados
from math import cos, sin, radians
from analisador_sep.numero_pu import cpolar, crec


# Número da equipe
NA = 4

# Definição do sistema de potência utilizado
sep = SEP(quantidade_barras=9, s_base=100, v_base_barra_1=230)

# Definição dos elementos do SEP analisado
elementos = [
    LinhaTransmissao(z_densidade=0.08953+0.53092j, comprimento=300 + NA, nome='LT 01C1', id_barra1=1, id_barra2=2),
    LinhaTransmissao(z_densidade=0.08953+0.53092j, comprimento=300 + NA, nome='LT 01C2', id_barra1=1, id_barra2=2),
    LinhaTransmissao(z_densidade=0.02898+0.47598j, comprimento=(300 + NA)/10, nome='LT 03J1', id_barra1=3, id_barra2=4),
    LinhaTransmissao(z_densidade=0.02898+0.47598j, comprimento=(450 + NA)/10, nome='LT 02J1', id_barra1=3, id_barra2=7),
    LinhaTransmissao(z_densidade=0.02898+0.47598j, comprimento=(450 + NA)/10, nome='LT 02J2', id_barra1=3, id_barra2=7),
    LinhaTransmissao(z_densidade=0.02898+0.47598j, comprimento=(350 + NA)/10, nome='LT 05J1', id_barra1=4, id_barra2=7),
    LinhaTransmissao(z_densidade=0.03752+0.50121j, comprimento=(700 + NA)/10, nome='LT 04J1', id_barra1=4, id_barra2=5),
    LinhaTransmissao(z_densidade=0.02682+0.49327j, comprimento=(60 + NA)/10, nome='LT 06K1', id_barra1=8, id_barra2=9),

    Transformador3Enro(v_nom_pri=230, v_nom_sec=69, v_nom_ter=13.8, s_nom_pri=100, s_nom_sec=40,
                       r_ps_pu=(0.0398 + NA*10**(-4))*10**(-2), x_ps_pu=(8.3214 + NA*10**(-2))*10**(-2),
                       r_pt_pu=(0.0756 + NA*10**(-4))*10**(-2), x_pt_pu=(15.5472 + NA*10**(-2))*10**(-2),
                       r_st_pu=(0.0401 + NA*10**(-4))*10**(-2), x_st_pu=(5.0101 + NA*10**(-2))*10**(-2),
                       adiantamento_ps=30, adiantamento_pt=30, nome='TR 01T1', id_barra1=2, id_barra2=3),
    Transformador3Enro(v_nom_pri=230, v_nom_sec=69, v_nom_ter=13.8, s_nom_pri=100, s_nom_sec=40,
                       r_ps_pu=(0.0398 + NA*10**(-4))*10**(-2), x_ps_pu=(8.3214 + NA*10**(-2))*10**(-2),
                       r_pt_pu=(0.0756 + NA*10**(-4))*10**(-2), x_pt_pu=(15.5472 + NA*10**(-2))*10**(-2),
                       r_st_pu=(0.0401 + NA*10**(-4))*10**(-2), x_st_pu=(5.0101 + NA*10**(-2))*10**(-2),
                       adiantamento_ps=30, adiantamento_pt=30, nome='TR 01T2', id_barra1=2, id_barra2=3),

    Transformador2Enro(v_nom_pri=69, v_nom_sec=34.5, s_nom=30, r_pu=0, x_pu=(6 + NA/100)*10**(-2), adiantamento_ps=30,
                       nome='TR 02T1', id_barra1=5, id_barra2=6),
    Transformador2Enro(v_nom_pri=69, v_nom_sec=13.8, s_nom=15, r_pu=0, x_pu=(5.5 + NA/100)*10**(-2), adiantamento_ps=30,
                       nome='TR 03C1', id_barra1=7, id_barra2=8),

    EquivalenteRede(v_base=230, s_base=100, nome="Eq1", id_barra1=1, Scc3=cpolar(19890.734, 89.0666)),
    EquivalenteRede(v_base=34.5, s_base=100, nome="Eq2", id_barra1=6, Z1_pu=cpolar(8.6764, 89.4313))
]

sep.adicionar_elementos(elementos)
sep.solve()

iresultados = Iresultados(sep)

iresultados.diagrama_impedancias()
iresultados.matriz_admitancias()
iresultados.matriz_impedancias()

v_t0_menos = [
    cpolar(1.0290,11.5276),
    cpolar(0.9852,6.0130),
    cpolar(0.9824,4.6215),
    cpolar(0.9817,3.8909),
    cpolar(0.9859,4.0049),
    cpolar(1.0355,9.6164),
    cpolar(0.9740,3.2654),
    cpolar(0.9636,-0.9988),
    cpolar(0.9434,-7.2417),
]

sep.adicionar_tensoes_pre_falta(v_t0_menos)

sep_curto_s_3 = sep.criar_curto_simetrico(id_barra_curto=2, z_f_ohm=2.101)
sep_curto_s_4 = sep.criar_curto_simetrico(id_barra_curto=4, z_f_ohm=2.787)
sep_curto_s_8 = sep.criar_curto_simetrico(id_barra_curto=8, z_f_ohm=0.048)

iresultados = Iresultados(sep_curto_s_4)
iresultados.curto_circuito_simetrico()

iresultados = Iresultados(sep_curto_s_8)
iresultados.curto_circuito_simetrico()
