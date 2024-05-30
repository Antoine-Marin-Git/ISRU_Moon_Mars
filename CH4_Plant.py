"""
Collection of subelements for sizing CH4 silica reduction plant
"""

import numpy as np

class CH4_Plant:
    """
    Description
    -----------
    - Water production by Carbothermal Reduction of silicon oxides (here SiO2) followed by Sabatier Reaction of CO 
    - Oxygen and Hydrogen production by water electrolysis
    - Experimental plant based on 7 optic fibers that each melt a hemisphere (d = 7.5 cm each) of regolith
    - Oxygen yields typically between 10-15% and up to 28%, but for yields > 15%, significant carbon losses
    - Assumes an ideal Sabatier CO/H2 stoechiometric reaction 
    - As Sabatier reaction and water electrolysis have excellent yields (up to 95-97%, so 100% to simplify), it is assumed here that 
      the water (oxygen originally) production yield penalty is due to the carbothermal reduction itself. It is then assumed that as 
      much SiO2 and CH4 as in the ideal reaction is consumed here, but the amount of CO and H2 produced is lower (value calculated 
      according to the water load (final O2 yield originally))

    Sources
    -------
    [1] Oxygen Extraction from Minerals, NASA Presentation to University of Central Florida
        T. Muscatello
        2017
    [2] Oxygen Production via Carbothermal Reduction of Lunar Regolith
        R. J. Gustafson, B. C. White, M. J. Fidler
        2009
    [3] Payload Concept Evaluation for Water/Oxygen production on the Moon based on Thermo- or Electro-Chemical Reduction of Lunar Regolith
        S. Fereres, M. Morales, T. Denk, K. Osen, R. J. McGlen. A. Seidel, H. Madakashira, D. Urbina, D. Binns
        2021
    [4] Small Lunar Base Camp and In Situ Resource Utilization Oxygen Production Facility Power System Comparison
        A. J. Colozza
        2020
    [5] Carbon Dioxide Reprocessing Subsystem for Loop Closure as part of the Regenerative Life Support System ACLS
        F. Kappmaier, C. Matthias, J. Witt
        2016

    Input Parameters
    ----------------    
    H2O_load (kg/day): float
        Water production load requirement
        Default to 44.01 (Based on the original O2 requirement) [4]
    mass_electrolyzer (kg): float
        Mass of the electrolyzer corresponding to the H2O_load
        Default to 49.44 (cf Electrolyzer.py) [4]
    compo_fraction (.): float (0 to 1)
        Fraction of regolith being processed given a max particle admissible diameter 
        Default to 0.9 [4]
    silica_mass_fraction (.): float (0.41 to 0.445)
        Ratio of mass of silica to mass of regolith
        Default to 0.41 [4]
    power_per_fiber (W): float (86 to 111) 
        Power delivered per optic fiber [2]
    melting_temperature (K): float (> 1875)
        Temperature at which the regolith is brought to perform the carbothermal reduction of silicon oxides [2]
    melting_time (h): float (0.6 to 1.4) 
        Time for melting the regolith and perform the reaction [1] & [2]
    carbon_loss_mass_fraction (.): float (0 to 0.0017) 
        Mass fraction of carbon loss per metric ton of oxygen produced originally (matches now the water load) [2]
    efficiency_factor (.): float (0.1 to 0.15)
        Water (originally oxygen) mass yield [2]
    mole_fraction (.): float
        Determines the amount of H2 (here assumed 3, stoechiometric) that needs to be inputted to have the highest conversion yield (here assumed 100%)
    """

    def __init__(
                self,
                H2O_load,
                mass_electrolyzer,
                compo_fraction,
                silica_mass_fraction,
                power_per_fiber,
                melting_temperature,
                melting_time,
                carbon_loss_mass_fraction,
                sabatier_temperature,
                efficiency_factor,
                mole_fraction
            ):
        self.H2O_load = H2O_load
        self.mass_electrolyzer = mass_electrolyzer
        self.compo_fraction = compo_fraction
        self.silica_mass_fraction = silica_mass_fraction 
        self.power_per_fiber = power_per_fiber
        self.melting_temperature = melting_temperature
        self.melting_time = melting_time
        self.carbon_loss_mass_fraction = carbon_loss_mass_fraction
        self.sabatier_temperature = sabatier_temperature
        self.efficiency_factor = efficiency_factor
        self.mole_fraction = mole_fraction
        
        # Molar Masses (g/mol)

        M_H2 = 2
        M_CH4 = 16
        M_H2O = 18
        M_CO = 28
        M_O2 = 32
        M_si = 60
                
        """
        Resources mass flow derivations
        Calculated to take into account the water load and not a O2 load anymore 
        """
        
        # Mass flow rate of screened regolith
        # Account for the yields (efficiency factor) mentioned p.4 [2]
        
        mass_flow_reg_screened = (M_O2/(2*M_H2O))*H2O_load/efficiency_factor # kg/day
        
        # Total regolith load
        
        self.regolith_load = 2*mass_flow_reg_screened/compo_fraction # kg/day, multiplied by 2 (can be changed) to take into account regolith needed for insulation
        
        # Mass flow rate of processed silicon oxides
        
        self.mass_flow_si = silica_mass_fraction*mass_flow_reg_screened # kg/day
        
        # Mass flow rate of consumed CH4 for the reduction reaction
        
        self.cons_CH4_reduction = 2*(M_CH4/M_si)*self.mass_flow_si # kg/day, Eq. (1) [2] using SiO2
        
        # Mass flow rate of consumed CO for the Sabatier reaction
        
        self.cons_CO_Sabatier = (M_CO/M_H2O)*H2O_load # kg/day, Eq. (2) [2]
        
        # Mass flow rate of consumed H2 for the Sabatier reaction
        
        self.cons_H2_Sabatier = mole_fraction*(M_H2/M_CO)*self.cons_CO_Sabatier # kg/day, Eq. (2) [2] + can account for a non-stoechiometric system
        
        # Mass flow rate of produced CH4 from the Sabatier reaction
        
        self.prod_CH4_reduction = (M_CH4/M_CO)*self.cons_CO_Sabatier # kg/day, Slide 18 [1]
        
        # Mass flow rate of produced CO from the reduction reaction
        
        self.prod_CO_reduction = self.cons_CO_Sabatier # kg/day, Eq. (1) et (2) [2]
        
        # Mass flow rate of produced H2 from the reduction reaction
        
        self.prod_H2_reduction = 2*(M_H2/M_CO)*self.prod_CO_reduction # kg/day, Eq (1) [2]
        
        # Mass flow rate of produced H2 from the reduction reaction
        
        self.carbon_loss = (M_O2/(2*M_H2O))*carbon_loss_mass_fraction*H2O_load # kg/day, p.5 [2] (cf class Input Parameters for more details)

        """
        Number of optic fibers that are needed to melt the regolith
        One fiber create one hemispherical melt with a diameter ~ 7.5 cm
        """
               
        regolith_density = 1400 # kg/m3
        
        self.num_fibers = np.ceil(mass_flow_reg_screened/(24*((4*np.pi*(0.075/2)**3)/6)*regolith_density/melting_time)) # p.2 [2]
        
        """
        Electrical, Thermal and Total Power derivations
        """
        
        # Plant electrical Power

        self.Power_elec = self.num_fibers*power_per_fiber/1000 # kW
        
        # Plant thermal Power
        
        c_p_CO = 1046 # J/(kg.K)
        Delta_H_r_Sabatier_CO = - 206 # kJ/mol
        
        # Thermal Power brekadown
        # It is assumed CO is at the regolith melting temperature and needs then to be cooled down to the Sabatier reaction temperature
        
        Power_heat_CO_Sabatier = self.cons_CO_Sabatier*c_p_CO*(sabatier_temperature - melting_temperature)/(1000*24*60*60) # kW, power needed to cool CO from the reduction temperature to the Sabatier temperature
        Power_heat_reaction_Sabatier = (Delta_H_r_Sabatier_CO*self.cons_CO_Sabatier)/(24*60*60*M_CO*10**(-3)) # kW, heat released during Sabatier reaction
        
        # Total thermal Power
        
        self.Power_thermal = Power_heat_CO_Sabatier + Power_heat_reaction_Sabatier # kW
        
        """
        Plant mass regression, based on analogies with [4] removing Magnetic separator (mass of which is assumed constant), Electrolyzer & O2/H2 Tanks
        Accounts for the water load instead of O2 load (hence the ratio of molar masses)
        NEED to find sources to derive the mass of the Sabatier Reactor
        """
        
        mass_Sabatier_reactor = (5.5/1.2)*H2O_load # kg, p3 & 5 [5]
        self.mass = (1 - (0.43 + 0.02))*(588*(M_O2/(2*M_H2O))*H2O_load/24 - (240)) + 240 - 97.7 - mass_electrolyzer + mass_Sabatier_reactor # kg, Figures 17 & 18 [1]

    def calc_regolith_load(self):   

        return self.regolith_load
    
    def calc_cons_CH4_reduction(self):

        return self.cons_CH4_reduction   
    
    def calc_cons_CO_Sabatier(self):
        
        return self.cons_CO_Sabatier
    
    def calc_cons_H2_Sabatier(self):
    
        return self.cons_H2_Sabatier
        
    def calc_prod_CH4_Sabatier(self):

        return self.prod_CH4_reduction 
    
    def calc_prod_CO_reduction(self):
        
        return self.prod_CO_reduction
    
    def calc_prod_H2_reduction(self):

        return self.prod_H2_reduction  

    def calc_carbon_loss(self):
        
        return self.carbon_loss
    
    def calc_num_fibers(self):
    
        return self.num_fibers
    
    def calc_Power_elec(self):
        
        return self.Power_elec
    
    def calc_Power_thermal(self):
        
        return self.Power_thermal
    
    def calc_P_CH4_plant(self):

        P_CH4_plant = self.Power_elec 

        return P_CH4_plant

    def calc_mass(self):
        
        return self.mass

