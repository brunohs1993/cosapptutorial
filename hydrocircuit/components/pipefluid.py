from cosapp.base import System
from cosapp.drivers import NonLinearSolver
from numpy import sign, sqrt, log10


class PipeFluid(System):
    """
    Class to calculate the transformation of the fluid between pipe"s
    inlet and outlet.

    Inwards
    -------
    diameter : float
        Pipe diameter in metres
    length : float
        Pipe length
    area : float
        Pipe cross sectional area
    elevation_change : float
        Difference in elevation between inlet and outlet
    roughness : float
        Pipe wall roughness in metres
    gravity : float
        Gravity acceleration

    Outwards
    --------
    f_out : float
        Friction factor calculating according to `reynolds`. When Re < 3000,
        the flow is considered laminar and `f_out = 64/Re`. Otherwise it is considered
        turbulent, and `f` is calculated according to Colebrook correlation.
    """

    def setup(self):
        # inwards geom
        self.add_inward("diameter", 1.0, unit="m", desc="Pipe diameter")
        self.add_inward("area", 0.0, unit="m**2", desc="Pipe cross section")
        self.add_inward("length", 1.0, unit="m", desc="Pipe length")
        self.add_inward("roughness", 0, unit="m", desc="Pipe wall roughness")
        self.add_inward("elevation_change", 0, unit="m", desc="Pipe length")

        # inwards fluid
        self.add_inward("pressure_in", 1.0, unit="Pa", desc="Inlet pressure")
        self.add_inward("density", value=1e3, unit="kg/m**3", desc="Fluid density")
        self.add_inward("kin_viscosity", value=1e-6, unit="m**2/s", desc="Fluid kinematic viscosity")
        self.add_inward("mass_flow", 1.0, unit="kg/s", desc="Fluid mass flow")
        self.add_inward(
            "f_guess", value=1, unit="", desc="approximation of friction factor"
        )

        # inwards other
        self.add_inward("gravity", 9.81, unit="m/s**2", desc="Gravity acceleration")

        # outwards
        self.add_outward("fd", 0.0, unit="", desc="Darcy factor for pipe head loss")
        self.add_outward("reynolds", 0.0, unit="", desc="Reynolds number")
        self.add_outward("pressure_out", 1.0, unit="Pa", desc="Outlet pressure")
        self.add_outward("velocity", 1.0, unit="Pa", desc="Outlet pressure")

        # driver to solve friction
        self.add_driver(NonLinearSolver('friction_solver'))
        self.add_unknown("f_guess")
        self.add_equation("fd == f_guess")

    def compute(self):
        self.velocity = self.mass_flow / (self.area * self.density)
        self.reynolds = self.velocity * self.diameter / self.kin_viscosity

        if self.reynolds < 3000:
            self.fd = 64 / self.reynolds
        else:
            self.fd = self.colebrook(
                self.f_guess, self.roughness, self.diameter, self.reynolds
            )

        self.pressure_out = self.pressure_in - sign(self.velocity) * self.fd * self.density * self.length * self.velocity**2 / (2 * self.diameter) - self.elevation_change * self.density * self.gravity

    @staticmethod
    def colebrook(f_guess, e, D, Re):
        A = (e / D) / 3.7
        B = 2.51 / (Re * sqrt(f_guess))
        C = -2 * log10(A + B)
        fd = 1 / C**2
        return fd
