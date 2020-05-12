# Procedure.py
# 
# Created:  Mar 2016, M. Vegh
# Modified: Aug 2017, E. Botero

# ----------------------------------------------------------------------        
#   Imports
# ----------------------------------------------------------------------    
import Missions

import numpy as np
import math
import SUAVE
from SUAVE.Core import Units, Data
from SUAVE.Analyses.Process import Process
from SUAVE.Methods.Propulsion.turbofan_sizing import turbofan_sizing
from SUAVE.Methods.Geometry.Two_Dimensional.Cross_Section.Propulsion.compute_turbofan_geometry import compute_turbofan_geometry
#from SUAVE.Methods.Center_of_Gravity.compute_component_centers_of_gravity import compute_component_centers_of_gravity
#from SUAVE.Methods.Center_of_Gravity.compute_aircraft_center_of_gravity import compute_aircraft_center_of_gravity
from SUAVE.Methods.Aerodynamics.Fidelity_Zero.Lift.compute_max_lift_coeff import compute_max_lift_coeff
from SUAVE.Optimization.write_optimization_outputs import write_optimization_outputs
from SUAVE.Methods.Performance.estimate_take_off_field_length import estimate_take_off_field_length
from SUAVE.Methods.Utilities.soft_max import soft_max
import pdb
# ----------------------------------------------------------------------        
#   Setup
# ----------------------------------------------------------------------   

def setup():
    # ------------------------------------------------------------------
    #   Analysis Procedure
    # ------------------------------------------------------------------ 
    # size the base config
    procedure = Process()
    procedure.simple_sizing = simple_sizing
    

    # find the weights
    procedure.weights = weight
    # finalizes the data dependencies
    procedure.finalize = finalize
    
    # performance studies
    procedure.missions                   = Process()
    procedure.missions.design_mission    = design_mission

    # post process the results
    procedure.post_process = post_process
    #pdb.set_trace()
        
    return procedure

# ----------------------------------------------------------------------        
#   Target Range Function
# ----------------------------------------------------------------------    

def find_target_range(nexus,mission):
    
    segments = mission.segments
    cruise_altitude = mission.segments['climb_5'].altitude_end
    climb_1  = segments['climb_1']
    climb_3  = segments['climb_3']
    climb_5  = segments['climb_5']
    climb_s  = segments['step_climb']

    descent_1 = segments['descent_1']
    descent_2 = segments['descent_2']
    descent_3 = segments['descent_3']
    x_climb_1   = (climb_1.altitude_end-(1500*Units.ft))/np.tan(np.arcsin(climb_1.climb_rate/climb_1.air_speed))
    x_climb_3   = (climb_3.altitude_end-climb_1.altitude_end)/np.tan(np.arcsin(climb_3.climb_rate/climb_3.air_speed))
    x_climb_5   = (climb_5.altitude_end-climb_3.altitude_end)/np.tan(np.arcsin(climb_5.climb_rate/climb_5.air_speed))
    x_climb_s   = (climb_s.altitude_end - climb_5.altitude_end)/np.tan(np.arcsin(climb_s.climb_rate/climb_s.air_speed))
    x_descent_1 = (climb_5.altitude_end-descent_1.altitude_end)/np.tan(np.arcsin(descent_1.descent_rate/descent_1.air_speed))
    x_descent_2 = (descent_1.altitude_end-descent_2.altitude_end)/np.tan(np.arcsin(descent_2.descent_rate/descent_2.air_speed))
    x_descent_3 = (descent_2.altitude_end-descent_3.altitude_end)/np.tan(np.arcsin(descent_3.descent_rate/descent_3.air_speed))
    cruise_range = mission.design_range-(x_climb_1+x_climb_5+x_descent_1+x_descent_2+x_descent_3+x_climb_3 + x_climb_s)
    segments['cruise1'].distance = cruise_range / 2
    segments['cruise2'].distance = cruise_range / 2
    
    return nexus

# ----------------------------------------------------------------------        
#   Design Mission
# ----------------------------------------------------------------------    
def design_mission(nexus):
    mission = nexus.missions.base
    mission.design_range = 7000 *Units.nautical_miles
    find_target_range(nexus,mission)
    results = nexus.results
    results.base = mission.evaluate()
   # for config in nexus.vehicle_configurations:
   #     config.mass_properties.max_landing = config.mass_properties.max_zero_fuel + (results.base.segments['descent_3'].conditions.weights.total_mass[-1] - results.base.segments['reserve_descent_1'].conditions.weights.total_mass[-1])
    return nexus

# ----------------------------------------------------------------------        
#   Sizing
# ----------------------------------------------------------------------    

