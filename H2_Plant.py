"""
Collection of subelements for sizing H2 ilmenite reduction plant
"""

import numpy as np
from scipy import integrate

class H2_Plant:
    """
    Description
    -----------
    - Water production by Hydrogen Reduction of Ilmenite, accounting for ALL systems involved
    - Oxygen and Hydrogen production by water electrolysis

    Sources
    -------
    [1] Small Lunar Base Camp and In Situ Resource Utilization Oxygen Production Facility Power System Comparison
        A. J. Colozza
        2020

    Input Parameters (cf Table 5 [1])
    ----------------
    H2O_load (kg/day): float
        Water production load requirement
        Default to 44.01 (Based on the original O2 requirement) [1]
    mass_electrolyzer (kg): float
        Mass of the electrolyzer corresponding to the H2O_load
        Default to 49.44 (cf Electrolyzer.py) [1]
    power_electrolyzer (kW): float
        Power of the electrolyzer corresponding to the H2O_load
        Default to 9.055 (cf Electrolyzer.py) [1]
    compo_fraction (.): float (0 to 1)
        Fraction of regolith processed given a max particle admissible  diameter 
        Default to 0.9 [1]
    ilmenite_separation_factor (.): float (0 to 1)
        Ilmenite separation process efficiency
        Default to 0.9 [1]    
    ilmenite_mass_fraction (.): float (0.004 to 0.128)
        Ratio of mass of ilmenite to mass of regolith
        Default to 0.07 [1]
    hydrogen_density_in_reg (kg/m3): float (0.1 to 0.2)
        Quantity of trapped hydrogen in regolith    
    regolith_temperature (K): float (100 to 384)
        Temperature of processed regolith
        Default to 384 [1]
    reactor_diameter (m): float
        Diameter of reactor tank
        Default to 0.8 [1]
    reactor_height (m) : float
        Height of reactor tank
        Default to 0.8 [1]
    remain_at_temperature_time (h): float
        Time during the regolith remains at the reaction temperature
        Default to 1 [1] 
    """

    def __init__(
                self,
                H2O_load,
                mass_electrolyzer,
                power_electrolyzer,
                compo_fraction,
                separation_factor,
                ilmenite_mass_fraction,
                hydrogen_density_in_reg,
                regolith_temperature,
                reactor_diameter,
                reactor_height,
                #fraction_volume_renewed,
                remain_at_temperature_time
                ):
        
        self.H2O_load = H2O_load
        self.mass_electrolyzer = mass_electrolyzer
        self.power_electrolyzer = power_electrolyzer
        self.compo_fraction = compo_fraction
        self.separation_factor = separation_factor
        self.ilmenite_mass_fraction = ilmenite_mass_fraction
        self.hydrogen_density_in_reg = hydrogen_density_in_reg
        self.regolith_temperature = regolith_temperature
        self.reactor_diameter = reactor_diameter
        self.reactor_height = reactor_height
        #self.fraction_volume_renewed = fraction_volume_renewed
        self.remain_at_temperature_time = remain_at_temperature_time
        
        # Molar Masses (g/mol)

        M_H2 = 2
        M_H2O = 18
        M_O2 = 32
        M_il = 151.7 # TO BE CHECKED ==> [1] says 308 and seems to be wrong, should be 151.7
        
        """
        Resources mass flow derivations
        Calculated to take into account the water load and not a O2 load anymore 
        """
        
        # Mass flow rate of processed ilmenite        
        self.mass_flow_il = (M_il/M_H2O)*H2O_load/separation_factor # kg/day, Eq. (22) [1]
        
        # Mass flow rate of regolith
        mass_flow_reg_screened = self.mass_flow_il/ilmenite_mass_fraction # kg/day, decomposition of Eq. (17) [1]
        self.regolith_load = mass_flow_reg_screened/compo_fraction # kg/day, decomposition of Eq. (17) [1]
    
        # Mass flow rate of released H2 when ilmenite is heated above 900°C
        rho_reg = 1400 # kg   
        self.prod_H2_il_heating = (hydrogen_density_in_reg/rho_reg)*self.mass_flow_il # kg/day, p.9 [1]
        
        # Mass flow rate of consumed H2 for the reduction reaction
        self.cons_H2_reduction = (M_H2/M_H2O)*H2O_load # kg/day, Eq. (4) [1]
        
        """
        Electrical, Thermal and Total Power derivations
        """
        
        # Plant thermal power breakdown
        
        def c_p_il(T):
            """
            Ilmenite specific heat capacity as a function of the temperature
            """

            return (-1848.5 + 1047.41*np.log10(T)) # J/(kgK) Eq. (1) [1]
        
        Reduction_Reaction_Enthalpy = 294 # kJ/kg
        ilmenite_density = 1400 # kg/m3
        
        # Compute the fraction of the reator that is renewed per unit of time
        # Direct influence on the heating power
        
        fraction_volume_renewed = ((4*ilmenite_mass_fraction)/(ilmenite_density*np.pi*reactor_height*reactor_diameter**2))*self.regolith_load/24 # /h, Eq. (7) [1]
        # print('dot_V =', fraction_volume_renewed)

        if fraction_volume_renewed*remain_at_temperature_time >= 1: # Eq. (18) [1]
            
            raise ValueError(f"The time needed to heat the ilmenite must be greater than 0, i.e the product of dot_V and t_rt must be strictly less than 1")
            
        else: 

            Power_reaction = Reduction_Reaction_Enthalpy*separation_factor*self.mass_flow_il/(24*60*60) # kW, Eq. (21) [1] different by a almost a factor 2 due to the difference in M_il
            #print('P_reac = ', Power_reaction)
            Power_heating = (ilmenite_density*integrate.quad(c_p_il, regolith_temperature, 1275)[0]*np.pi*(reactor_diameter**2)*reactor_height*(1 - remain_at_temperature_time*fraction_volume_renewed))/(1000*4*60*60*(1/fraction_volume_renewed - remain_at_temperature_time)) # kW, Eq. (19) [1] assume cp_il(1275) constant to find the paper values when M_il = 308
            #print('P_heat = ', Power_heating)
            Power_losses = (0.03/0.97)*(Power_reaction + Power_heating) # Figure 11 [1], losses are approximately 3% of total thermal power
            #print('P_losses = ', Power_losses)
    
            self.Power_thermal = Power_reaction + Power_heating + Power_losses # kW, Eq (28) [1]

        # Plant electrical Power breakdown
        
        self.Power_elec = (0.04/0.96)*power_electrolyzer # kW, Figure 12 [1] & Eq (27) [1], electrical power other than electrolyzer power is 4% of the total power
        
        # Total Power
        
        if self.Power_thermal is not None:

                self.Power_total = self.Power_thermal + self.Power_elec # kW  
                          
        else:
                self.Power_total = None
                
        """
        Plant mass regression 
        Removes Electrolyzer & O2/H2 Tanks contribution and accounts for the water load instead
        """

        self.mass = (1 - (0.43 + 0.02))*(588*(M_O2/(2*M_H2O))*H2O_load/24 - (240)) + 240 - mass_electrolyzer # kg, Figures 17 & 18 [1]

    def calc_regolith_load(self):
        
        return self.regolith_load
    
    def calc_prod_H2_il_heating(self):
        
        return self.prod_H2_il_heating 
    
    def calc_cons_H2_reduction(self):
    
        return self.cons_H2_reduction
        
    def calc_Power_thermal(self):
    
        return self.Power_thermal
    
    def calc_Power_elec(self):

        return self.Power_elec

    def calc_Power_total(self):
        
        return self.Power_total

    def calc_mass(self):
        
        return self.mass

