## @ingroup Methods-Weights-Correlations-BWB
# empty.py
# 
# Created:  Apr 2017, M. Clarke 
# Modified: Jul 2017, M. Clarke

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
import SUAVE
from SUAVE.Core     import Units, Data
from .cabin          import cabin
from .aft_centerbody import aft_centerbody
from .systems        import systems
from SUAVE.Methods.Weights.Correlations.Tube_Wing   import tail_vertical
from SUAVE.Methods.Weights.Correlations.Common import wing_main as wing_main
from SUAVE.Methods.Weights.Correlations.Common import landing_gear as landing_gear
from SUAVE.Methods.Weights.Correlations.Common import payload as payload
from SUAVE.Methods.Weights.Correlations import Propulsion as Propulsion
import warnings

# ----------------------------------------------------------------------
#  Empty
# ----------------------------------------------------------------------

## @ingroup Methods-Weights-Correlations-BWB
def empty(vehicle):
    """ This is for a BWB aircraft configuration. 
    
    Assumptions:
         calculated aircraft weight from correlations created per component of historical aircraft
      
    Source: 
        N/A
         
    Inputs:
        engine - a data dictionary with the fields:                    
            thrust_sls - sea level static thrust of a single engine                                        [Newtons]

        wing - a data dictionary with the fields:
            gross_area - wing gross area                                                                   [meters**2]
            span - span of the wing                                                                        [meters]
            taper - taper ratio of the wing                                                                [dimensionless]
            t_c - thickness-to-chord ratio of the wing                                                     [dimensionless]
            sweep - sweep angle of the wing                                                                [radians]
            mac - mean aerodynamic chord of the wing                                                       [meters]
            r_c - wing root chord                                                                          [meters]

        aircraft - a data dictionary with the fields:                    
            Nult - ultimate load of the aircraft                                                           [dimensionless]
            Nlim - limit load factor at zero fuel weight of the aircraft                                   [dimensionless]
            TOW - maximum takeoff weight of the aircraft                                                   [kilograms]
            zfw - maximum zero fuel weight of the aircraft                                                 [kilograms]
            num_eng - number of engines on the aircraft                                                    [dimensionless]
            num_pax - number of passengers on the aircraft                                                 [dimensionless]
            wt_cargo - weight of the bulk cargo being carried on the aircraft                              [kilograms]
            num_seats - number of seats installed on the aircraft                                          [dimensionless]
            ctrl - specifies if the control system is "fully powered", "partially powered", or not powered [dimensionless]
            ac - determines type of instruments, electronics, and operating items based on types: 
                "short-range", "medium-range", "long-range", "business", "cargo", "commuter", "sst"        [dimensionless]

         fuselage - a data dictionary with the fields:
            area - fuselage wetted area                                                                    [meters**2]
            diff_p - Maximum fuselage pressure differential                                                [Pascal]
            width - width of the fuselage                                                                  [meters]
            height - height of the fuselage                                                                [meters]
            length - length of the fuselage                                                                [meters]   
        
    Outputs:
        output - a data dictionary with fields:
            wt_payload - weight of the passengers plus baggage and paid cargo                              [kilograms]
            wt_pax - weight of all the passengers                                                          [kilogram]
            wt_bag - weight of all the baggage                                                             [kilogram]
            wt_fuel - weight of the fuel carried                                                           [kilogram]
            wt_empty - operating empty weight of the aircraft                                              [kilograms]
    
    Properties Used:
    N/A
    """    

    # Unpack inputs
    Nult       = vehicle.envelope.ultimate_load
    Nlim       = vehicle.envelope.limit_load
    TOW        = vehicle.mass_properties.max_takeoff
    wt_zf      = vehicle.mass_properties.max_zero_fuel
    wt_cargo   = vehicle.mass_properties.cargo
    num_pax    = vehicle.passengers
    ctrl_type  = vehicle.systems.control
    ac_type    = vehicle.systems.accessories
     
    num_seats                = vehicle.passengers
    bwb_aft_centerbody_area  = vehicle.fuselages['fuselage_bwb'].aft_centerbody_area
    bwb_aft_centerbody_taper = vehicle.fuselages['fuselage_bwb'].aft_centerbody_taper
    bwb_cabin_area           = vehicle.fuselages['fuselage_bwb'].cabin_area_available
    
  
    
    propulsor_name = list(vehicle.propulsors.keys())[0] #obtain the key for the propulsor for assignment purposes
    
    propulsors     = vehicle.propulsors[propulsor_name]
    num_eng        = propulsors.number_of_engines
    if propulsor_name=='turbofan' or propulsor_name=='Turbofan':
        # thrust_sls should be sea level static thrust. Using design thrust results in wrong propulsor 
        # weight estimation. Engine sizing should return this value.
        # for now, using thrust_sls = design_thrust / 0.20, just for optimization evaluations
        thrust_sls                       = propulsors.sealevel_static_thrust
        wt_engine_jet                    = Propulsion.engine_jet(thrust_sls)
        wt_propulsion                    = Propulsion.integrated_propulsion(propulsors, 1.6)
        fuel_weight        = vehicle.wings['main_wing'].fuel_volume * .804 * 1000 / Units.lbs
        max_mach           = vehicle.cruise_mach*1.1
        num_eng            = propulsors.thrust.inputs.number_of_engines
        fuel_system_weight = 1.07 * (fuel_weight**.58) * (num_eng**.43) * (max_mach**.34) * Units.lb
       # engine_start_weight = 11 * (num_eng) * (max_mach**.32) * (propulsors.nacelle_diameter / Units.inches**1.6) ## This isn't working
        propulsors.mass_properties.mass  = wt_propulsion + fuel_system_weight
    elif propulsor_name == 'openrotor' or propulsor_name == 'openrotoraft':
        #wt_propulsion      = Propulsion.integrated_propulsion_open_rotor(propulsors,1.6)
        thrust_sls                       = propulsors.sealevel_static_thrust

        wt_engine_jet                    = Propulsion.engine_jet(thrust_sls)
        wt_propulsion                    = Propulsion.integrated_propulsion(propulsors, 1.6)
        fuel_weight        = vehicle.wings['main_wing'].fuel_volume * .804 * 1000 / Units.lbs
        max_mach           = vehicle.cruise_mach*1.1
        num_eng            = propulsors.thrust.inputs.number_of_engines
        fuel_system_weight = 1.07 * (fuel_weight**.58) * (num_eng**.43) * (max_mach**.34) * Units.lb
        prop_k_factor      = 0.8
        propulsors.mass_properties.mass  = (wt_propulsion + fuel_system_weight) * prop_k_factor
    else: #propulsor used is not a turbo_fan; assume mass_properties defined outside model
        wt_propulsion                   = propulsors.mass_properties.mass

        if wt_propulsion==0:
            warnings.warn("Propulsion mass= 0 ;e there is no Engine Weight being added to the Configuration", stacklevel=1)      
    
    S_gross_w  = vehicle.reference_area

    if 'main_wing' not in vehicle.wings:
        wt_wing  = 0.0
        wing_c_r = 0.0
        warnings.warn("There is no Wing Weight being added to the Configuration", stacklevel=1)
        
    else:
        #BWB Wing here is just the outboard wing, the center section is included in fuselage, so start at section 5
        b          = (1- vehicle.wings['main_wing'].Segments[4].percent_span_location) * vehicle.wings['main_wing'].spans.projected
        lambda_w   = vehicle.wings['main_wing'].Segments[6].root_chord_percent / vehicle.wings['main_wing'].Segments[4].root_chord_percent
        t_c_w      = vehicle.wings['main_wing'].Segments[4].thickness_to_chord
        sweep_w    = vehicle.wings['main_wing'].Segments[4].sweeps.quarter_chord
        mac_w      =  (2/3 * vehicle.wings['main_wing'].Segments[4].root_chord_percent *((1+lambda_w +lambda_w **2)/(1+lambda_w )))* vehicle.wings['main_wing'].chords.root
        wing_c_r   = vehicle.wings['main_wing'].Segments[4].root_chord_percent * vehicle.wings['main_wing'].chords.root
        S_h        = vehicle.wings['main_wing'].areas.reference*0.01 # control surface area on bwb
        S_bwb_ref  = 0 
        S_bwb_ref  +=  ((vehicle.wings['main_wing'].Segments[5].percent_span_location - vehicle.wings['main_wing'].Segments[4].percent_span_location) * vehicle.wings['main_wing'].spans.projected) * (((vehicle.wings['main_wing'].Segments[5].root_chord_percent + vehicle.wings['main_wing'].Segments[4].root_chord_percent)/2) * vehicle.wings['main_wing'].chords.root )
        S_bwb_ref  +=  ((vehicle.wings['main_wing'].Segments[6].percent_span_location - vehicle.wings['main_wing'].Segments[5].percent_span_location) * vehicle.wings['main_wing'].spans.projected) * (((vehicle.wings['main_wing'].Segments[6].root_chord_percent + vehicle.wings['main_wing'].Segments[5].root_chord_percent)/2) * vehicle.wings['main_wing'].chords.root )
        # Add sref fracation and TOW fraction
        wt_wing    = wing_main.wing_main(S_bwb_ref,b,lambda_w,t_c_w,sweep_w,Nult,TOW * S_bwb_ref / vehicle.reference_area,wt_zf)
        vehicle.wings['main_wing'].mass_properties.mass = wt_wing        

    # Calculating Empty Weight of Aircraft
    wt_landing_gear    = landing_gear.landing_gear(TOW)
    wt_cabin           = cabin(bwb_cabin_area, TOW)
    wt_aft_centerbody  = aft_centerbody(num_eng, bwb_aft_centerbody_area, bwb_aft_centerbody_taper, TOW)
    output_2           = systems(num_seats, ctrl_type, S_h , S_gross_w, ac_type)

    # Calculate the equipment empty weight of the aircraft
    vehicle.fuselages['fuselage_bwb'].mass_properties.mass = wt_cabin 
    #Do the vertical stabilizers, assume they are the same
    S_v          = vehicle.wings['vertical_stabilizer_r'].areas.reference
    b_v          = vehicle.wings['vertical_stabilizer_r'].spans.projected
    t_c_v        = vehicle.wings['vertical_stabilizer_r'].thickness_to_chord
    sweep_v      = vehicle.wings['vertical_stabilizer_r'].sweeps.quarter_chord
    t_tail       = vehicle.wings['vertical_stabilizer_r'].t_tail  
    output_3     = tail_vertical(S_v,Nult,b_v,TOW,t_c_v,sweep_v,S_gross_w,t_tail)
    wt_vtail_tot = output_3.wt_tail_vertical + output_3.wt_rudder
    #wt_vtail_tot = wt_vtail_tot*(1.-wt_factors.empennage)
    vehicle.wings['vertical_stabilizer_r'].mass_properties.mass = wt_vtail_tot
    vehicle.wings['vertical_stabilizer_l'].mass_properties.mass = wt_vtail_tot
    wt_empty           = (wt_wing +wt_vtail_tot*2 + wt_cabin + wt_aft_centerbody + wt_landing_gear + wt_propulsion + output_2.wt_systems)


    
    # packup outputs
    output                                      = payload.payload(TOW, wt_empty, num_pax,wt_cargo)
    output.wing                                 = wt_wing
    output.fuselage                             = wt_cabin + wt_aft_centerbody
    output.propulsion                           = wt_propulsion
    output.vertical_tail                        = output_3.wt_tail_vertical * 2
    output.landing_gear                         = wt_landing_gear
    output.systems                              = output_2.wt_systems       
    output.systems_breakdown                    = Data()
    output.systems_breakdown.control_systems    = output_2.wt_flt_ctrl 
    output.systems_breakdown.apu                = output_2.wt_apu         
    output.systems_breakdown.hydraulics         = output_2.wt_hyd_pnu     
    output.systems_breakdown.instruments        = output_2.wt_instruments 
    output.systems_breakdown.avionics           = output_2.wt_avionics    
    output.systems_breakdown.optionals          = output_2.wt_opitems     
    output.systems_breakdown.electrical         = output_2.wt_elec        
    output.systems_breakdown.air_conditioner    = output_2.wt_ac          
    output.systems_breakdown.furnish            = output_2.wt_furnish    
    #define weights components

    try: 
        landing_gear_component=vehicle.landing_gear #landing gear previously defined
    except AttributeError: # landing gear not defined
        landing_gear_component=SUAVE.Components.Landing_Gear.Landing_Gear()
        vehicle.landing_gear=landing_gear_component
    
    control_systems                             = SUAVE.Components.Physical_Component()
    electrical_systems                          = SUAVE.Components.Physical_Component()
    passengers                                  = SUAVE.Components.Physical_Component()
    furnishings                                 = SUAVE.Components.Physical_Component()
    air_conditioner                             = SUAVE.Components.Physical_Component()
    fuel                                        = SUAVE.Components.Physical_Component()
    apu                                         = SUAVE.Components.Physical_Component()
    hydraulics                                  = SUAVE.Components.Physical_Component()
    optionals                                   = SUAVE.Components.Physical_Component()
    avionics                                    = SUAVE.Components.Energy.Peripherals.Avionics()
    
    
    #assign output weights to objects
    landing_gear_component.mass_properties.mass = output.landing_gear
    control_systems.mass_properties.mass        = output.systems_breakdown.control_systems
    electrical_systems.mass_properties.mass     = output.systems_breakdown.electrical
    passengers.mass_properties.mass             = output.pax + output.bag
    furnishings.mass_properties.mass            = output.systems_breakdown.furnish
    avionics.mass_properties.mass               = output.systems_breakdown.avionics \
        + output.systems_breakdown.instruments  
    air_conditioner.mass_properties.mass        = output.systems_breakdown.air_conditioner
    fuel.mass_properties.mass                   = output.fuel
    apu.mass_properties.mass                    = output.systems_breakdown.apu
    hydraulics.mass_properties.mass             = output.systems_breakdown.hydraulics
    optionals.mass_properties.mass              = output.systems_breakdown.optionals

    
    #assign components to vehicle
    vehicle.control_systems                     = control_systems
    vehicle.electrical_systems                  = electrical_systems
    vehicle.avionics                            = avionics
    vehicle.furnishings                         = furnishings
    vehicle.passenger_weights                   = passengers 
    vehicle.air_conditioner                     = air_conditioner
    vehicle.fuel                                = fuel
    vehicle.apu                                 = apu
    vehicle.hydraulics                          = hydraulics
    vehicle.optionals                           = optionals
    vehicle.landing_gear                        = landing_gear_component

    return output