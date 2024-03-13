from cosapp.base import System
from .pipegeometry import PipeGeometry
from .pipefluid import PipeFluid


class Pipe(System):
    def setup(self):
        self.add_child(PipeGeometry("geo"), pulling=["diameter", "length", "elevation_in", "elevation_out"])
        self.add_child(
            PipeFluid("fluid"), pulling=["diameter", "length", "roughness", "pressure_in", "pressure_out", "density", "kin_viscosity", "mass_flow", "gravity"]
        )

        self.connect(self.geo.outwards, self.fluid.inwards, ["area", "elevation_change"])