if __name__ == "__main__":
    model = 'H2_Plant'  # H2_Plant
    print_options = np.get_printoptions()
    np_precision = print_options['precision']

    match model:
        case 'H2_Plant':
            H2_Plant_instance = H2_Plant(
                H2O_load = 44.01, # kg/day, Baseline = 44.01 (24*18/16*O2_load) 
                mass_electrolyzer = 49.44, # kg, Baseline = 49.44
                power_electrolyzer = 9.05, # kW, Baseline = 9.05
                compo_fraction = 0.9, # 0 to 1, Baseline = 0.9 [1]
                separation_factor = 0.9, # 0 to 1, Baseline = 0.9
                ilmenite_mass_fraction = 0.07, # 0.004 to 0.128, Baseline = 0.07 if we consider density of ilmenite = density of regolith (true for bulk density) [1]
                hydrogen_density_in_reg = 0.15, # kg/m3, 0.1 to 0.2 [1]
                regolith_temperature = 384, # K, 100 to 384, Baseline = 384 [1]
                reactor_diameter = 0.8, # m, Baseline = 0.8 [1]
                reactor_height = 0.8, # m, Baseline = 0.8 [1]
                #fraction_volume_renewed = 0.03, # 0 to 1, Baseline = 0.03 calculation from [1]
                remain_at_temperature_time = 1 # h, Baseline = 1 [1]
                )
            
    H2_Plant_regolith_load = H2_Plant_instance.calc_regolith_load()
    H2_Plant_prod_H2_il_heating = H2_Plant_instance.calc_prod_H2_il_heating()
    H2_Plant_cons_H2_reduction = H2_Plant_instance.calc_cons_H2_reduction()
    H2_Plant_Power_thermal = H2_Plant_instance.calc_Power_thermal()
    H2_Plant_Power_elec = H2_Plant_instance.calc_Power_elec()
    H2_Plant_Power_total = H2_Plant_instance.calc_Power_total()
    H2_Plant_mass = H2_Plant_instance.calc_mass()
    # power = reduction.calc_power()
    # power = np.round(power, np_precision)

    print(f'\n H2 ilmenite Reduction Plant: \n')

    print(f'Regolith Load (kg/day) = {H2_Plant_regolith_load}')
    print(f'H2 (Ilmenite Heating) Production Rate (kg/day) = {H2_Plant_prod_H2_il_heating}')
    print(f'H2 Consumption Rate (kg/day) = {H2_Plant_cons_H2_reduction}')
    print(f'Thermal Power (kW) = {H2_Plant_Power_thermal}')
    print(f'Electrical Power (kW) = {H2_Plant_Power_elec}')
    print(f'H2 Ilmenite Reduction Plant Power (Total) (kW) = {H2_Plant_Power_total}')
    print(f'H2 Ilmenite Reduction Plant mass (kg) = {H2_Plant_mass}')
