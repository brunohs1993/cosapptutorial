from cosapp.base import System
from cosapp.drivers import Optimizer
from cosapp.recorders import DataFrameRecorder

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go


# objective function definition
def rastrigin(x, y):
    return 20 + x**2 + y**2 - 10 * np.cos(np.pi * x) - 10 * np.cos(np.pi * y)


# small system to test
class Function(System):
    def setup(self):
        # free parameters
        self.add_inward("x", value=0)
        self.add_inward("y", value=0)

        # objective variable
        self.add_outward("f", value=0)

    def compute(self):
        # apply objective function
        self.f = rastrigin(self.x, self.y)


# generate object
s = Function("objective")

# generate random initial points
s.x, s.y = 2 * (0.5 - np.random.rand()), 2 * (0.5 - np.random.rand())

# optimiser parameters
optim = s.add_driver(Optimizer("optim", method="CG", max_iter=100))

optim.add_unknown(["x", "y"])
optim.set_minimum("f")

# record convergence
optim.options["monitor"] = True
recorder = optim.add_recorder(DataFrameRecorder(includes=["x", "y", "f"]))

# run
s.run_drivers()

# get data
df = recorder.export_data()
print(df)

# shape of objective function
XX, YY = np.meshgrid(np.linspace(-1.5, 1.5, 100), np.linspace(-1.5, 1.5, 100))

FF = rastrigin(XX, YY)

# 3d with plotly

plots = [go.Surface(x=XX, y=YY, z=FF), go.Scatter3d(x=df["x"], y=df["y"], z=df["f"])]

fig = go.Figure(data=plots)

fig.show()


# 2d with matplotlib
fig1, ax = plt.subplots(nrows=1, ncols=1)

ax.contourf(XX, YY, FF)

ax.plot(df["x"].to_numpy(), df["y"].to_numpy(), linestyle="--", color="k")
ax.scatter(df["x"].to_numpy()[0], df["y"].to_numpy()[0], marker="o", color="r")
ax.scatter(df["x"].to_numpy()[-1], df["y"].to_numpy()[-1], marker="o", color="b")

plt.tight_layout()
plt.show(block=True)
