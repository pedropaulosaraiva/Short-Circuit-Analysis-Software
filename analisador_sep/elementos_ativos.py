from analisador_sep.elementos_passivos import Elemento2Terminais


class EquivalenteRede(Elemento2Terminais):
    def __init__(self, v_base: float,s_base: float, nome: str, id_barra1: int, z_1_pu: complex, z_0_pu: complex):
        z_ohm = z_1_pu*(v_base**2/s_base)

        super().__init__(z_ohm, nome, id_barra1, 0)

        self.z_ohm_0 = z_0_pu * (v_base ** 2 / s_base)

        # A barra 1 não pode ser terra
        if self.id_barra1 == 0:
            self.id_barra1, self.id_barra2 = self.id_barra2, self.id_barra1

    @classmethod
    def paramScc(cls, v_base: float,s_base: float, nome: str, id_barra1: int, Scc3: complex, Scc1: complex):
        Scc3_pu = Scc3/s_base
        Scc1_pu = Scc1/s_base

        z_1_pu = 1/Scc3_pu.conjugate()
        z_0_pu = ((3/Scc1_pu.conjugate()) - (2/Scc3_pu.conjugate()))

        return cls(v_base,s_base, nome, id_barra1, z_1_pu, z_0_pu)

    def transformar_seq0(self):
        self.z_ohm = self.z_ohm_0
