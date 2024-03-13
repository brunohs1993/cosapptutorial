from cosapp.base import System


class Pump(System):
    def setup(self):
        self.add_inward("power", unit="W", value=0, desc="Pumping power")
        self.add_inward("pressure_in", unit="Pa", value=0, desc="inlet pressure")
        self.add_inward("mass_flow", unit="kg/s", value=0, desc="fluid mass flow")
        self.add_inward("density", unit="kg/m**3", value=0, desc="fluid density")

        self.add_outward("pressure_out", unit="Pa", value=0, desc="Outlet pressure")

    def compute(self):
        self.pressure_out = (
            self.pressure_in + self.power * self.density / self.mass_flow
        )
