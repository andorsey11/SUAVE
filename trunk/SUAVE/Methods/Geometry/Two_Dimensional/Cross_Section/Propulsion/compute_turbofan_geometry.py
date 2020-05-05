## @ingroup Methods-Geometry-Two_Dimensional-Cross_Section-Propulsion
# engine_geometry.py
#
# Created:  Jun 15, A. Variyar 
# Modified: Mar 16, M. Vegh

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# SUAVE imports
from SUAVE.Core  import Data, Units

# package imports
import numpy as np
from math import pi, sqrt

# ----------------------------------------------------------------------
#  Correlation-based methods to compute engine geometry
# ----------------------------------------------------------------------

## @ingroup Methods-Geometry-Two_Dimensional-Cross_Section-Propulsion
def compute_turbofan_geometry(turbofan, conditions):
    """Estimates geometry for a ducted fan.

    Assumptions:
    None

    Source:
    http://adg.stanford.edu/aa241/AircraftDesign.html

    Inputs:
    turbofan.sealevel_static_thrust [N]

    Outputs:
    turbofan.
      engine_length                 [m]
      nacelle_diameter              [m]
      areas.wetted                  [m^2]

    Properties Used:
    N/A
    """    

    #unpack
    thrust            = turbofan.thrust
    core_nozzle       = turbofan.core_nozzle
    fan_nozzle        = turbofan.fan_nozzle
    bypass_ratio      = turbofan.bypass_ratio
    gamma = 1.4
    R = 287.05
    if turbofan.tag == 'openrotor' or turbofan.tag == 'openrotoraft':
    # Size the nacelle from the LPC instead of the fan
        core_mdot = turbofan.thrust.outputs.core_mass_flow_rate[0][0]# Core mass flow to fan mass flow
        core_Tt   = turbofan.low_pressure_compressor.inputs.stagnation_temperature[0][0]
        core_mach = turbofan.thrust.inputs.core_nozzle.mach_number[0][0] 
        core_Pt   = turbofan.low_pressure_compressor.inputs.stagnation_pressure[0][0]
        Area_exp = (-1*(gamma+1)/(2*(gamma-1)))
        Area_rs  = core_Pt * np.sqrt(gamma/R)* core_mach*(1+((gamma-1)/2)*core_mach**2)**(Area_exp)

        core_area = core_mdot * np.sqrt(core_Tt) / Area_rs
        core_ratio = 6 # compressor blade height to total core diameter
        compressor_height = sqrt(core_area) / (sqrt(2*pi*core_ratio+pi))
        core_diameter = 2*(compressor_height + core_ratio * compressor_height)
        core_length_to_di = 4.14 # core length versus first stage lpc diameter, taken from literature
        nacelle_diameter = core_diameter * 2.15 # k factor to add the actual nacelle and claptrap, matches literature
        L_eng_m = core_length_to_di * nacelle_diameter 

        fan_mdot = turbofan.thrust.outputs.core_mass_flow_rate[0][0]*(1/(1-turbofan.thrust.inputs.flow_through_fan)) # Core mass flow to fan mass flow
        fan_Tt   = turbofan.fan.inputs.stagnation_temperature[0][0]
        fan_mach = turbofan.thrust.inputs.fan_nozzle.mach_number[0][0] 
        fan_Pt   = turbofan.fan.inputs.stagnation_pressure[0][0]
    
        Area_exp = (-1*(gamma+1)/(2*(gamma-1)))
        Area_rs  = fan_Pt * np.sqrt(gamma/R)* fan_mach*(1+((gamma-1)/2)*fan_mach**2)**(Area_exp)

        fan_area = fan_mdot * np.sqrt(fan_Tt) / Area_rs
       # fan_height = sqrt(fan_area) / (sqrt(2*pi*turbofan.fan.spinner_ratio+pi))
        fan_radius = np.sqrt(fan_area / pi + (nacelle_diameter/2)**2)
        fan_diameter = fan_radius * 2 * 1.2 # k factor
    else:
        fan_mdot = turbofan.thrust.outputs.core_mass_flow_rate[0][0]*(1/(1-turbofan.thrust.inputs.flow_through_fan)) # Core mass flow to fan mass flow
        fan_Tt   = turbofan.fan.inputs.stagnation_temperature[0][0]
        fan_mach = turbofan.thrust.inputs.fan_nozzle.mach_number[0][0] 
        fan_Pt   = turbofan.fan.inputs.stagnation_pressure[0][0]
        Area_exp = (-1*(gamma+1)/(2*(gamma-1)))
        Area_rs  = fan_Pt * np.sqrt(gamma/R)* fan_mach*(1+((gamma-1)/2)*fan_mach**2)**(Area_exp)
        fan_area = fan_mdot * np.sqrt(fan_Tt) / Area_rs
        fan_diameter = 2 * ((sqrt(fan_area) / (sqrt(pi))) / (1-(1-turbofan.fan.spinner_ratio)**2))
        nacelle_diameter = 1.12 * fan_diameter
        L_eng_m = turbofan.fan.nacelle_length_to_fan_di  * nacelle_diameter

    #Pack
    turbofan.engine_length    = L_eng_m
    turbofan.nacelle_diameter = nacelle_diameter
    turbofan.fan_diameter     = fan_diameter
  
    turbofan.areas.wetted     = 1.1*np.pi*turbofan.nacelle_diameter*turbofan.engine_length


# ----------------------------------------------------------------------
#   Module Tests
# ----------------------------------------------------------------------
if __name__ == '__main__':
    print()
