from cosapp.base import System
from cosapp.drivers import NonLinearSolver
from numpy import log10, sqrt


class FrictionFactor(System):
    '''
    Class to calculate friction factor (head loss) in a pipe.

    Inwards
    -------
    diameter : float
        Pipe diameter in metres
    roughness : float
        Pipe wall roughness in metres
    reynolds : float
        Flow Reynolds number

    Outwards
    --------
    fd : float
        Friction factor calculating according to `reynolds`. When Re < 3000,
        the flow is considered laminar and `fd = 64/Re`. Otherwise it is considered
        turbulent, and `f` is calculated according to Colebrook correlation.
    '''

    def setup(self):
        # free parameters
        self.add_inward(
            "f_guess", value=1, unit="", desc="approximation of friction factor"
        )
        self.add_inward("roughness", value=0, unit="m", desc="wall roughness")
        self.add_inward("diameter", value=1, unit="m", desc="pipe diameter")
        self.add_inward("reynolds", value=1000, unit="", desc="reynolds number")

        # objective variable
        self.add_outward(
            "fd", value=0, unit="", desc="new estimation of friction factor"
        )

        # presetting solver
        self.add_driver(NonLinearSolver('friction_solver'))
        self.add_unknown("f_guess")
        self.add_equation("fd == f_guess")

    def compute(self):
        # apply objective function
        if self.reynolds < 3000:
            self.fd = 64 / self.reynolds
        else:
            self.fd = self.colebrook(
                self.f_guess, self.roughness, self.diameter, self.reynolds
            )

    @staticmethod
    def colebrook(f_guess, e, D, Re):
        A = (e / D) / 3.7
        B = 2.51 / (Re * sqrt(f_guess))
        C = -2 * log10(A + B)
        fd = 1 / C**2
        return fd
