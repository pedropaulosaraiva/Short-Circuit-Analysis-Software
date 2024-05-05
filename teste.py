from analisador_sep.elementos_rede import SEP
from analisador_sep.elementos_passivos import LinhaTransmissao, Transformador2Enro, Transformador3Enro
from analisador_sep.elementos_ativos import EquivalenteRede


# Numero da equipe
NA = 4

# Definir o sistema de potencia utilizado
sep = SEP(5, 1, 1)

# Definir elementos do SEP analisado

elementos = [
    LinhaTransmissao(0.125j, 1, 1, 2),
    LinhaTransmissao(0.25j, 1, 1, 3),
    LinhaTransmissao(0.4j, 1, 1, 4),
    LinhaTransmissao(0.5j, 1, 2, 3),
    LinhaTransmissao(0.5j, 1, 2, 3),
    LinhaTransmissao(0.2j, 1, 2, 4),
    LinhaTransmissao(1.25j, 1, 3, 5),
    LinhaTransmissao(1.25j, 1, 4, 5),
]

elementos2 = [
    LinhaTransmissao(1.25j, 1, 1, 5),
    LinhaTransmissao(0.5j, 1, 1, 3),
    LinhaTransmissao(0.5j, 1, 1, 3),
    LinhaTransmissao(0.25j, 1, 1, 4),
    LinhaTransmissao(0.2j, 1, 2, 3),


]

#
sep.adicionar_elementos(elementos)
sep.solve()

print(sep.matriz_incidencia)
print(sep.matriz_primitiva_admitancias)

print(sep.matriz_admitancias)