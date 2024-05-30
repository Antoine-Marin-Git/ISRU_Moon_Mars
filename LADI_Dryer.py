import numpy as np
import math
from scipy.optimize import fsolve
from scipy import integrate

class LADI_Dryer:
    """
    Description
    ----------- 
    - Water extraction by regolith heating BELOW TRIPLE POINT CONDITIONS at constant pressure dryer_pressure
    - Modeling of the overall water extraction physics, NOT the engineering systems (hence a gap in power requirements) 
      ==> Possibility to rely on ref [2]
    - Regolith load evenly shared among dryers (e.g, if a dryer can process 400 kg/day, requirement is 700 kg/day, 2 dryers 
      are needed and process 350 kg/day)
    - Efficiency of the water extraction assumed to be water_extraction_efficiency = 1
    - For ice mining only, set water_mass_fraction = 1

    Sources
    ------- 
    [1] Planetary and Terrestrial Mining Sciences Symposium (PTMSS) and Space Resources Roundtable (SRR), NASA
        2021
    [2] Small Lunar Base Camp and In Situ Resource Utilization Oxygen Production Facility Power System Comparison
        A. J. Colozza
        2020
    [3] Ice Mining in Lunar Permanently Shadowed Regions
        G. F. Sowers, C. B. Dreyer
        2019

    Input Parameters
    ---------------- 
    H2O_load (kg/day): float
        Water production load requirement
    compo_fraction (.): float (0 to 1)
        Fraction of regolith processed given a max particle admissible  diameter 
        Default to 0.9 [1]
    water_mass_fraction (.): float (0.029 to 0.085)
        Ratio of mass of water to mass of regolith [3]
    dryer_pressure (Pa) : float
        Operating Dryer Pressure below triple points conditions [1]
    inital_temperature (K) : float
        Initial Temperature of the extracted regolith 
    final_temperature (K): float
        Final (Operating) Dryer Temperature 
    heating_duration (h) : float 
        Residence time for heating
    fraction_volume_renewed (/h) : float 
        LADI volume renewed every hour to take another batch of regolith
        Default to 0.5 (arbitrary, need data)
    water_extraction_efficiency (.): float (0 to 1)
        Efficiency of the water extraction process    
        Default to 1 (ideal process) 
    """

    def __init__(
                self, 
                H2O_load,
                compo_fraction,
                water_mass_fraction,
                dryer_pressure, 
                inital_temperature, 
                final_temperature, 
                remain_at_temperature_time,
                fraction_volume_renewed,
                water_extraction_efficiency 
                ):
         
        self.H2O_load = H2O_load
        self.compo_fraction = compo_fraction
        self.water_mass_fraction = water_mass_fraction
        self.dryer_pressure = dryer_pressure
        self.inital_temperature = inital_temperature
        self.final_temperature = final_temperature 
        self.remain_at_temperature_time = remain_at_temperature_time
        self.fraction_volume_renewed = fraction_volume_renewed
        self.water_extraction_efficiency = water_extraction_efficiency 
        
        # Triple Point Conditions
        
        triple_point_pressure = 611.657  # Pa
        triple_point_temperature = 273.16  # K
        
        def T_sub(T):
            """
            Determine the water's sublimation temperature given the dryer's operating pressure
            """
            return dryer_pressure - triple_point_pressure*np.exp(6293*(1/triple_point_temperature - 1/T) - 0.555*np.log(T/triple_point_temperature) - 1/T)
         
        self.sublimation_temperature = fsolve(T_sub, 250)[0]  # K 
        
        # --- Checks if the input temperatures make sense ---

        if dryer_pressure > triple_point_pressure:
            raise ValueError(f'The dryer pressure must be lower than the triple point pressure: {triple_point_pressure} Pa')
        if inital_temperature > final_temperature:
            raise ValueError(f'The initial temperature must be less than the final temperature: {triple_point_temperature} K')
        if inital_temperature > self.sublimation_temperature:
            raise ValueError(f'The initial temperature must be less than the sublimation temperature: {self.sublimation_temperature} K')
        if final_temperature < self.sublimation_temperature:
            raise ValueError(f'The final temperature must be greater than the sublimation temperature: {self.sublimation_temperature} K')
        
        """
        Resources mass flow derivations
        Calculated to take into account the water load and not a O2 load anymore 
        """
        
        # Densities (kg/m3)
        
        regolith_density = 1400  
        ice_density = 910 
        
        self.mass_flow_reg_screened = H2O_load/(water_extraction_efficiency*water_mass_fraction) # kg/day, amount of regolith to be extracted
        self.regolith_load = self.mass_flow_reg_screened/compo_fraction  # kg/day, amount of regolith to be extracted given only a certain size of grain is processed
        self.dryer_volume = 0.0246 # m3, based on ROUGH estimations, slide 9 [1]
        # self.dryer_volume = total_mass_flow_reg_screened*heating_duration/(24*regolith_density)  # m3
        # print('Dryer Volume = ', self.dryer_volume, 'm3')
        
        # fraction_volume_renewed = (mass_flow_reg_screened/24)/(self.dryer_volume*((1 - water_mass_fraction)*regolith_density + water_mass_fraction*ice_density)) # /h, adapted from Eq. (7) [2]
        # print('dot_V =', fraction_volume_renewed)

        if fraction_volume_renewed*remain_at_temperature_time >= 1: # Eq. (18) [1]
            
            raise ValueError(f"The time needed to heat the ilmenite must be greater than 0, i.e fraction_volume_renewed*remain_at_temperature_time must be strictly less than 1")

        else:
            
            self.dryer_capacity = 24*fraction_volume_renewed*self.dryer_volume*((1 - water_mass_fraction)*regolith_density + water_mass_fraction*ice_density) # kg/day, mass flow rate of mixed ice and regolith processed per day per dryer
            
                        
            """
            Thermal and Total Power derivations
            """

            # --- Calculate water power usages ---
            
            # Water Specific Heat Capacities (kJ/(kg.K))
            
            cp_ice = 2.10
            cp_steam = 1.9
            
            # Water Specific Enthalpies (kJ/kg)
            
            enthalpy_fusion = 0.3335e3  
            enthalpy_vaporization = 2.257e3 
            
            Q_heat_ice = (regolith_density/ice_density)*water_mass_fraction*ice_density*self.dryer_volume*(self.regolith_load/(self.calc_num_dryers()*self.dryer_capacity))*cp_ice*(self.sublimation_temperature - inital_temperature) # kJ, energy to heat the ice up to sublimation temperature, adapted from Eq. (19) [2] and knowing that the dryer volume is not only full of regolith, but regolith + ice (ratio of densities), and that the dryer is not necessarily full
            Q_sublimation = (regolith_density/ice_density)*water_mass_fraction*ice_density*self.dryer_volume*(self.regolith_load/(self.calc_num_dryers()*self.dryer_capacity))*(enthalpy_fusion + enthalpy_vaporization) # kJ, energy to sublimate the ice
            Q_heat_vapor = (regolith_density/ice_density)*water_mass_fraction*ice_density*self.dryer_volume*(self.regolith_load/(self.calc_num_dryers()*self.dryer_capacity))*cp_steam*(final_temperature - self.sublimation_temperature) # kJ, energy to heat the steam up to the final temperature (using mass of steam = mass of ice that has been heated)
            
            # Q_heat_ice = water_mass_fraction*mass_flow_reg_screened*cp_ice*(self.sublimation_temperature - inital_temperature)/(24*60*60) # kW, power to heat the ice up to sublimation temperature
            # Q_sublimation = water_mass_fraction*mass_flow_reg_screened*(enthalpy_fusion + enthalpy_vaporization)/(24*60*60) # kW, power to sublimate the ice
            # Q_heat_vapor = water_mass_fraction*mass_flow_reg_screened*cp_steam*(final_temperature - self.sublimation_temperature)/(24*60*60) # kW, power to heat the steam up to the final temperature
            
            # self.water_extraction_power = (Q_sublimation + Q_heat_ice + Q_heat_vapor)*((1)/(3600*(1/fraction_volume_renewed - remain_at_temperature_time)))  # kW, total power to extract water vapor from the regolith adapted from Eq. (19) [2]
            self.water_extraction_power = (Q_sublimation + Q_heat_ice + Q_heat_vapor)*((1 - fraction_volume_renewed*remain_at_temperature_time)/(3600*(1/fraction_volume_renewed - remain_at_temperature_time)))  # kW, real formula from Eq. (19) [2] I think it is wrong.
            
            # --- Calculate regolith power usages PER DRYER ---
            
            def c_p_reg(T):
                """
                Ilmenite specific heat capacity as a function of the temperature
                """
                
                return (-1848.5 + 1047.41*np.log10(T)) # J/(kg.K)
            
            self.regolith_heating_power = integrate.quad(c_p_reg, inital_temperature, final_temperature)[0]*(1 - (regolith_density/ice_density)*water_mass_fraction)*regolith_density*self.dryer_volume*(self.regolith_load/(self.calc_num_dryers()*self.dryer_capacity))*((1 - fraction_volume_renewed*remain_at_temperature_time)/(1000*60*60*(1/fraction_volume_renewed - remain_at_temperature_time))) # kW, power needed to heat regolith up to the final temperature

            # --- Calculate losses ---
            
            self.power_losses = (0.03/0.97)*(self.water_extraction_power + self.regolith_heating_power) # kW, Adapted from Figure 11 [1], losses are approximately 3% of total thermal power
            
            # --- Total Power --- 

            self.total_power = self.water_extraction_power + self.regolith_heating_power + self.power_losses # kW
        
        # --- Mass ---

        """
        Plant mass regression 
        Takes only into account the Conveyor belts, Vibrating screen and Reactor tank (can be assumed to be the equivalent of the 
        dryer section where the regolith is being heated, to be changed!) contribution and accounts for the water load instead
        NEED of much more reliable info on LADI mass
        """
        
        self.mass = 26.9 + 68.4 + 50.9 # kg, Figures 17 & 18 [1]
        
    def calc_num_dryers(self):
        
        num_dryers = math.ceil(self.mass_flow_reg_screened/self.dryer_capacity) # Possibility to add a redudancy parameter

        return num_dryers
    
    def calc_mass(self):
        return self.mass*self.calc_num_dryers()
    
    def calc_power(self):
        return self.total_power

