from analisador_sep.elementos_rede import SEP
from analisador_sep.elementos_passivos import LinhaTransmissao, Transformador2Enro, Transformador3Enro
from analisador_sep.elementos_ativos import EquivalenteRede


# Numero da equipe
NA = 4

# Definir o sistema de potencia utilizado
sep = SEP(9, 100, 1, 230)

# Definir elementos do SEP analisado

elementos = [
    LinhaTransmissao(0.08953+0.53092j, 300 + NA, 1, 2),
    LinhaTransmissao(0.08953+0.53092j, 300 + NA, 1, 2),

]