def simple_sizing(nexus):
    configs=nexus.vehicle_configurations
    base=configs.base
   
    #find conditions
    air_speed   = nexus.missions.base.segments['cruise1'].air_speed 
    altitude    = nexus.missions.base.cruise_altitude
    atmosphere  = SUAVE.Analyses.Atmospheric.US_Standard_1976()
    freestream  = atmosphere.compute_values(altitude)
    freestream0 = atmosphere.compute_values(6000.*Units.ft)  #cabin altitude
    
    diff_pressure         = np.max(freestream0.pressure-freestream.pressure,0)
    fuselage              = base.fuselages['fuselage']
    fuselage.differential_pressure = diff_pressure 
    
    #now size engine
    mach_number        = air_speed/freestream.speed_of_sound
    
    #now add to freestream data object
    freestream.velocity    = air_speed
    freestream.mach_number = mach_number
    freestream.gravity     = 9.81

    conditions             = SUAVE.Analyses.Mission.Segments.Conditions.Aerodynamics()   #assign conditions in form for propulsor sizing
    conditions.freestream  = freestream
    engine_arm_center      = configs.base.fuselages['fuselage'].width / 2 + 1.5 * configs.base.propulsors['turbofan'].nacelle_diameter # 1 diameter from fuselage
    for config in configs:
        config.wings.horizontal_stabilizer.areas.reference = (26.0/92.0)*config.wings.main_wing.areas.reference
        # vertical tail sizing is a force balance
        vertical_arm = (config.wings.vertical_stabilizer.origin[0] + .25 * config.wings.vertical_stabilizer.chords.mean_aerodynamic) - (config.wings.main_wing.origin[0] + config.wings.main_wing.chords.mean_aerodynamic * .25)
    
        config.wings.vertical_stabilizer.areas.reference   = (config.propulsors['turbofan'].sealevel_static_thrust * engine_arm_center) / (config.wings.vertical_stabilizer.q_cl_vertical * vertical_arm)
        config.wings.vertical_stabilizer.areas.reference   = soft_max(config.wings.vertical_stabilizer.areas.reference,(.07 * config.wings.main_wing.areas.reference * config.wings.main_wing.spans.projected) / vertical_arm)
        for wing in config.wings:
            
            wing = SUAVE.Methods.Geometry.Two_Dimensional.Planform.wing_planform(wing)
            wing.areas.exposed  = 0.8 * wing.areas.wetted
            wing.areas.affected = 0.6 * wing.areas.reference
            # Redo wing geometry based on new area
            wing.spans.projected         = np.sqrt(wing.aspect_ratio * wing.areas.reference)
            wing.chords.root             = wing.yehudi_factor * 2 * wing.areas.reference / wing.spans.projected / (1+wing.taper)   #A = .5 * [ ct + cr ] * s 
            wing.chords.tip              = wing.chords.root * wing.taper
            wing.chords.mean_aerodynamic = wing.chords.root - (2*(wing.chords.root-wing.chords.tip)*(.5*wing.chords.root+wing.chords.tip)/(3*(wing.chords.root+wing.chords.tip)))   #A-(2(A-B)(0.5A+B) / (3(A+B))) http://www.nasascale.org/p2/wp-content/uploads/mac-calculator.htm
            wing.fuel_volume             = (wing.thickness_to_chord * wing.chords.root * wing.chords.root*(.4) + wing.thickness_to_chord* wing.chords.tip * wing.chords.tip*.4) / 2 *wing.spans.projected* .9 * .7 # 70% span, 10% stringer and skin knockdown, average x-sec * span

        fuselage              = config.fuselages['fuselage']
        fuselage.differential_pressure = diff_pressure 
  
        turbofan_sizing(config.propulsors['turbofan'], .25, 0)
        compute_turbofan_geometry(config.propulsors['turbofan'], conditions)
        #ducted_fan_sizing(config.propulsors['turbofan'], .25, 0)
        #compute_ducted_fan_geometry(config.propulsors['turbofan'], conditions)
    # ------------------------------------------------------------------
    #   Landing Configuration
    # ------------------------------------------------------------------
    landing = nexus.vehicle_configurations.landing
    landing_conditions = Data()
    landing_conditions.freestream = Data()

    # landing weight
    #landing.mass_properties.landing = config.mass_properties.operating_empty + config.mass_properties.max_payload + (config.mass_properties.takeoff - (config.mass_properties.operating_empty + config.mass_properties.max_payload))*.1
    #nexus.vehicle_configurations.base.mass_properties.max_landing = landing.mass_properties.landing
    # Landing CL_max
    altitude   = 0 * Units.ft
    atmosphere = SUAVE.Analyses.Atmospheric.US_Standard_1976()
    freestream_landing = atmosphere.compute_values(0.)
    landing_conditions.freestream.velocity           = nexus.missions.base.segments['descent_3'].air_speed
    landing_conditions.freestream.density            = freestream_landing.density
    landing_conditions.freestream.dynamic_viscosity  = freestream_landing.dynamic_viscosity
    CL_max_landing,CDi = compute_max_lift_coeff(landing,landing_conditions)
    landing.maximum_lift_coefficient = CL_max_landing

    approach_denom = freestream_landing.density*config.wings.main_wing.areas.reference*CL_max_landing

    nexus.summary.approach_denom = approach_denom
    #Takeoff CL_max
    takeoff = nexus.vehicle_configurations.takeoff
    takeoff_conditions = Data()
    takeoff_conditions.freestream = Data()    
    altitude = nexus.missions.base.airport.altitude
    freestream_takeoff = atmosphere.compute_values(altitude)

    takeoff_conditions.freestream.velocity           = nexus.missions.base.segments.climb_1.air_speed
    takeoff_conditions.freestream.density            = freestream_takeoff.density
    takeoff_conditions.freestream.dynamic_viscosity  = freestream_takeoff.dynamic_viscosity 
    max_CL_takeoff, CDi = compute_max_lift_coeff(takeoff,takeoff_conditions)
    takeoff.maximum_lift_coefficient = max_CL_takeoff
    #Base config CL_max
    base = nexus.vehicle_configurations.base
    base_conditions = Data()
    base_conditions.freestream = takeoff_conditions.freestream   
    max_CL_base, CDi = compute_max_lift_coeff(base,base_conditions) 
    base.maximum_lift_coefficient = max_CL_base    

    nexus.missions.base.cruise_altitude  = configs.base.cruise_altitude
    nexus.missions.base.cruise_mach      = configs.base.cruise_mach
    #pdb.set_trace()
    nexus.missions = Missions.setup(nexus.analyses,nexus.vehicle_configurations) # Reset up missions with the new inputs



    return nexus

