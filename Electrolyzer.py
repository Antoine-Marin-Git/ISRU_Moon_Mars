class Electrolyzer:
    """
    Description
    -----------
    Electrolyzer to perform water electrolysis and produce O2/H2

    Sources
    -------
    [1] Small Lunar Base Camp and In Situ Resource Utilization Oxygen Production Facility Power System Comparison
        A. J. Colozza
        2020

    Input Parameters
    ----------------
    etha (.): float(0 to 1)
        Electrolyzer power efficiency
        Default 0.72 [1]
    H2O load (kg/day): float
        Water production load requirement
        Default to 44.01 (Based on the original O2 requirement) [1]
    """
    def __init__(
                self, 
                etha,
                H2O_load
                ):
        
        self.etha = etha
        self.H2O_load = H2O_load
        
        Delta_G_H2O = 230.4 # kJ/mol, p. 14 [1]
        M_H2O = 18 # g/mol
        
        # Electrolyzer power

        self.power = (Delta_G_H2O*H2O_load)/(24*60*60*etha*M_H2O*10**(-3)) # Eq. (26) [1]
        
        # Heat to dissipate
        
        self.heat_to_dissipate = (Delta_G_H2O*H2O_load)*(1/etha - 1)/(24*60*60*M_H2O*10**(-3)) # Eq. (30) [1]
    
        # Electrolyzer mass. Cf Table 6 [1] for the following constants
    
        S_es = 2.00
        S_wt = 0.10
        S_f = 0.12
        S_pl = 0.52
        S_cu = 0.16
        S_w = 0.30
        S_he = 1.00
        S_wp = 0.27
        S_chv = 0.08
        S_fr = 0.62
        S_cv = 0.16
        S_s = 0.07
        S_fs = 0.06
    
        self.mass = self.power*(S_es + S_wt + S_f + S_pl + S_cu + S_w + S_he + S_wp + S_chv + S_fr + S_cv + S_s + S_fs) # Eq. (29) [1]

    def calc_power(self):
        
        return self.power
        
    def calc_heat_to_dissipate(self):
        
        return self.heat_to_dissipate
        
    def calc_mass(self):
            
        return self.mass

if __name__ == "__main__":

    Electrolyzer_instance = Electrolyzer(
        etha = 0.72,
        H2O_load = 44.01 # kg/day, Baseline = 44.01 [1]
        )    

    power = Electrolyzer_instance.calc_power()
    heat = Electrolyzer_instance.calc_heat_to_dissipate()
    mass = Electrolyzer_instance.calc_mass()

    print(f'\n Electrolyzer: \n')
    print(f'Power (kW) = {power}')
    print(f'heat to dissipate (kW) = {heat}')
    print(f'Mass (kg) = {mass}')

    