if __name__ == "__main__":
    model = 'CH4_Plant'  # CH4_Plant
    print_options = np.get_printoptions()
    np_precision = print_options['precision']

    match model:
        case 'CH4_Plant':
            CH4_Plant_instance = CH4_Plant(
                H2O_load = 44.01, # kg/day, Baseline = 44.01 [4]
                mass_electrolyzer = 49.44, # kg, Baseline = 49.44 
                compo_fraction = 0.9, # 0 to 1, Baseline = 0.9 [4]
                silica_mass_fraction = 0.41, # 0.41 to 0.445 [4]
                power_per_fiber = 100, # W, 86 to 111 [2]
                melting_temperature = 2000, # K, > 1875 [2]
                melting_time = 1, # h, 0.6 to 1.4 [1] & [2]
                carbon_loss_mass_fraction = 0.001, # 0 to 0.0017 [2]
                sabatier_temperature = 573.15, # 523.15 to 573.15 [3]
                efficiency_factor = 0.125, # 0 to 1
                mole_fraction = 3 # Default = 3 (stoechiometric)
                )
            
            CH4_Plant_regolith_load = CH4_Plant_instance.calc_regolith_load()
            CH4_Plant_cons_CH4_reduction = CH4_Plant_instance.calc_cons_CH4_reduction()
            CH4_Plant_prod_CH4_Sabatier = CH4_Plant_instance.calc_prod_CH4_Sabatier()
            CH4_Plant_prod_CO_reduction = CH4_Plant_instance.calc_prod_CO_reduction()
            CH4_Plant_cons_CO_Sabatier = CH4_Plant_instance.calc_cons_CO_Sabatier()
            CH4_Plant_prod_H2_reduction = CH4_Plant_instance.calc_prod_H2_reduction()
            CH4_Plant_cons_H2_Sabatier = CH4_Plant_instance.calc_cons_H2_Sabatier()
            carbon_loss = CH4_Plant_instance.calc_carbon_loss()
            CH4_Plant_P_thermal = CH4_Plant_instance.calc_Power_thermal()
            CH4_Plant_num_fibers = CH4_Plant_instance.calc_num_fibers()
            CH4_Plant_P_elec = CH4_Plant_instance.calc_Power_elec()
            P_CH4_plant = CH4_Plant_instance.calc_P_CH4_plant()
            CH4_Plant_mass = CH4_Plant_instance.calc_mass()
            # power = reduction.calc_power()
            # power = np.round(power, np_precision)

            print(f'\n CH4 SiO2 Reduction Plant: \n')

            print(f'Regolith Load (kg/day) = {CH4_Plant_regolith_load}')
            print(f'CH4 (Reduction) Consumption Rate (kg/day) = {CH4_Plant_cons_CH4_reduction}')
            print(f'CH4 (Sabatier) Production Rate (kg/day) = {CH4_Plant_prod_CH4_Sabatier}')
            print(f'CO (Reduction) Production Rate (kg/day) = {CH4_Plant_prod_CO_reduction}')
            print(f'CO (Sabatier) Consumption Rate (kg/day) = {CH4_Plant_cons_CO_Sabatier}')
            print(f'H2 (Reduction) Production Rate (kg/day) = {CH4_Plant_prod_H2_reduction}')
            print(f'H2 (Sabatier) Consumption Rate (kg/day) = {CH4_Plant_cons_H2_Sabatier}')
            print(f'Carbon loss (kg/day) = {carbon_loss}')
            print(f'Thermal Power to dissipate (kW) = {- CH4_Plant_P_thermal}')
            print(f'Number of fibers = {CH4_Plant_num_fibers}')
            print(f'Electrical Power (kW) = {CH4_Plant_P_elec}')
            print(f'CH4 SiO2 Reduction Plant Power (Total) (kW) = {P_CH4_plant}')
            print(f'Mass (kg) = {CH4_Plant_mass}')