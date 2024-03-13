from cosapp.base import Port


class FluidProperties(Port):
    def setup(self):
        self.add_variable("density", unit="kg/m**3", desc="fluid density")
        self.add_variable(
            "kin_viscosity", unit="m**2/s", desc="fluid kinematic viscosity"
        )
        self.add_variable("mass_flow", unit="kg/s", desc="mass flow")
