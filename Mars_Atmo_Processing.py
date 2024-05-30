"""
Collection of subelements for sizing a Martian atmosphere processing Plant
"""

import numpy as np

class Atmo_Processing:
    """
    Description
    -----------
    - Water production by Martian atmospheric CO2 processing using Sabatier reactor
    - Two-staged Sabatier reactors (1st one high temperature & adiabatic, 2nd one moderate temperature and isothermal) to achieve 
      90-95% H2 conversion rate at the end of the two-staged process
    - Other gases than water vapor (i.e remaining CO2, H2, and produced CH4) are discarded in this model
    - Oxygen and Hydrogen production by water electrolysis
    - Check Mars_Atmo_Explanation.jpg for mass flow derivations explanations
    - Need to find data on how much power is needed to heat the catalyst beds up to the given temperature

    Sources
    -------
    [1] Small Lunar Base Camp and In Situ Resource Utilization Oxygen Production Facility Power System Comparison
        A. J. Colozza
        2020
    [2] Carbon Dioxide Reprocessing Subsystem for Loop Closure as part of the Regenerative Life Support System ACLS
        F. Kappmaier, C. Matthias, J. Witt
        2016

    Input Parameters
    ----------------    
    H2O_load (kg/day): float
        Water production load requirement
        Default to 44.01 (Based on the original O2 requirement) [1]
    mole_fraction (.): float
        Determines the amount of H2 (here assumed 3, stoechiometric) that needs to 
        be inputted to have the highest conversion yield (here assumed 100%)
        Default to 2.34 [2]
    temperature_reactor1 (K): float (around 803 K)
        Temperature at which the first Sabatier reaction in Reactor 1 takes place
        Default to 803 [2]
        Change in this value will affect power but not yield (hence a BIAS) because 
        we don't know how the yield is constrained by temperature   
    temperature_reactor2 (K): float (around 573 K)
        Temperature at which the second Sabatier reaction in Reactor 2 takes place
        Default to 573 [2]
        Change in this value will affect power but not yield (hence a BIAS) because 
        we don't know how the yield is constrained by temperature 
    temperature_water_recovery_unit (K): float (< 303 K)
        Temperature of the Water Recovery Unit (WRU) to condense water
        Default to 303 [2]
    conversion_efficiency (.): float (0.90 to 0.95)
        Efficiency of the overall process (in terms of H2 conversion)
        Default to 0.95 [2]
    """
    
    def __init__(
                self,
                H2O_load,
                mole_fraction,
                temperature_reactor1,
                temperature_reactor2,
                temperature_water_recovery_unit,
                conversion_efficiency
            ):
        self.H2O_load = H2O_load
        self.mole_fraction = mole_fraction
        self.temperature_reactor1 = temperature_reactor1
        self.temperature_reactor2 = temperature_reactor2
        self.temperature_water_recovery_unit = temperature_water_recovery_unit
        self.conversion_efficiency = conversion_efficiency
        
        # Molar Masses (kg/mol)

        M_H2 = 2*10**(-3)
        M_CH4 = 16*10**(-3)
        M_H2O = 18*10**(-3)
        M_CO2 = 44*10**(-3)
        
        """
        Resources mass flow derivations
        """
        
        # Input resources loads based on the water load requirement (kg/day)
        
        self.H2_load = (2/conversion_efficiency)*(M_H2/M_H2O)*H2O_load 
        self.CO2_load = (1/mole_fraction)*(M_CO2/M_H2)*self.H2_load 
        
        # REACTOR 1
        
        Progress_1 = (1/6)*self.H2_load/M_H2 # mol/day, progress of Reactor 1 reaction
        
        # Output mass flow rates of Reactor 1 (kg/day) 
        
        R1_H2O_out = 2*Progress_1*M_H2O 
        R1_CH4_out = Progress_1*M_CH4 
        R1_H2_out = self.H2_load - 4*Progress_1*M_H2 
        R1_CO2_out = self.CO2_load - Progress_1*M_CO2 
        
        # REACTOR 2
        
        Progress_2 = (1/4)*(1/3 + conversion_efficiency - 1)*self.H2_load/M_H2 # mol, progress of Reactor 2 reaction
        
        # Output mass flow rates of Reactor 2 (kg/day)
        
        self.R2_H2O_out = R1_H2O_out + 2*Progress_2*M_H2O 
        self.R2_CH4_out = R1_CH4_out + Progress_2*M_CH4 
        self.R2_H2_out = R1_H2_out - 4*Progress_2*M_H2 
        self.R2_CO2_out = R1_CO2_out - Progress_2*M_CO2 
        
        """
        Electrical, Thermal and Total Power derivations
        """
        
        # REACTOR 1
        
        # Power_pre_heat_1 =         # kW, p.6 [2] power needed to pre-heat the catalyst bed 1 up to 673 K
        # No heat to dissipate as the reactor is adiabatic
        
        Delta_H_r = - 165 # kJ/mol
        
        heat_losses = -(Delta_H_r*Progress_1)/(24*60*60) # kW, p.8 [2] heat losses are of the same order of magnitude than the heat produced
        
        # REACTOR 2
        
        # Power_pre_heat_2 = Power_pre_heat_1 # kW, p.6 [2] power needed to pre-heat the catalyst bed 2 up to 673 K
        
        # Cooling of output mix from Reactor 1
        
        mass_mix = R1_H2O_out + R1_CH4_out + R1_H2_out + R1_CO2_out # mass composition of the output mix from Reactor 1
        
            # Specific Heat Capacities of output gases (kJ/(kg.K))
            
        cp_H2O = 2.047
        cp_CH4 = 2.232
        cp_H2 = 14.57
        cp_CO2 = 1.102 
        cp_mix = (R1_H2O_out*cp_H2O + R1_CH4_out*cp_CH4 + R1_H2_out*cp_H2 + R1_CO2_out*cp_CO2)/mass_mix # cp_mix is the sum of all gases cp, weighted by their mass fraction    
        
        heat_cooling_R1_mix_out = mass_mix*cp_mix*(temperature_reactor1 - temperature_reactor2)/(24*60*60) # kW, p.6 [2] cooling of Reactor 1 output gases
        
        # Reactor 2 heat power to dissipate
        
        heat_reactor2 = -(Delta_H_r*Progress_2)/(24*60*60) # kW, heat released during 2nd Sabatier reaction
        
        # Water Recovery Unit (WRU)
        
        heat_cooling_R2_mix_out = mass_mix*cp_mix*(temperature_reactor1 - temperature_water_recovery_unit)/(24*60*60) # kW, p.7 [2] cooling of Reactor 2 output gases to recover water
        
        # Total heat to dissipate
        
        self.heat = heat_losses + heat_cooling_R1_mix_out + heat_reactor2 + heat_cooling_R2_mix_out
        
        """
        System mass derivation
        """
        
        self.mass = (5.5/1.2)*H2O_load # p.3 & 5 [2]
    
    def calc_CO2_load(self):
        return self.CO2_load
    
    def calc_H2_load(self):
        return self.H2_load
    
    def calc_CH4_prod(self):
        return self.R2_CH4_out
    
    def calc_heat(self):
        return self.heat
    
    def calc_mass(self):
        return self.mass
    