# ----------------------------------------------------------------------        
#   Weights
# ----------------------------------------------------------------------    

def weight(nexus):
    vehicle = nexus.vehicle_configurations.base
    results = nexus.results

    # weight analysis
    weights = nexus.analyses.base.weights.evaluate()
    weights = nexus.analyses.cruise.weights.evaluate()
    nexus.vehicle_configurations.base.mass_properties.breakdown = weights
    weights = nexus.analyses.landing.weights.evaluate()
    weights = nexus.analyses.takeoff.weights.evaluate()
  #  weights = nexus.analyses.short_field_takeoff.weights.evaluate()
    
    empty_weight     = vehicle.mass_properties.operating_empty
    passenger_weight = vehicle.passenger_weights.mass_properties.mass 
    bags             = vehicle.mass_properties.breakdown.bag  
    for config in nexus.vehicle_configurations:
        config.mass_properties.zero_fuel_center_of_gravity  = vehicle.mass_properties.zero_fuel_center_of_gravity
        config.fuel                                         = vehicle.fuel
        config.mass_properties.max_zero_fuel                = empty_weight + passenger_weight + bags + vehicle.mass_properties.cargo
    return nexus

def weight_cruise(nexus):
    vehicle=nexus.vehicle_configurations.base

    # weight analysis
    weights = nexus.analyses.base.weights.evaluate()
    #weights = nexus.analyses.cruise.weights.evaluate()
    vehicle.mass_properties.breakdown = weights
    #weights = nexus.analyses.landing.weights.evaluate()
    #weights = nexus.analyses.takeoff.weights.evaluate()
    #weights = nexus.analyses.short_field_takeoff.weights.evaluate()
    
    empty_weight     = vehicle.mass_properties.operating_empty
    passenger_weight = vehicle.passenger_weights.mass_properties.mass 
    bags = vehicle.mass_properties.breakdown.bag  
    vehicle.mass_properties.max_zero_fuel                = empty_weight + passenger_weight + bags + vehicle.mass_properties.cargo    


       # config.mass_properties.max_landing   = config.mass_properties.max_zero_fuel + (nexus.results.base.segments['descent_3'].conditions.weights.total_mass[-1] - nexus.results.segments['reserve_descent_1'].conditions.weights.total_mass[-1])
    

    return nexus



# ----------------------------------------------------------------------
#   Finalizing Function
# ----------------------------------------------------------------------    

def finalize(nexus):
    
    nexus.analyses.finalize()   
    
    return nexus         

