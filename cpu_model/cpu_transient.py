from cosapp.base import System
from cosapp.drivers import NonLinearSolver, RungeKutta
from cosapp.recorders import DataFrameRecorder

import matplotlib.pyplot as plt
from scipy.constants import Stefan_Boltzmann


class Control(System):
    def setup(self):
        self.add_inward("T_control", value=10, unit="K", desc="CPU temperature")
        self.add_outward("V_fan", value=0, unit="V", desc="Fan activation voltage.")

    def compute(self):
        # if self.T_control < 20:
        #     self.V_fan = 0.0
        # elif self.T_control > 40:
        #     self.V_fan = 12.0
        # else:
        #     self.V_fan = 6.0

        self.V_fan = min(max(0, self.T_control * 12 / 40), 12)


class Heatsink(System):
    def setup(self):

        self.add_inward(
            "h_air", value=0, unit="W/m**2/K", desc="total heat transfer coefficient"
        )
        self.add_inward("T_amb", value=20, unit="K", desc="ambient temperature")
        self.add_inward(
            "Q_in", value=0, unit="W", desc="heat comming from the cpu to the heatsink"
        )
        self.add_inward(
            "emissivity",
            value=0.8,
            unit="",
            desc="surface thermal emissivity (grey surface)",
        )
        self.add_inward(
            "convection_area",
            value=0.1,
            unit="m**2",
            desc="effective convection surface area",
        )
        self.add_inward(
            "radiation_area",
            value=0.5,
            unit="m**2",
            desc="effective radiation surface area",
        )
        self.add_inward("heat_cap", value=10, unit="J/K", desc="heatsink heat capacity")

        self.add_inward("T_metal", value=10, unit="K", desc="CPU temperature")

        self.add_outward("T_contact", value=10, unit="K", desc="CPU temperature")
        self.add_outward(
            "Q_out", value=0, unit="W", desc="heat leaving heatsink to the environment"
        )
        self.add_outward("dT", value=0, unit="K/s", desc="temperature variation")

        self.add_transient("T_metal", der="dT")

        self.add_unknown("T_metal")

    def compute(self):

        self.Q_out = self.h_air * self.convection_area * (
            self.T_metal - self.T_amb
        ) + self.emissivity * Stefan_Boltzmann * self.radiation_area * (
            (self.T_metal + 273.15) ** 4 - (self.T_amb + 273.15) ** 4
        )

        self.dT = (self.Q_in - self.Q_out) / self.heat_cap

        self.T_contact = self.T_metal


class Fan(System):
    def setup(self):
        self.add_inward("V_fan", value=0, unit="V", desc="Fan activation voltage.")
        self.add_outward(
            "h_air", value=0, unit="W/m**2/K", desc="total heat transfer coefficient"
        )

    def compute(self):
        self.h_air = self.V_fan * 1e1


class CPU(System):
    def setup(self):
        self.add_inward("use", value=0, desc="cpu usage")
        self.add_inward(
            "max_power", value=20, unit="W", desc="Maximum power dissipated"
        )
        self.add_inward("heat_cap", value=10, unit="J/K", desc="heat capacity")
        self.add_inward("T_cpu", value=10, unit="K", desc="CPU temperature")
        self.add_inward(
            "contact_cond",
            value=10,
            unit="W/K",
            desc="effective conductivity of contact",
        )
        self.add_inward("T_contact", value=10, unit="K", desc="metal temperature")

        self.add_outward("dT", value=0, unit="K/s", desc="temperature variation")
        self.add_outward(
            "T_control", value=10, unit="K", desc="temperature sent to the controller"
        )
        self.add_outward(
            "Q_out", value=0, unit="W", desc="heat leaving cpu to heatsink"
        )

        self.add_transient("T_cpu", der="dT")

    def compute(self):
        self.Q_out = self.contact_cond * (self.T_cpu - self.T_contact)

        self.dT = (self.use * self.max_power - self.Q_out) / self.heat_cap

        self.T_control = self.T_cpu


class CPUSystem(System):
    def setup(self):
        self.add_child(CPU("cpu"), pulling=["use", "max_power", "T_cpu"])
        self.add_child(Fan("fan"))
        self.add_child(Heatsink("hsink"), pulling=["T_amb"])
        self.add_child(Control("controller"))

        self.connect(
            self.cpu.outwards, self.controller.inwards, ["T_control"]
        )  # T_cpu from cpu to fan controller
        self.connect(
            self.controller.outwards, self.fan.inwards, ["V_fan"]
        )  # V_fan from fan controller to fan
        self.connect(
            self.fan.outwards, self.hsink.inwards, ["h_air"]
        )  # h_air from fan to heatsink
        self.connect(
            self.hsink.outwards, self.cpu.inwards, ["T_contact"]
        )  # T_cpu from cpu to heatsink
        self.connect(
            self.cpu.outwards, self.hsink.inwards, {"Q_out": "Q_in"}
        )  # Q_out from heatsink to cpu

    def compute(self):
        pass


sys = CPUSystem("sys")

# cpu properties
sys.max_power = 500
sys.cpu.heat_cap = 710 * 0.1
sys.hsink.heat_cap = 900 * 0.2
sys.hsink.emissivity = 0.8

sys.cpu.contact_cond = 100

sys.T_cpu = 20
sys.hsink.T_metal = 20

# ambient temperature
sys.T_amb = 20

sys.drivers.clear()

solver = sys.add_driver(RungeKutta("RungeKutta"))
solver.add_child(NonLinearSolver("NLsolver"))


solver.time_interval = (0, 150)
solver.dt = 0.05

solver.set_scenario(
    init={"T_cpu": 20.0},
    values={"use": 1.0},
)

rec = solver.add_recorder(
    DataFrameRecorder(
        includes=[
            "use",
            "T_cpu",
            "hsink.T_metal",
            "cpu.Q_out",
            "hsink.Q_out",
            "fan.V_fan",
        ]
    )
)

sys.run_drivers()

df = rec.data

print(df.head(10))

fig, ax = plt.subplots(nrows=1, ncols=3)
# ax.plot(df["time"].to_numpy(), df["use"].to_numpy(), label="use")
ax[0].plot(df["time"].to_numpy(), df["T_cpu"].to_numpy(), label="T cpu")
ax[0].plot(df["time"].to_numpy(), df["hsink.T_metal"].to_numpy(), label="T metal")
ax[1].plot(df["time"].to_numpy(), df["cpu.Q_out"].to_numpy(), label="Q cpu")
ax[1].plot(df["time"].to_numpy(), df["hsink.Q_out"].to_numpy(), label="Q hsink")
ax[2].plot(df["time"].to_numpy(), df["use"].to_numpy(), label="cpu usage")
ax[2].plot(df["time"].to_numpy(), df["fan.V_fan"].to_numpy(), label="V fan")

for a in ax:
    a.legend()

plt.tight_layout()
plt.show(block=True)
