from analisador_sep.elementos_rede import SEP
from analisador_sep.elementos_passivos import LinhaTransmissao, Transformador2Enro, Transformador3Enro
from analisador_sep.elementos_ativos import EquivalenteRede
from analisador_sep.interface_resultados import Iresultados
from math import cos, sin, radians
from analisador_sep.numero_pu import cpolar, crec


# Definição do sistema de potência utilizado
sep = SEP(quantidade_barras=4, s_base=100, v_base_barra_1=13.8)

# Definição dos elementos do SEP analisado
elementos = [
    LinhaTransmissao(z_densidade=20j, comprimento=1, nome='LT', id_barra1=2, id_barra2=3),


    Transformador2Enro(v_nom_pri=13.8, v_nom_sec=138, s_nom=100, r_pu=0, x_pu=0.1, adiantamento_ps=-30,
                       nome='TR1', id_barra1=1, id_barra2=2),
    Transformador2Enro(v_nom_pri=138, v_nom_sec=13.8, s_nom=100, r_pu=0, x_pu=0.1, adiantamento_ps=30,
                       nome='TR2', id_barra1=3, id_barra2=4),

    EquivalenteRede(v_base=13.8, s_base=100, nome="Eq1", id_barra1=1, Z1_pu=0.15j),
    EquivalenteRede(v_base=13.8, s_base=100, nome="Eq2", id_barra1=4, Z1_pu=0.20j)
]

sep.adicionar_elementos(elementos)
sep.solve()

iresultados = Iresultados(sep)

iresultados.diagrama_impedancias()
iresultados.matriz_admitancias()
iresultados.matriz_impedancias()

v_t0_menos = [
    cpolar(1.05,0),
    cpolar(1.0243,-5.0679),
    cpolar(1.0063,-10.6218),
    cpolar(0.9982,-16.0488),
]

sep.adicionar_tensoes_pre_falta(v_t0_menos)

sep_curto_s_1 = sep.criar_curto_simetrico(id_barra_curto=1, z_f_ohm=1)

iresultados = Iresultados(sep_curto_s_1)
iresultados.curto_circuito_simetrico()

