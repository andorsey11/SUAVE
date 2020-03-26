## @ingroup Methods-Weights-Correlations-Propulsion
# integrated_propulsion.py
# 
# Created:  Jan 2014, M. A. Wendorff 
# Modified: Feb 2014, A. Wendorff
#           Feb 2016, E. Botero

# ----------------------------------------------------------------------
#   Integrated Propulsion
# ----------------------------------------------------------------------
from SUAVE.Core import Units

## @ingroup Methods-Weights-Correlations-Propulsion
def integrated_propulsion(propulsors, engine_wt_factor = 1.6):
    """ Calculate the weight of the entire propulsion system 
    
    Assumptions:
            The propulsion system is a fixed 60% greater than the dry engine alone. 
            The propulsion system includes the engines, engine exhaust, reverser, starting,
            controls, lubricating, and fuel systems. The nacelle and pylon weight are also
            part of this calculation.           
            
    Source: 
            N/A
            
    Inputs:
            engine_jet - dry weight of the engine                                             [kilograms]
            num_eng - total number of engines on the aircraft                                 [dimensionless]
            engine_wt_factor - weight increase factor for entire integrated propulsion system [dimensionless]
    
    Outputs:
            weight - weight of the full propulsion system                                     [kilograms]
        
    Properties Used:
            N/A
    """   
    if propulsors.tag == 'openrotor':
        rpm_fan = 1100
        gear_ratio = 6
        power = propulsors.takeoff_power[0][0] / Units.hp
        num_eng = propulsors.thrust.inputs.number_of_engines
        # Use what a turbofan thrust would be SLS
        thrust_sls_en = propulsors.design_thrust * 1.255 / Units.force_pound / 2 # Convert N to lbs force  
        engine_jet = (0.4054*thrust_sls_en ** 0.9255) * Units.lb # Convert lbs to kg
        gearbox_param = (power/rpm_fan)**.75 * (gear_ratio)**.15 # Convert to kg
        gearbox_weight = -37.42 + 116.32 * gearbox_param * Units.lbs
        power = propulsors.takeoff_power[0][0] / 1000 # KW
        fan_diameter = propulsors.fan_diameter
        activity_factor = 150
        max_tip_speed = .95 * 344 # m/s max tip speed
        num_blades = 10 
        fan_weight = (2.476 + 2.005 * (power/(fan_diameter**2))**.35) * fan_diameter ** 2.5 * (activity_factor/231)**.75 * (max_tip_speed/243.6)**.3 * (num_blades/8)**.65
        nacelle_weight = 0
        thrust_rev_weight = 0 
        engine_controls   = .26 * num_eng * (thrust_sls_en **.5) * Units.lb

        weight = num_eng*(engine_jet*1.1  + engine_controls + fan_weight * 2 + gearbox_weight) # Calibrate engine jet, dual fans
        #import pdb; pdb.set_trace()
        
    else:    
        power = propulsors.takeoff_power[0][0] / Units.hp
        num_eng = propulsors.thrust.inputs.number_of_engines

        thrust_sls_en = propulsors.sealevel_static_thrust / Units.force_pound # Convert N to lbs force  
    
    # process
        engine_jet = (0.4054*thrust_sls_en ** 0.9255) * Units.lb # Convert lbs to kg
     
    #add the nacelle
        nacelle_diameter = propulsors.nacelle_diameter / Units.inches
        nacelle_length   = propulsors.engine_length / Units.inches
   # nacelle_gauge    = .1 #inches
   # nacelle_weight   = 1.1 * nacelle_diameter * 3.14 * nacelle_length * 2 * num_eng * nacelle_gauge * .1 * Units.kg
        nacelle_weight  = .25 * num_eng * (nacelle_diameter / 12) * (nacelle_length / 12) * (thrust_sls_en**.36) * Units.lb
    # Thrust reverser weight
    # https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20170005851.pdf
        thrust_rev_weight = .034 * thrust_sls_en * num_eng * Units.lb
        engine_controls   = .26 * num_eng * (thrust_sls_en **.5) * Units.lbs
        weight = engine_jet * num_eng + nacelle_weight + thrust_rev_weight + engine_controls

    return weight
