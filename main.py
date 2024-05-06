from analisador_sep.elementos_rede import SEP
from analisador_sep.elementos_passivos import LinhaTransmissao, Transformador2Enro, Transformador3Enro
from analisador_sep.elementos_ativos import EquivalenteRede
from analisador_sep.interface_resultados import Iresultados


# Numero da equipe
NA = 4

# Definir o sistema de potencia utilizado
sep = SEP(9, 100, 230)

# Definir elementos do SEP analisado

elementos = [
    LinhaTransmissao(0.08953+0.53092j, 300 + NA, 'LT 01C1', 1, 2),
    LinhaTransmissao(0.08953+0.53092j, 300 + NA, 'LT 01C2', 1, 2),
    Transformador3Enro(230, 69, 13.8, 100, 40,0.0398 + NA*10**(-4),
                       8.3214 + NA*10**(-2), 0.0756, 15.5472,0.0401, 5.0101,
                       30, 30,'TR 01T1',2, 3),
    Transformador3Enro(230, 69, 13.8, 100, 40,0.0398 + NA*10**(-4),
                       8.3214 + NA*10**(-2), 0.0756, 15.5472,0.0401, 5.0101,
                       30, 30,'TR 01T2',2, 3),
    LinhaTransmissao(0.02898+0.47598j, (300 + NA)/10,'LT 03J1', 3, 4),
    LinhaTransmissao(0.02898+0.47598j, (450 + NA)/10,'LT 02J1', 3, 7),
    LinhaTransmissao(0.02898+0.47598j, (450 + NA)/10,'LT 02J2', 3, 7),
    LinhaTransmissao(0.02898+0.47598j, (350 + NA)/10,'LT 05J1', 4, 7),
    LinhaTransmissao(0.03752+0.50121j, (700 + NA)/10,'LT 04J1', 4, 5),
    Transformador2Enro(69,34.5,30,0,(6+NA/100)*10**(-2),30,
                       'TR 02T1',5,6),
    Transformador2Enro(69,13.8,15,0,(5.5+NA/100)*10**(-2),30,
                       'TR 03C1',7,8),
    LinhaTransmissao(0.02682+0.49327j, (60 + NA)/10,'LT 06K1', 8, 9)
]

sep.adicionar_elementos(elementos)
sep.solve()

iresultados = Iresultados(sep)

iresultados.diagrama_impedancias()
iresultados.matriz_admitancias()
iresultados.matriz_impedancias()