# ----------------------------------------------------------------------
#   Post Process Results to give back to the optimizer
# ----------------------------------------------------------------------   

def post_process(nexus):
    
    # Unpack data
    vehicle                           = nexus.vehicle_configurations.base
    results                           = nexus.results
    summary                           = nexus.summary
    missions                          = nexus.missions  
    nexus.total_number_of_iterations +=1
    # Static stability calculations
    CMA = -10.
    for segment in results.base.segments.values():
        max_CMA = np.max(segment.conditions.stability.static.cm_alpha[:,0])
        if max_CMA > CMA:
            CMA = max_CMA
            
    summary.static_stability = CMA
    
    #throttle in design mission
    max_throttle = 0
    for segment in results.base.segments.values():
        max_segment_throttle = np.max(segment.conditions.propulsion.throttle[:,0])
        if max_segment_throttle > max_throttle:
            max_throttle = max_segment_throttle
            
    summary.max_throttle = max_throttle
    
    #Set Requirements here
    second_seg_grad_req     = .024
    tofl_req                = 7900 * Units.ft
    fuel_margin_req         = .1
    max_throttle_req        = .95
    approach_speed_req      = 150 * Units.knots


    passenger_weight         = vehicle.passenger_weights.mass_properties.mass 
    bags                     = vehicle.mass_properties.breakdown.bag  
    payload                  = passenger_weight + bags + vehicle.mass_properties.cargo    

    # Fuel margin and base fuel calculations
    operating_empty          = vehicle.mass_properties.operating_empty
    design_takeoff_weight    = vehicle.mass_properties.takeoff
    max_takeoff_weight       = nexus.vehicle_configurations.takeoff.mass_properties.max_takeoff
    zero_fuel_weight         = payload + operating_empty
  #  reserve_fuel             = (results.base.segments['descent_3'].conditions.weights.total_mass[-1] - results.base.segments['reserve_descent_1'].conditions.weights.total_mass[-1])

    #summary.max_zero_fuel_margin    = (design_landing_weight - zero_fuel_weight)/zero_fuel_weight   # This just shows reserve fuel fraction
    summary.base_mission_fuelburn   = design_takeoff_weight - results.base.segments['descent_3'].conditions.weights.total_mass[-1]
    reserve_fuel = .05 * summary.base_mission_fuelburn
    design_landing_weight    = zero_fuel_weight + reserve_fuel

   # print(summary.max_zero_fuel_margin)
    #print(results.base.segments['descent_3'].conditions.weights.total_mass[-1] + reserve_fuel) # Guessed landing weight
    #print(design_landing_weight)                                                               # Actual landing weight
    if ((2*design_landing_weight*9.81)/(summary.approach_denom) > 0):
        summary.approach_Speed          = math.sqrt((2 * design_landing_weight * 9.81)/(summary.approach_denom))
    else:    
        summary.approach_Speed          = math.sqrt((-10 * 2 * design_landing_weight*9.81)/(summary.approach_denom))
    summary.takeoff_field_length,summary.second_seg_grad = estimate_take_off_field_length(nexus.vehicle_configurations.takeoff,nexus.analyses,nexus.missions.base.airport,1)
 
    actual_takeoff_weight          = operating_empty  +  payload   +   summary.base_mission_fuelburn + reserve_fuel
    summary.takeoff_diff           = (design_takeoff_weight - actual_takeoff_weight) / design_takeoff_weight
   # print(design_takeoff_weight)
   # print(actual_takeoff_weight)
    summary.landing_diff           = (results.base.segments['descent_3'].conditions.weights.total_mass[-1] - design_landing_weight) / design_landing_weight
   
  #  summary.mzfw_diff              = (results.base.segments['reserve_descent_1'].conditions.weights.total_mass[-1] - zero_fuel_weight) / zero_fuel_weight

    summary.takeoff_weight         = actual_takeoff_weight
    summary.operating_empty        = operating_empty
    summary.thrust                 = vehicle.propulsors['turbofan'].sealevel_static_thrust * 2
    summary.fuel_margin            = (vehicle.wings.main_wing.fuel_volume*.804 * 1000 - summary.base_mission_fuelburn) / (vehicle.wings.main_wing.fuel_volume*.804 * 1000) 
    summary.nacelle_d              = vehicle.propulsors['turbofan'].nacelle_diameter / Units.inches  
    summary.engine_length          = vehicle.propulsors['turbofan'].engine_length / Units.inches
    
   # import pdb; pdb.set_trace()
    #when you run want to output results to a file
    #filename = 'results.txt'
    #write_optimization_outputs(nexus, filename)
    #print(summary.takeoff_field_length)
    return nexus    
