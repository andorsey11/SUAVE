# Vehicles.py
# 
# Created:  Feb. 2016, M. Vegh
# Modified: Aug. 2017, E. Botero

# ----------------------------------------------------------------------        
#   Imports
# ----------------------------------------------------------------------    

import SUAVE
import numpy
from SUAVE.Core import Units
from SUAVE.Methods.Propulsion.turbofan_sizing import turbofan_sizing
from SUAVE.Methods.Propulsion.ducted_fan_sizing import ducted_fan_sizing 

# ----------------------------------------------------------------------
#   Define the Vehicle
# ----------------------------------------------------------------------

def setup():
    
    base_vehicle = base_setup()
    configs = configs_setup(base_vehicle)
    
    return configs

def base_setup():
    
    # ------------------------------------------------------------------
    #   Initialize the Vehicle
    # ------------------------------------------------------------------

    vehicle = SUAVE.Vehicle()
    vehicle.tag = 'BWB_Test'    
    
    # ------------------------------------------------------------------
    #   Vehicle-level Properties
    # ------------------------------------------------------------------    

    # mass properties
    vehicle.mass_properties.max_takeoff               = 87000 * Units.kilogram 
    vehicle.mass_properties.takeoff                   = 87000 * Units.kilogram   
    vehicle.mass_properties.operating_empty           = 52746.4 * Units.kilogram 
    vehicle.mass_properties.max_zero_fuel             = 62732.0 * Units.kilogram 
    vehicle.mass_properties.cargo                     = 10000.  * Units.kilogram
    vehicle.mass_properties.econ_takeoff              = 75000   * Units.kilogram  

    # envelope properties
    vehicle.envelope.ultimate_load = 2.5
    vehicle.envelope.limit_load    = 1.5

    # basic parameters
    vehicle.reference_area         = 180 * Units['meters**2']  
    vehicle.passengers             = 170
    vehicle.systems.control        = "fully powered" 
    vehicle.systems.accessories    = "medium range"


    vehicle.cruise_altitude    = 31200 * Units.ft
    vehicle.cruise_mach        = .79
    vehicle.cruise_step        = 2000 / 3.28 * Units.m
    # ------------------------------------------------------------------        
    #  Landing Gear
    # ------------------------------------------------------------------        
    # used for noise calculations
    landing_gear = SUAVE.Components.Landing_Gear.Landing_Gear()
    landing_gear.tag = "main_landing_gear"
    
    landing_gear.main_tire_diameter = 1.12000 * Units.m
    landing_gear.nose_tire_diameter = 0.6858 * Units.m
    landing_gear.main_strut_length  = 1.8 * Units.m
    landing_gear.nose_strut_length  = 1.3 * Units.m
    landing_gear.main_units  = 2    #number of main landing gear units
    landing_gear.nose_units  = 1    #number of nose landing gear
    landing_gear.main_wheels = 2    #number of wheels on the main landing gear
    landing_gear.nose_wheels = 2    #number of wheels on the nose landing gear      
    vehicle.landing_gear = landing_gear

    # ------------------------------------------------------------------        
    #   Main Wing
    # ------------------------------------------------------------------        
    
    wing = SUAVE.Components.Wings.Main_Wing()
    wing.tag = 'main_wing'
    wing.areas.reference         = 180 * Units['meters**2']  
    wing.aspect_ratio            = 6
    wing.sweeps.quarter_chord    = 0 * Units.deg
    wing.sweeps.leading_edge     = 45 * Units.deg
    wing.sweeps.trailing_edge    = 45 * Units.deg
    wing.thickness_to_chord      = 0.15
    wing.taper                   = 0.025
    wing.span_efficiency         = 1.01
    wing.yehudi_factor           = 1.5               # Factor to capture extra root chord due to yehudi, 1.2 good for low wing, close to 1 for high wing
    wing.spans.projected         = 118 / 3.28
    wing.chords.root             = 20   #A = .5 * [ ct + cr ] * s. This doesn't work for a non-trap wing
    wing.chords.tip              = wing.chords.root * wing.taper
    wing.chords.mean_aerodynamic = wing.chords.root - (2*(wing.chords.root-wing.chords.tip)*(.5*wing.chords.root+wing.chords.tip)/(3*(wing.chords.root+wing.chords.tip)))   #A-(2(A-B)(0.5A+B) / (3(A+B))) http://www.nasascale.org/p2/wp-content/uploads/mac-calculator.htm
    wing.twists.root             = 0 * Units.degrees
    wing.twists.tip              = 0.0 * Units.degrees
    wing.origin                  = [[0,0,0]] # meters
    wing.vertical                = False
    wing.symmetric               = True
    wing.high_lift               = True
    wing.dynamic_pressure_ratio  = 1.0
    wing.aft_centerbody_area     = 0 
    wing.cabin_area_available    = 0
    wing.cabin_cutoff            = .35
    wing.fuel_volume             = (wing.thickness_to_chord * wing.chords.root * wing.chords.root*(.4) + wing.thickness_to_chord* wing.chords.tip * wing.chords.tip*.4) / 2 *wing.spans.projected* .9 * .7 # 70% span, 10% stringer and skin knockdown, average x-sec * span

    segment = SUAVE.Components.Wings.Segment()

    segment.tag                   = 'section_1'
    segment.percent_span_location = 0.0
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 1.
    segment.dihedral_outboard     = 0. * Units.degrees
    segment.sweeps.quarter_chord  = 60.0 * Units.degrees
    segment.thickness_to_chord    = 0.165
    # segment.vsp_mesh              = Data()
    # segment.vsp_mesh.inner_radius    = 4.
    # segment.vsp_mesh.outer_radius    = 4.
    # segment.vsp_mesh.inner_length    = .14
    # segment.vsp_mesh.outer_length    = .14    
    wing.Segments.append(segment)    
    
    segment = SUAVE.Components.Wings.Segment()
    segment.tag                      = 'section_2'
    segment.percent_span_location    = 0.05
    segment.twist                    = 0. * Units.deg
    segment.root_chord_percent       = 0.921
    segment.dihedral_outboard        = 0.   * Units.degrees
    segment.sweeps.quarter_chord     = 50 * Units.degrees
    segment.thickness_to_chord       = 0.167
    # segment.vsp_mesh                 = Data()
    # segment.vsp_mesh.inner_radius    = 4.
    # segment.vsp_mesh.outer_radius    = 4.
    # segment.vsp_mesh.inner_length    = .14
    # segment.vsp_mesh.outer_length    = .14     
    wing.Segments.append(segment)   

    segment = SUAVE.Components.Wings.Segment()
    segment.tag                      = 'section_3'
    segment.percent_span_location    = 0.15
    segment.twist                    = 0. * Units.deg
    segment.root_chord_percent       = 0.90
    segment.dihedral_outboard        = 1.85 * Units.degrees
    segment.sweeps.quarter_chord     = 45 * Units.degrees  
    segment.thickness_to_chord       = 0.171
    # segment.vsp_mesh                 = Data()
    # segment.vsp_mesh.inner_radius    = 4.
    # segment.vsp_mesh.outer_radius    = 4.
    # segment.vsp_mesh.inner_length    = .14
    # segment.vsp_mesh.outer_length    = .14     
    wing.Segments.append(segment)   
    
    segment = SUAVE.Components.Wings.Segment()
    segment.tag                      = 'section_4'
    segment.percent_span_location    = 0.2
    segment.twist                    = 0. * Units.deg
    segment.root_chord_percent       = 0.624
    segment.dihedral_outboard        = 1.85 * Units.degrees
    segment.sweeps.quarter_chord     = 35* Units.degrees    
    segment.thickness_to_chord       = 0.175
    # segment.vsp_mesh                 = Data()
    # segment.vsp_mesh.inner_radius    = 4.
    # segment.vsp_mesh.outer_radius    = 2.8
    # segment.vsp_mesh.inner_length    = .14
    # segment.vsp_mesh.outer_length    = .14     
    wing.Segments.append(segment)       
    
    #This is defined as the extent of the center section, and the span location is a design variable
    segment = SUAVE.Components.Wings.Segment()
    segment.tag                   = 'section_5'
    segment.percent_span_location = wing.cabin_cutoff
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 0.5
    segment.dihedral_outboard     = 1.85  * Units.degrees
    segment.sweeps.quarter_chord  = 35* Units.degrees
    segment.thickness_to_chord    = 0.118
    wing.Segments.append(segment)       
    
    segment = SUAVE.Components.Wings.Segment()
    segment.tag                   = 'section_6'
    segment.percent_span_location = 0.5
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 0.4
    segment.dihedral_outboard     = 1.85 * Units.degrees
    segment.sweeps.quarter_chord  = 34.3 * Units.degrees
    segment.thickness_to_chord    = 0.10
    wing.Segments.append(segment)     
    
    segment = SUAVE.Components.Wings.Segment()
    segment.tag                   = 'section_7'
    segment.percent_span_location = 0.97
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 0.086
    segment.dihedral_outboard     = 1.85 * Units.degrees
    segment.sweeps.quarter_chord  = 55. * Units.degrees
    segment.thickness_to_chord    = 0.10
    wing.Segments.append(segment)      

    segment = SUAVE.Components.Wings.Segment()
    segment.tag                   = 'tip'
    segment.percent_span_location = 1
    segment.twist                 = 0. * Units.deg
    segment.root_chord_percent    = 0.0241
    segment.dihedral_outboard     = 0. * Units.degrees
    segment.sweeps.quarter_chord  = 0. * Units.degrees
    segment.thickness_to_chord    = 0.10
    wing.Segments.append(segment)  

    # add to vehicle
    vehicle.append_component(wing)

    # ------------------------------------------------------------------        
    #  Horizontal Stabilizer
    # ------------------------------------------------------------------        
    # wing = SUAVE.Components.Wings.Wing()
    # wing.tag = 'horizontal_stabilizer'
    
    # wing.aspect_ratio            = 6.16     
    # wing.sweeps.quarter_chord    = 40 * Units.deg
    # wing.thickness_to_chord      = 0.08
    # wing.taper                   = 0.2
    # wing.span_efficiency         = 0.9
    # wing.spans.projected         = 14.2 * Units.meter
    # wing.chords.root             = 4.7  * Units.meter
    # wing.chords.tip              = .955 * Units.meter
    # wing.chords.mean_aerodynamic = 8.0  * Units.meter
    # wing.areas.reference         = 32.488   * Units['meters**2']  
    # wing.twists.root             = 3.0 * Units.degrees
    # wing.twists.tip              = 3.0 * Units.degrees  
    # wing.origin                  = [32.83,0,1.14] # meters
    # wing.vertical                = False 
    # wing.symmetric               = True
    # wing.dynamic_pressure_ratio  = 0.9  
    # wing.yehudi_factor           = 1.2  
    # # add to vehicle
    # vehicle.append_component(wing)
    
    # ------------------------------------------------------------------
    #   Vertical Stabilizer
    # ------------------------------------------------------------------
    
    wing = SUAVE.Components.Wings.Wing()
    wing.tag = 'vertical_stabilizer_r'    

    wing.aspect_ratio            = 1.91
    wing.sweeps.quarter_chord    = 25. * Units.deg
    wing.thickness_to_chord      = 0.08
    wing.taper                   = 0.25
    wing.span_efficiency         = 0.9
    wing.spans.projected         = 2 * Units.meter
    wing.chords.root             = 2  * Units.meter
    wing.chords.tip              = 2  * Units.meter
    wing.chords.mean_aerodynamic = 2   * Units.meter
    wing.areas.reference         = 20 * Units['meters**2']  
    wing.twists.root             = 0.0 * Units.degrees
    wing.twists.tip              = 0.0 * Units.degrees  
    wing.origin                  = [28.79,0,1.54] # meters
    wing.vertical                = True 
    wing.symmetric               = False
    wing.t_tail                  = False
    wing.dynamic_pressure_ratio  = 1.0
    wing.yehudi_factor           = 1.2
    wing.q_cl_vertical           = 2000 # Pascals      
    # add to vehicle
    vehicle.append_component(wing)

    wing = SUAVE.Components.Wings.Wing()
    wing.tag = 'vertical_stabilizer_l'    

    wing.aspect_ratio            = 1.91
    wing.sweeps.quarter_chord    = 25. * Units.deg
    wing.thickness_to_chord      = 0.08
    wing.taper                   = 0.25
    wing.span_efficiency         = 0.9
    wing.spans.projected         = 2 * Units.meter
    wing.chords.root             = 2  * Units.meter
    wing.chords.tip              = 2  * Units.meter
    wing.chords.mean_aerodynamic = 2   * Units.meter
    wing.areas.reference         = 20 * Units['meters**2']  
    wing.twists.root             = 0.0 * Units.degrees
    wing.twists.tip              = 0.0 * Units.degrees  
    wing.origin                  = [28.79,0,1.54] # meters
    wing.vertical                = True 
    wing.symmetric               = False
    wing.t_tail                  = False
    wing.dynamic_pressure_ratio  = 1.0
    wing.yehudi_factor           = 1.2
    wing.q_cl_vertical           = 2000 # Pascals      
    # add to vehicle
    vehicle.append_component(wing)

    # ------------------------------------------------------------------
    #  Fuselage
    # ------------------------------------------------------------------
    
    fuselage = SUAVE.Components.Fuselages.Fuselage()
    fuselage.tag = 'fuselage_bwb'
    
    fuselage.number_coach_seats    = vehicle.passengers
    fuselage.seats_abreast         = 6
    fuselage.seat_pitch            = 1     * Units.meter
    fuselage.fineness.nose         = 1.6
    fuselage.fineness.tail         = 2.
    fuselage.lengths.nose          = 6.4   * Units.meter
    fuselage.lengths.tail          = 8.0   * Units.meter
    fuselage.lengths.cabin         = 28.85 * Units.meter
    fuselage.lengths.total         = 38.02 * Units.meter
    fuselage.lengths.fore_space    = 6.    * Units.meter
    fuselage.lengths.aft_space     = 5.    * Units.meter
    fuselage.width                 = 0  * Units.meter
    fuselage.heights.maximum       = 3.74  * Units.meter
    fuselage.effective_diameter    = 3.74     * Units.meter
    fuselage.areas.side_projected  = 142.1948 * Units['meters**2'] 
    fuselage.areas.wetted          = 2*3.14*fuselage.width/2*(fuselage.lengths.cabin+(fuselage.lengths.total - fuselage.lengths.cabin)*.5)  * Units['meters**2'] 
    fuselage.areas.front_projected = 12.57    * Units['meters**2'] 
    fuselage.differential_pressure = 5.0e4 * Units.pascal # Maximum differential pressure
    #This is a required floor area, and is a constraint in the optimization
    fuselage.cabin_area_required   = ((34 * 18 * 1.2) + (24/6 * 34))/144 * vehicle.passengers * Units['feet**2'] 
    fuselage.cabin_area_available  = 0
    fuselage.aft_centerbody_area   += 0.3*((vehicle.wings['main_wing'].Segments[1].percent_span_location - vehicle.wings['main_wing'].Segments[0].percent_span_location) * vehicle.wings['main_wing'].spans.projected) * ((vehicle.wings['main_wing'].Segments[1].root_chord_percent + vehicle.wings['main_wing'].Segments[0].root_chord_percent)/2 *vehicle.wings['main_wing'].chords.root)
    fuselage.aft_centerbody_area   += 0.3*((vehicle.wings['main_wing'].Segments[2].percent_span_location - vehicle.wings['main_wing'].Segments[1].percent_span_location) * vehicle.wings['main_wing'].spans.projected) * ((vehicle.wings['main_wing'].Segments[2].root_chord_percent + vehicle.wings['main_wing'].Segments[1].root_chord_percent)/2 *vehicle.wings['main_wing'].chords.root)
    fuselage.aft_centerbody_area   += 0.3*((vehicle.wings['main_wing'].Segments[3].percent_span_location - vehicle.wings['main_wing'].Segments[2].percent_span_location) * vehicle.wings['main_wing'].spans.projected) * ((vehicle.wings['main_wing'].Segments[3].root_chord_percent + vehicle.wings['main_wing'].Segments[2].root_chord_percent)/2 *vehicle.wings['main_wing'].chords.root)
    fuselage.aft_centerbody_area   += 0.3*((vehicle.wings['main_wing'].Segments[4].percent_span_location - vehicle.wings['main_wing'].Segments[3].percent_span_location) * vehicle.wings['main_wing'].spans.projected) * ((vehicle.wings['main_wing'].Segments[4].root_chord_percent + vehicle.wings['main_wing'].Segments[3].root_chord_percent)/2 *vehicle.wings['main_wing'].chords.root)
    #import pdb; pdb.set_trace()
    fuselage.aft_centerbody_taper   = vehicle.wings['main_wing'].Segments[5].root_chord_percent
    fuselage.heights.at_quarter_length          = 3.74 * Units.meter
    fuselage.heights.at_three_quarters_length   = 3.65 * Units.meter
    fuselage.heights.at_wing_root_quarter_chord = 3.74 * Units.meter
    
    # add to vehicle
    vehicle.append_component(fuselage)

    # ------------------------------------------------------------------
    #  Turbofan Network
    # ------------------------------------------------------------------    

    #initialize the gas turbine network
    gt_engine                   = SUAVE.Components.Energy.Networks.Turbofan()
    gt_engine.tag               = 'turbofan'

    gt_engine.number_of_engines = 2.0
    gt_engine.bypass_ratio      = 7
    gt_engine.engine_length     = 2.71
    gt_engine.nacelle_diameter  = 2.05

    #set the working fluid for the network
    gt_engine.working_fluid = SUAVE.Attributes.Gases.Air()


    #Component 1 : ram,  to convert freestream static to stagnation quantities
    ram = SUAVE.Components.Energy.Converters.Ram()
    ram.tag = 'ram'

    #add ram to the network
    gt_engine.ram = ram

    #Component 2 : inlet nozzle
    inlet_nozzle = SUAVE.Components.Energy.Converters.Compression_Nozzle()
    inlet_nozzle.tag = 'inlet nozzle'

    inlet_nozzle.polytropic_efficiency = 0.98
    inlet_nozzle.pressure_ratio        = 0.98

    #add inlet nozzle to the network
    gt_engine.inlet_nozzle = inlet_nozzle

    #Component 3 :low pressure compressor    
    low_pressure_compressor = SUAVE.Components.Energy.Converters.Compressor()    
    low_pressure_compressor.tag = 'lpc'

    low_pressure_compressor.polytropic_efficiency = 0.91
    low_pressure_compressor.pressure_ratio        = 1.9    

    #add low pressure compressor to the network    
    gt_engine.low_pressure_compressor = low_pressure_compressor

    #Component 4: high pressure compressor  
    high_pressure_compressor = SUAVE.Components.Energy.Converters.Compressor()    
    high_pressure_compressor.tag = 'hpc'

    high_pressure_compressor.polytropic_efficiency = 0.91
    high_pressure_compressor.pressure_ratio        = 10.0   

    #add the high pressure compressor to the network    
    gt_engine.high_pressure_compressor = high_pressure_compressor

    #Component 5 :low pressure turbine  
    low_pressure_turbine = SUAVE.Components.Energy.Converters.Turbine()   
    low_pressure_turbine.tag='lpt'

    low_pressure_turbine.mechanical_efficiency = 0.99
    low_pressure_turbine.polytropic_efficiency = 0.93

    #add low pressure turbine to the network    
    gt_engine.low_pressure_turbine = low_pressure_turbine

    #Component 5 :high pressure turbine  
    high_pressure_turbine = SUAVE.Components.Energy.Converters.Turbine()   
    high_pressure_turbine.tag='hpt'

    high_pressure_turbine.mechanical_efficiency = 0.99
    high_pressure_turbine.polytropic_efficiency = 0.93

    #add the high pressure turbine to the network    
    gt_engine.high_pressure_turbine = high_pressure_turbine 

    #Component 6 :combustor  
    combustor = SUAVE.Components.Energy.Converters.Combustor()   
    combustor.tag = 'Comb'

    combustor.efficiency                = 0.99 
    combustor.alphac                    = 1.0     
    combustor.turbine_inlet_temperature = 1500
    combustor.pressure_ratio            = 0.95
    combustor.fuel_data                 = SUAVE.Attributes.Propellants.Jet_A()    

    #add the combustor to the network    
    gt_engine.combustor = combustor

    #Component 7 :core nozzle
    core_nozzle = SUAVE.Components.Energy.Converters.Expansion_Nozzle()   
    core_nozzle.tag = 'core nozzle'

    core_nozzle.polytropic_efficiency = 0.95
    core_nozzle.pressure_ratio        = 0.99    

    #add the core nozzle to the network    
    gt_engine.core_nozzle = core_nozzle

    #Component 8 :fan nozzle
    fan_nozzle = SUAVE.Components.Energy.Converters.Expansion_Nozzle()   
    fan_nozzle.tag = 'fan nozzle'

    fan_nozzle.polytropic_efficiency = 0.95
    fan_nozzle.pressure_ratio        = 0.99

    #add the fan nozzle to the network
    gt_engine.fan_nozzle = fan_nozzle

    #Component 9 : fan   
    fan = SUAVE.Components.Energy.Converters.Fan()   
    fan.tag = 'fan'

    fan.polytropic_efficiency = 0.93
    fan.pressure_ratio        = 1.7
    fan.spinner_ratio         = 1.2
    fan.nacelle_length_to_fan_di = 1.6 # CFM56


    #add the fan to the network
    gt_engine.fan = fan    

    #Component 10 : thrust (to compute the thrust)
    thrust = SUAVE.Components.Energy.Processes.Thrust()       
    thrust.tag ='compute_thrust'

    #total design thrust (includes all the engines)
    thrust.total_design             = 2*31000/1.255 * Units.lbf #Newtons
 
    #design sizing conditions
    altitude      = 0.0*Units.ft
    mach_number   = 0.25 
    isa_deviation = 0.

    # add thrust to the network
    gt_engine.thrust = thrust

    #size the turbofan
    turbofan_sizing(gt_engine,mach_number,altitude,isa_deviation)   
    #ducted_fan_sizing(gt_engine,mach_number,altitude,isa_deviation)
    # add  gas turbine network gt_engine to the vehicle
    vehicle.append_component(gt_engine)      
    #now add weights objects
    vehicle.landing_gear       = SUAVE.Components.Landing_Gear.Landing_Gear()
    vehicle.control_systems    = SUAVE.Components.Physical_Component()
    vehicle.electrical_systems = SUAVE.Components.Physical_Component()
    vehicle.avionics           = SUAVE.Components.Energy.Peripherals.Avionics()
    vehicle.passenger_weights  = SUAVE.Components.Physical_Component()
    vehicle.furnishings        = SUAVE.Components.Physical_Component()
    vehicle.air_conditioner    = SUAVE.Components.Physical_Component()
    vehicle.fuel               = SUAVE.Components.Physical_Component()
    vehicle.apu                = SUAVE.Components.Physical_Component()
    vehicle.hydraulics         = SUAVE.Components.Physical_Component()
    vehicle.optionals          = SUAVE.Components.Physical_Component()
    #vehicle.wings['vertical_stabilizer'].rudder = SUAVE.Components.Physical_Component()
    
    # ------------------------------------------------------------------
    #   Vehicle Definition Complete
    # ------------------------------------------------------------------

    return vehicle

