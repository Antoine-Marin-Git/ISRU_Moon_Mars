"""
Collection of subelements for sizing resource extraction rovers.
"""

import math
import numpy as np


class BasicRegolithExtractionRover:
    """
    Basic extraction rover subelement for regolith excavation on Mars or the
    Moon. Sizes a discrete number of excavation rovers to meet a specified load.
    Power calculation only takes into account the extraction power, not
    mobility.

    Sources:
    [1] Design of an Excavation Robot: Regolith Advanced Surface Systems Operations Robot (RASSOR) 2.0
        Mueller R., Smith J., Schuler J., Nick A., Gelino N., Leucht K., Townsend I., Dokos A
        2015

    Input Parameters
    ----------------
    regolith_load (kg/d) : float
        Regolith excavation load requirement
    baseline_mass (kg) : float
        Baseline rover mass
        Default to 66 [1]
    baseline_regolith_capacity (kg/day) : float 
        Baseline rover load capacity per day
        Default to 2778 [1]
    specific_power (W/(kg/time)) : float
        Power consumption per kg of regolith excavation rate 
        Default to 4 [1]
    recharge_time (h) : float
        Time needed per day to recharge rover batteries
        Default to 8 [1]
    redundancy (.) : int
        Number to account for rover redundancy
    """

    def __init__(
        self, 
        regolith_load, 
        baseline_mass, 
        baseline_regolith_capacity, 
        specific_power, 
        recharge_time, 
        redundancy
    ):
        self.regolith_load = regolith_load
        self.baseline_mass = baseline_mass
        self.baseline_regolith_capacity = baseline_regolith_capacity
        self.specific_power = specific_power
        self.recharge_time = recharge_time
        self.redundancy = redundancy

    def calc_num_rovers(self):
        
        num_rovers = math.ceil(self.regolith_load/self.baseline_regolith_capacity) + self.redundancy

        return num_rovers

    def calc_mass(self):
        
        mass = self.baseline_mass*self.calc_num_rovers()  # kg, [1]

        return mass

    def calc_power(self):
        """
        Power to recharge the rover during the alloted recharge time
        """
        
        power = (self.regolith_load/24)*self.specific_power*(24 - self.recharge_time)/(self.recharge_time)  # kW, p.1 [1]

        return power


if __name__ == "__main__":
    model = 'BasicRegolithExtractionRover'  # BasicRegolithExtractionRover
    print_options = np.get_printoptions()
    np_precision = print_options['precision']

    match model:
        case 'BasicRegolithExtractionRover':
            extraction_rover = BasicRegolithExtractionRover(
                regolith_load = 2778.94737, # kg/day
                baseline_mass = 66, # kg
                baseline_regolith_capacity = 2778.94737, # kg/day
                specific_power = 4*10**(-3), # kW/(kg/h)
                recharge_time = 8, # h
                redundancy = 0
            )
            
            num_rovers = extraction_rover.calc_num_rovers()
            num_rovers = np.round(num_rovers, np_precision)
            mass = extraction_rover.calc_mass()
            power = extraction_rover.calc_power()
            
            print(f'\n RASSOR_v2: \n')

            print(f'Number of Rovers = {num_rovers}')
            print(f'Total Mass = {mass} (kg)')
            print(f'Total Extraction Power = {power} (kW)')
