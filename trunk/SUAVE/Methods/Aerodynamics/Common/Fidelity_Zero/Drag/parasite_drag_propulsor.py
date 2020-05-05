## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
# parasite_drag_propulsor.py
# 
# Created:  Dec 2013, SUAVE Team
# Modified: Jan 2016, E. Botero          

#Sources: Stanford AA241 Course Notes
#         Raymer: Aircraft Design: A Conceptual Approach

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
from SUAVE.Core import Data
from SUAVE.Methods.Aerodynamics.Common.Fidelity_Zero.Helper_Functions import compressible_turbulent_flat_plate

# package imports
import numpy as np

# ----------------------------------------------------------------------
#   Parasite Drag Propulsor
# ----------------------------------------------------------------------

## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
def parasite_drag_propulsor(state,settings,geometry):
    """Computes the parasite drag due to the propulsor

    Assumptions:
    Basic fit

    Source:
    adg.stanford.edu (Stanford AA241 A/B Course Notes)

    Inputs:
    state.conditions.freestream.
      mach_number                                [Unitless]
      temperature                                [K]
      reynolds_number                            [Unitless]
    geometry.      
      nacelle_diameter                           [m^2]
      areas.wetted                               [m^2]
      engine_length                              [m]

    Outputs:
    propulsor_parasite_drag                      [Unitless]

    Properties Used:
    N/A
    """

    # unpack inputs
    conditions    = state.conditions
    configuration = settings
    
    propulsor = geometry
    Sref      = propulsor.nacelle_diameter**2. / 4. * np.pi
    Swet      = propulsor.areas.wetted





    l_prop = propulsor.engine_length
    d_prop = propulsor.nacelle_diameter
    
    # conditions
    freestream = conditions.freestream
    Mc  = freestream.mach_number
    Tc  = freestream.temperature    
    re  = freestream.reynolds_number
    q_free = freestream.dynamic_pressure
    q_delta = [1]

    drag_delta = 0
    #propulsor.tag = "open_rotor"
    if (propulsor.tag == "openrotor"):
        Swet = Swet * .8  *.6 # One part is slipper on the wing, the first part to the back of the fan is not airframe drag
       # Mc = propulsor.fan_nozzle.outputs.mach_number[0]
       # Tc = propulsor.fan_nozzle.outputs.static_temperature[0]
        # need to increase the effective drag due to change in q  -- Drag  = q * S * Cd so we ratio the Cd up by delta q
        q_new = .5 * propulsor.fan_nozzle.outputs.density * propulsor.fan_nozzle.outputs.velocity**2
        q_delta = q_new[0] / q_free[0]
        #Need to add wing scrubbing
        chord_affected = propulsor.scrubbed_chord
        span_affected = propulsor.fan_diameter
        area_affected = (chord_affected * span_affected + chord_affected * (span_affected - propulsor.nacelle_diameter)) * propulsor.number_of_engines # Don't double count the nacelle area
        # Get baseline drag of this section of wing
        Re_wing = re * chord_affected 
        cf_wing, k_wing, k_reyn_wing = compressible_turbulent_flat_plate(Re_wing,Mc,Tc)
        drag_delta = (q_delta-1) * area_affected * cf_wing  / Sref * 1.3 # Engineering judgment form factor and extra turbulence
        #drag_delta = 0
        #q_delta[0] = 1
        #import pdb; pdb.set_trace()
    #print(drag_delta)
    # reynolds number
    Re_prop = re*l_prop
    
    # skin friction coefficient
    cf_prop, k_comp, k_reyn = compressible_turbulent_flat_plate(Re_prop,Mc,Tc)
    
    ## form factor according to Raymer equation (pg 283 of Aircraft Design: A Conceptual Approach)
    k_prop = 1 + 0.35 / (float(l_prop)/float(d_prop))  
    k_prop = k_prop * q_delta[0] #Store the q_delta in the k factor
    # find the final result    
    propulsor_parasite_drag = k_prop * cf_prop * Swet / Sref + drag_delta
   # print(propulsor_parasite_drag)
    # dump data to conditions
    propulsor_result = Data(
        wetted_area               = Swet    , 
        reference_area            = Sref    , 
        parasite_drag_coefficient = propulsor_parasite_drag ,
        skin_friction_coefficient = cf_prop ,
        compressibility_factor    = k_comp  ,
        reynolds_factor           = k_reyn  , 
        form_factor               = k_prop  ,
    )
    conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag] = propulsor_result    
  
    return propulsor_parasite_drag