if __name__ == "__main__":

    LADI_test = LADI_Dryer(
        H2O_load = 44.01, # kg/day
        compo_fraction = 0.9, # 0 to 1
        water_mass_fraction = 0.057, # 0.029 to 0.085
        dryer_pressure = 500, # < 611 Pa
        inital_temperature = 120, # K
        final_temperature = 280, # K
        remain_at_temperature_time = 1, # h
        fraction_volume_renewed = 0.9, # /h
        water_extraction_efficiency = 1, # 0 to 1
        )
    
    LADI_sublimation_temperature = LADI_test.sublimation_temperature
    LADI_regolith_load = LADI_test.regolith_load
    LADI_dryer_capacity = LADI_test.dryer_capacity
    LADI_ice_load = LADI_test.H2O_load/LADI_test.water_extraction_efficiency
    LADI_water_extraction_power = LADI_test.water_extraction_power*LADI_test.calc_num_dryers()
    LADI_regolith_heating_power = LADI_test.regolith_heating_power*LADI_test.calc_num_dryers()
    LADI_total_power = LADI_test.calc_power()*LADI_test.calc_num_dryers()
    LADI_mass = LADI_test.calc_mass()
    num_dryers = LADI_test.calc_num_dryers()
    
    if LADI_test.water_mass_fraction == 1:
        
        print(f'\n LADI: \n')

        print(f'Sublimation Temperature at the Operating Pressure (K) = {LADI_sublimation_temperature}')
        print(f'Ice Load (kg/day) = {LADI_ice_load}')
        print(f'Water Extraction Power (kW) = {LADI_water_extraction_power}')
        print(f'Regolith Heating Power (kW) = {LADI_regolith_heating_power}')
        print(f'Dryer Power (Total) (kW) = {LADI_total_power}')
        print(f'Mass (kg) = {LADI_mass}')
        
    else:
        
        print(f'\n LADI: \n')

        print(f'Regolith Load (kg/day) = {LADI_regolith_load}')
        print(f'Dryer Capacity (kg/day) = {LADI_dryer_capacity}')
        print(f'Number of Dryers = {num_dryers}')
        print(f'Sublimation Temperature at the Operating Pressure (K) = {LADI_sublimation_temperature}')
        print(f'Water Extraction Power (kW) = {LADI_water_extraction_power}')
        print(f'Regolith Heating Power (kW) = {LADI_regolith_heating_power}')
        print(f'Dryer(s) Power (Total) (kW) = {LADI_total_power}')
        print(f'Mass (kg) = {LADI_mass}')


