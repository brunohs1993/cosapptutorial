from cosapp.base import System
from scipy.constants import pi


class PipeGeometry(System):
    '''
    Class to calculate geometric properties of the pipe.

    Inwards
    -------
    diameter : float
        Pipe diameter
    length : float
        Pipe length
    elevation_in : float
        Pipe elevation at entrance
    elevation_out : float
        Pipe elevation at exit

    Outwards
    --------
    area : float
        Cross sectional area of the pipe
    elevation_change : float
        Change of elevation of the pipe between entrance and exit
    '''

    def setup(self):
        # inward variables
        self.add_inward("diameter", 1.0, unit="m", desc="Pipe diameter")
        self.add_inward("length", 1.0, unit="m", desc="Pipe length")
        self.add_inward("elevation_in", 0.0, unit="m", desc="Vertical elevation at entrance")
        self.add_inward("elevation_out", 0.0, unit="m", desc="Vertical elevation at exit")

        # outward quantities
        self.add_outward("area", 0.0, unit="m**2", desc="Pipe cross section")
        self.add_outward("elevation_change", 0.0, unit="m", desc="Change in elevation from in to out")

    def compute(self):
        self.area = (pi * self.diameter**2) / 4
        self.elevation_change = self.elevation_out - self.elevation_in
