from cosapp.base import System


class IntakeReservoir(System):
    def setup(self):
        # inwards
        self.add_inward("density", value=1e3, unit="kg/m**3", desc="Fluid density")
        self.add_inward(
            "level", value=1, unit="m", desc="Level of reservoir in relation to outlet"
        )
        self.add_inward(
            "gravity", value=9.81, unit="m/s**2", desc="Gravity acceleration"
        )
        self.add_inward("atmosphere", value=1e5, unit="Pa", desc="Atmospheric pressure")

        self.add_outward("pressure_out", value=0, unit="Pa")

    def compute(self):
        self.pressure_out = self.atmosphere + self.level * self.gravity * self.density


class DischargeReservoir(System):
    def setup(self):
        # inwards
        self.add_inward("density", value=1e3, unit="kg/m**3", desc="Fluid density")
        self.add_inward(
            "level", value=1, unit="m", desc="Level of reservoir in relation to outlet"
        )
        self.add_inward(
            "gravity", value=9.81, unit="m/s**2", desc="Gravity acceleration"
        )
        self.add_inward("atmosphere", value=1e5, unit="Pa", desc="Atmospheric pressure")
        self.add_inward(
            "pressure_in",
            value=0,
            unit="Pa",
            desc="Inlet pressure given by connected pipe",
        )

        self.add_outward(
            "p_diff",
            value=0,
            unit="Pa",
            desc="Pressure difference between atmosphere and fluid surface",
        )

        self.add_equation("p_diff == 0")

    def compute(self):
        self.p_diff = self.pressure_in - (
            self.atmosphere + self.level * self.gravity * self.density
        )
