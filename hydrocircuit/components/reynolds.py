from cosapp.base import System
from numpy import absolute


class Reynolds(System):
    def setup(self):
        self.add_inward(
            "kin_viscosity", value=1e-6, unit="m**2/s", desc="kinematic viscosity"
        )
        self.add_inward(
            "char_length",
            value=1,
            unit="m",
            desc="characteristic length for reynolds",
        )
        self.add_inward("velocity", value=1, unit="m/s", desc="fluid velocity")

        self.add_outward("reynolds", value=0, unit="", desc="reynolds number")

    def compute(self):
        self.reynolds = absolute(self.velocity * self.char_length / self.kin_viscosity)