# ----------------------------------------------------------------------
#   Define the Configurations
# ---------------------------------------------------------------------

def configs_setup(vehicle):
    
    # ------------------------------------------------------------------
    #   Initialize Configurations
    # ------------------------------------------------------------------

    configs = SUAVE.Components.Configs.Config.Container()

    base_config = SUAVE.Components.Configs.Config(vehicle)
    base_config.tag = 'base'
    configs.append(base_config)


    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'econ'
    config.mass_properties.takeoff = 70000 * Units.kg
    config.cruise_altitude = 37000 * Units.ft
    config.cruise_step = 1 * Units.m
    configs.append(config)
    


    # ------------------------------------------------------------------
    #   Cruise Configuration
    # ------------------------------------------------------------------

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'cruise'

    configs.append(config)
    
    config.maximum_lift_coefficient = 1.2
    
    # ------------------------------------------------------------------
    #   Cruise with Spoilers Configuration
    # ------------------------------------------------------------------

    #config = SUAVE.Components.Configs.Config(base_config)
    #config.tag = 'cruise_spoilers'

   # configs.append(config)
    
    #config.maximum_lift_coefficient = 1.2


    # ------------------------------------------------------------------
    #   Takeoff Configuration
    # ------------------------------------------------------------------

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'takeoff'

    config.wings['main_wing'].flaps.angle = 20. * Units.deg
    config.wings['main_wing'].slats.angle = 25. * Units.deg

    config.V2_VS_ratio = 1.21
    config.maximum_lift_coefficient = 2.

    configs.append(config)

    # ------------------------------------------------------------------
    #   Landing Configuration
    # ------------------------------------------------------------------

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'landing'

    config.wings['main_wing'].flaps_angle = 30. * Units.deg
    config.wings['main_wing'].slats_angle = 25. * Units.deg

    config.Vref_VS_ratio = 1.23
    config.maximum_lift_coefficient = 2.2

    configs.append(config)
    
    # ------------------------------------------------------------------
    #   Short Field Takeoff Configuration
    # ------------------------------------------------------------------ 

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'short_field_takeoff'
    
    config.wings['main_wing'].flaps.angle = 20. * Units.deg
    config.wings['main_wing'].slats.angle = 25. * Units.deg

    config.V2_VS_ratio = 1.21
    config.maximum_lift_coefficient = 2. 
    
    configs.append(config)

    return configs
