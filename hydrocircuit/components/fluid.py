from cosapp.base import System


class Fluid(System):
    def setup(self):
        self.add_outward("density", value=1e3, unit="kg/m**3", desc="fluid density")
        self.add_outward(
            "kin_viscosity", value=1e-6, unit="m**2/s", desc="fluid kinematic viscosity"
        )