if __name__ == "__main__":

    Atmo_Processing_instance = Atmo_Processing(
                                            H2O_load = 44.01, # kg/day, Baseline = 44.01 [1]
                                            mole_fraction = 2.34, # Baseline = 2.34 [2]
                                            temperature_reactor1 = 803, # K, Baseline = 803 [2]
                                            temperature_reactor2 = 573, # K, Baseline = 573 [2]
                                            temperature_water_recovery_unit = 303, # < 303 K, Baseline = 303 [2]
                                            conversion_efficiency = 0.95 # 0.90 to 0.95, Baseline = 0.95 [2]
                                            )    

    H2_load = Atmo_Processing_instance.calc_H2_load()
    CO2_load = Atmo_Processing_instance.calc_CO2_load()
    CH4_prod = Atmo_Processing_instance.calc_CH4_prod()
    heat = Atmo_Processing_instance.calc_heat()
    mass = Atmo_Processing_instance.calc_mass()

    print(f'\n Atmosphere Processing Plant: \n')
    
    print(f'CO2 Load (kg/day) = {CO2_load}')
    print(f'H2 Load (kg/day) = {H2_load}')
    print(f'CH4 Production Rate (kg/day) = {CH4_prod}')
    print(f'Heat to Dissipate (kW) = {heat}')
    print(f'Mass (kg) = {mass}')
        
        
        
        
        
        
        

        