from cosapp.base import System, Port
from cosapp.drivers import NonLinearSolver


class Fluid(Port):
    def setup(self):
        self.add_variable("T", unit="degC")
        self.add_variable("h", unit="W/K")


class Voltage(Port):
    def setup(self):
        self.add_variable("V", unit="V")


class Temperature(Port):
    def setup(self):
        self.add_variable("T", unit="degC")


class Control(System):
    def setup(self):
        self.add_input(Temperature, "T_cpu")
        self.add_output(Voltage, "V_fan")

    def compute(self):
        # if self.T_cpu.T < 20:
        #     self.V_fan.V = 0.
        # elif self.T_cpu.T > 40:
        #     self.V_fan.V = 12.
        # else:
        #     self.V_fan.V = 6.

        self.V_fan.V = self.T_cpu.T * 12 / 40


class Heatsink(System):
    def setup(self):

        self.add_input(Fluid, "air")
        self.add_input(Temperature, "T_cpu")

        self.add_outward("Q_out", value=0, unit="W")

    def compute(self):
        self.Q_out = self.air.h * (self.T_cpu.T - self.air.T)


class Fan(System):
    def setup(self):
        self.add_input(Voltage, "V_fan")
        self.add_output(Fluid, "air")

        self.add_inward("T_amb", value=20, unit="degC")

    def compute(self):
        self.air.T = self.T_amb
        self.air.h = self.V_fan.V / 10


class CPU(System):
    def setup(self):
        self.add_input(Temperature, "T_cpu")

        self.add_inward("use", value=0, desc="cpu usage")
        self.add_inward(
            "max_power", value=20, unit="W", desc="Maximum power dissipated"
        )

        self.add_outward("Q_out", value=0, unit="W")

    def compute(self):
        self.Q_out = self.use * self.max_power


class CPUSystem(System):
    def setup(self):
        self.add_child(CPU("cpu"), pulling=["use", "max_power", "T_cpu"])
        self.add_child(Fan("fan"), pulling=["T_amb"])
        self.add_child(Heatsink("hsink"), pulling=["T_cpu"])
        self.add_child(Control("controller"), pulling=["T_cpu"])

        self.connect(self.controller.V_fan, self.fan.V_fan)
        self.connect(self.fan.air, self.hsink.air)

        self.add_unknown("T_cpu.T", lower_bound=self.T_amb)
        self.add_equation("cpu.Q_out == hsink.Q_out")

    def compute(self):
        pass


sys = CPUSystem("sys")

# cpu properties
sys.use = 1
sys.max_power = 20

# ambient temperature
sys.T_amb = 20

solver = sys.add_driver(NonLinearSolver("solver"))

sys.run_drivers()

print(solver.problem)
