## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
# compressibility_drag_wing.py
# 
# Created:  Dec 2013, SUAVE Team
# Modified: Nov 2016, T. MacDonald
#        

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# SUAVE imports
from SUAVE.Core import Data
from SUAVE.Components import Wings

# package imports
import numpy as np
import scipy as sp


# ----------------------------------------------------------------------
#  The Function
# ----------------------------------------------------------------------

## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
def compressibility_drag_wing_BWB(state,settings,geometry):
    """Computes compressibility drag for a wing

    Assumptions:
    Subsonic to low transonic
    Supercritical airfoil

    Source:
    adg.stanford.edu (Stanford AA241 A/B Course Notes)

    Inputs:
    state.conditions.
      freestream.mach_number                         [Unitless]
      aerodynamics.lift_breakdown.compressible_wings [Unitless]
    geometry.thickness_to_chord                      [Unitless]
    geometry.sweeps.quarter_chord                    [radians]

    Outputs:
    total_compressibility_drag                       [Unitless]

    Properties Used:
    N/A
    """ 
    #import pdb; pdb.set_trace()
    # unpack
    conditions    = state.conditions
    configuration = settings    # unused
    total_compressibility_drag = 0.0

    wing = geometry
    #Iterate over the wing segments and sum it up
    if wing.tag == 'main_wing':
        wing_lifts = conditions.aerodynamics.lift_breakdown.compressible_wings # currently the total aircraft lift
    elif wing.vertical:
        wing_lifts = 0
    else:
        wing_lifts = 0.15 * conditions.aerodynamics.lift_breakdown.compressible_wings
    mach           = conditions.freestream.mach_number
    drag_breakdown = conditions.aerodynamics.drag_breakdown
    if wing.tag=='main_wing':
        cl_w = wing_lifts
    else:
        cl_w = 0
        # start result
    qdyn = conditions.freestream.density * .5 * conditions.freestream.velocity**2
    totallift = wing_lifts * qdyn * geometry.areas.reference
    lstarsum = 0
    if wing.tag =='main_wing':
        for x in range(6):  
            wingseg = geometry.Segments[x]
            nextseg = geometry.Segments[x+1]
            midpt = (nextseg.percent_span_location - wingseg.percent_span_location)/2 + wingseg.percent_span_location
            srefseg = wingseg.areas.reference
            lstar = (1-(midpt)**2)*(nextseg.percent_span_location - wingseg.percent_span_location) # Assumes elliptical, lift per this length of span
            lstarsum += lstar # add it up to get factor to get dimensional lift
        #import pdb; pdb.set_trace()
        
        liftk = totallift / lstarsum / conditions.freestream.gravity[0][0]
        for y in range(6):
            wingseg = geometry.Segments[y]
            nextseg = geometry.Segments[y+1]
            midpt = (nextseg.percent_span_location - wingseg.percent_span_location)/2 + wingseg.percent_span_location
            lave = (1-(midpt)**2) * liftk
            cl_w = (1-(midpt)**2)*liftk/(wingseg.areas.reference *qdyn)


            t_c_w   = wingseg.thickness_to_chord
            sweep_w = wingseg.sweeps.quarter_chord

            #Calibrate to fit real data, make t/c hurt more, sweep help less
            t_c_w = t_c_w * 1.8
            sweep_w = sweep_w * .7
            
            # Currently uses vortex lattice model on all wings  
            cos_sweep = np.cos(sweep_w)

            # get effective Cl and sweep
            tc = t_c_w /(cos_sweep)
            cl = cl_w / (cos_sweep*cos_sweep)

            # compressibility drag based on regressed fits from AA241
            mcc_cos_ws = 0.922321524499352       \
                       - 1.153885166170620*tc    \
                       - 0.304541067183461*cl    \
                       + 0.332881324404729*tc*tc \
                       + 0.467317361111105*tc*cl \
                       + 0.087490431201549*cl*cl
                
            # crest-critical mach number, corrected for wing sweep
            mcc = mcc_cos_ws / cos_sweep
            
            # divergence mach number
            MDiv = mcc * ( 1.02 + 0.08*(1 - cos_sweep) )
            
            # divergence ratio
            mo_mc = mach/mcc
            
            # compressibility correlation, Shevell
            dcdc_cos3g = 0.0019*mo_mc**14.641
            
            # compressibility drag
            cd_c = dcdc_cos3g * cos_sweep*cos_sweep*cos_sweep
            cd_c = cd_c * .1 *wingseg.areas.reference / wing.areas.reference # Correction factor to get real world optimizations, and just the cou
            # increment
            total_compressibility_drag += cd_c
    else:
        conditions    = state.conditions
        configuration = settings    # unused
        
        wing = geometry
        if wing.tag == 'main_wing':
            wing_lifts = conditions.aerodynamics.lift_breakdown.compressible_wings # currently the total aircraft lift
        elif wing.vertical:
            wing_lifts = 0
        else:
            wing_lifts = 0.15 * conditions.aerodynamics.lift_breakdown.compressible_wings
            
        mach           = conditions.freestream.mach_number
        drag_breakdown = conditions.aerodynamics.drag_breakdown
        # start result
        total_compressibility_drag = 0.0
            
        # unpack wing
        t_c_w   = wing.thickness_to_chord
        sweep_w = wing.sweeps.quarter_chord

        #Calibrate to fit real data, make t/c hurt more, sweep help less
        t_c_w = t_c_w * 1.8
        sweep_w = sweep_w * .7
        
        # Currently uses vortex lattice model on all wings
        if wing.tag=='main_wing':
            cl_w = wing_lifts
        else:
            cl_w = 0
            
        cos_sweep = np.cos(sweep_w)

        # get effective Cl and sweep
        tc = t_c_w /(cos_sweep)
        cl = cl_w / (cos_sweep*cos_sweep)

        # compressibility drag based on regressed fits from AA241
        mcc_cos_ws = 0.922321524499352       \
                   - 1.153885166170620*tc    \
                   - 0.304541067183461*cl    \
                   + 0.332881324404729*tc*tc \
                   + 0.467317361111105*tc*cl \
                   + 0.087490431201549*cl*cl
            
        # crest-critical mach number, corrected for wing sweep
        mcc = mcc_cos_ws / cos_sweep
        
        # divergence mach number
        MDiv = mcc * ( 1.02 + 0.08*(1 - cos_sweep) )
        
        # divergence ratio
        mo_mc = mach/mcc
        
        # compressibility correlation, Shevell
        dcdc_cos3g = 0.0019*mo_mc**14.641
        
        # compressibility drag
        cd_c = dcdc_cos3g * cos_sweep*cos_sweep*cos_sweep
        cd_c = cd_c * .1 # Correction factor to get real world optimizations
        # increment
        #total_compressibility_drag += cd_c
        
    
    # dump data to conditions
    wing_results = Data(
        compressibility_drag      = total_compressibility_drag ,
        thickness_to_chord        = tc      , 
        wing_sweep                = sweep_w , 
        crest_critical            = mcc     ,
        divergence_mach           = MDiv    ,
    )
    drag_breakdown.compressible[wing.tag] = wing_results
    
    return total_compressibility_drag
