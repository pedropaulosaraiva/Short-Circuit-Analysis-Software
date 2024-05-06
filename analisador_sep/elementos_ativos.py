from analisador_sep.elementos_passivos import Elemento2Terminais


class EquivalenteRede(Elemento2Terminais):
    def __init__(self, v_t0_menos: complex, v_base: float,s_base: float, nome: str, id_barra1: int,
                 Scc3_pu=None, Z0_pu=None):
        if Scc3_pu is not None:
            z_pu = (v_t0_menos**2)/Scc3_pu
        elif Z0_pu is not None:
            z_pu = Z0_pu
        else:
            raise ValueError(f"Insira um valor de Scc3_pu ou X0_pu")
        z_ohm = z_pu*(v_base**2/s_base)
        self.v_t0_menos = v_t0_menos

        super().__init__(z_ohm, nome, id_barra1, 0)
        # A barra não pode ser terra
        if self.id_barra1 == 0:
            self.id_barra1, self.id_barra2 = self.id_barra2, self.id_barra1

    def __str__(self):
        return (f'O equivalente de rede {self.nome} na barra #{self.id_barra1} com '
                f'impedância Zth{self.id_barra1} em pu: {self.z_pu}@{self.v_base/1000}kV, {self.s_base/10**6}MVA')
