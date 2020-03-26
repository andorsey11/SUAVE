import SUAVE
import numpy
from SUAVE.Core import Units
from SUAVE.Methods.Propulsion.turbofan_sizing import turbofan_sizing
from SUAVE.Methods.Propulsion.ducted_fan_sizing import ducted_fan_sizing



def setup():
    base_vehicle = base_setup()
    configs = configs_setup(base_vehicle)
    return configs




def base_setup():
    vehicle = SUAVE.Vehicle()
    vehicle.tag = 'StandardTechMid_200_6000'

    vehicle.mass_properties.max_takeoff = 352000.0 * Units.lbs 
    vehicle.mass_properties.takeoff  = 352000.0 * Units.lbs 
    vehicle.mass_properties.operating_empty = 158399.99999999997 * Units.lbs 
    vehicle.mass_properties.max_zero_fuel  = 202399.99999999997 * Units.lbs 
    vehicle.mass_properties.cargo = 0.  * Units.kilogram
    vehicle.envelope.ultimate_load = 2.5
    vehicle.envelope.limit_load    = 1.5
    vehicle.reference_area         = 2850.9719222462204  * Units['feet**2']
    vehicle.passengers             = 200
    vehicle.systems.control        = "fully powered" 
    vehicle.systems.accessories    = "long range" 
    vehicle.cruise_altitude    = 35000 
    vehicle.cruise_step        = 2000 / 3.28 * Units.m 
    vehicle.cruise_mach        =0.8275 



    landing_gear = SUAVE.Components.Landing_Gear.Landing_Gear()
    landing_gear.tag = "main_landing_gear"

    landing_gear.main_units  = 2
    landing_gear.nose_units  = 1
    landing_gear.main_wheels = 4
    landing_gear.nose_wheels = 2.0
    landing_gear.main_strut_length  = 98.82735703537493 * Units.inches
    landing_gear.nose_strut_length  = 98.82735703537493 * Units.inches
    landing_gear.main_tire_diameter = 45.75742620410691 * Units.inches
    landing_gear.nose_tire_diameter = 44.09085730965911 * Units.inches
    vehicle.landing_gear = landing_gear


    wing = SUAVE.Components.Wings.Main_Wing()
    wing.tag = 'main_wing'
    wing.areas.reference         = 2850.9719222462204 * Units['feet**2']
    wing.aspect_ratio            = 11
    wing.sweeps.quarter_chord    = 26 * Units.deg
    wing.thickness_to_chord      = 0.095
    wing.taper                   = 0.1
    wing.span_efficiency         = 0.95
    wing.yehudi_factor           = 1.2
    wing.spans.projected         = numpy.sqrt(wing.aspect_ratio * wing.areas.reference)
    wing.chords.root             = wing.yehudi_factor * 2 * wing.areas.reference / wing.spans.projected / (1+wing.taper)
    wing.chords.tip              = wing.chords.root * wing.taper
    wing.chords.mean_aerodynamic = wing.chords.root - (2*(wing.chords.root-wing.chords.tip)*(.5*wing.chords.root+wing.chords.tip)/(3*(wing.chords.root+wing.chords.tip)))
    wing.twists.root             = 2 * Units.degrees
    wing.twists.tip              = 0.0 * Units.degrees
    wing.origin                  = [23.181055999999998,0,-0.9753599999999999]# meters
    wing.vertical                = False
    wing.symmetric               = True
    wing.high_lift               = True
    wing.dynamic_pressure_ratio  = 1.08
    wing.fuel_volume             = (wing.thickness_to_chord * wing.chords.root * wing.chords.root*(.4) + wing.thickness_to_chord* wing.chords.tip * wing.chords.tip*.4) / 2 *wing.spans.projected* .9 * .7


    wing.flaps.chord      =  0.30
    wing.flaps.span_start =  0.10
    wing.flaps.span_end   =  0.75
    wing.flaps.type       = 'double_slotted'
    vehicle.append_component(wing)





    wing = SUAVE.Components.Wings.Wing()
    wing.tag = 'horizontal_stabilizer'
    wing.yehudi_factor           = 1.0
    wing.areas.reference         = 712.7429805615551 * Units['feet**2']
    wing.aspect_ratio            = 6  
    wing.sweeps.quarter_chord    = 40 * Units.deg
    wing.thickness_to_chord      = 0.08
    wing.taper                   = 0.2
    wing.span_efficiency         = 0.9
    wing.spans.projected         = numpy.sqrt(wing.aspect_ratio * wing.areas.reference)
    wing.chords.root             = wing.yehudi_factor * 2 * wing.areas.reference / wing.spans.projected / (1+wing.taper)
    wing.chords.tip              = wing.chords.root * wing.taper
    wing.chords.mean_aerodynamic = wing.chords.root - (2*(wing.chords.root-wing.chords.tip)*(.5*wing.chords.root+wing.chords.tip)/(3*(wing.chords.root+wing.chords.tip)))
    wing.origin                  = [43.46448,0,2.92608]
    wing.vertical                = False
    wing.symmetric               = True
    wing.dynamic_pressure_ratio  = 0.9
    vehicle.append_component(wing)





    wing = SUAVE.Components.Wings.Wing()
    wing.tag = 'vertical_stabilizer'
    wing.yehudi_factor           = 1
    wing.areas.reference         = 570.1943844492441 * Units['feet**2']
    wing.aspect_ratio            = 2
    wing.sweeps.quarter_chord    = 25. * Units.deg
    wing.thickness_to_chord      = 0.08
    wing.taper                   = 0.25
    wing.span_efficiency         = 0.9
    wing.spans.projected         = numpy.sqrt(wing.aspect_ratio * wing.areas.reference)
    wing.chords.root             = wing.yehudi_factor * 2 * wing.areas.reference / wing.spans.projected / (1+wing.taper)
    wing.chords.tip              = wing.chords.root * wing.taper
    wing.chords.mean_aerodynamic = wing.chords.root - (2*(wing.chords.root-wing.chords.tip)*(.5*wing.chords.root+wing.chords.tip)/(3*(wing.chords.root+wing.chords.tip)))
    wing.twists.root             = 0.0 * Units.degrees
    wing.twists.tip              = 0.0 * Units.degrees
    wing.origin                  = [41.04978666666666,0,3.316224]
    wing.vertical                = True
    wing.symmetric               = False
    wing.t_tail                  = False
    wing.dynamic_pressure_ratio  = 1.0
    wing.q_cl_vertical           = 2000
    vehicle.append_component(wing)





    fuselage = SUAVE.Components.Fuselages.Fuselage()
    fuselage.tag = 'fuselage'
    fuselage.number_coach_seats      = vehicle.passengers
    fuselage.seats_abreast           = 6
    fuselage.seat_pitch              = 0.8635999999999999 * Units.meter
    fuselage.fineness.nose           = 2
    fuselage.fineness.tail           = 3
    fuselage.lengths.nose            = 7.802879999999999 * Units.meter 
    fuselage.lengths.tail            = 11.70432 * Units.meter 
    fuselage.lengths.cabin           = 28.786666666666665 * Units.meter 
    fuselage.lengths.total           = 48.293866666666666 * Units.meter 
    fuselage.lengths.fore_space      = 6.242304 * Units.meter 
    fuselage.lengths.aft_space       = 9.363456 * Units.meter 
    fuselage.width                   = 3.9014399999999996 * Units.meter
    fuselage.heights.maximum         = 3.9014399999999996 * Units.meter
    fuselage.effective_diameter      = 3.9014399999999996 * Units.meter 
    fuselage.areas.side_projected    = fuselage.width * fuselage.lengths.total *  Units['meters**2']
    fuselage.areas.wetted            = 2*3.14*fuselage.width/2*(fuselage.lengths.cabin+(fuselage.lengths.total - fuselage.lengths.cabin)*.5)  * Units['meters**2']
    fuselage.areas.front_projected   = fuselage.width / 2 * fuselage.width / 2 * 3.14 * Units['meters**2']
    fuselage.differential_pressure   = 5.0e4 * Units.pascal
    fuselage.heights.at_quarter_length = 3.9014399999999996 * Units.meter
    fuselage.heights.at_three_quarters_length = 3.9014399999999996 * Units.meter
    fuselage.heights.at_wing_root_quarter_chord = 3.9014399999999996* Units.meter
    vehicle.append_component(fuselage)






    gt_engine                   = SUAVE.Components.Energy.Networks.Turbofan()
    gt_engine.tag               = 'turbofan'

    gt_engine.number_of_engines = 2.0
    gt_engine.bypass_ratio      = 7
    gt_engine.engine_length     = 2.71
    gt_engine.nacelle_diameter  = 2.05

    gt_engine.working_fluid = SUAVE.Attributes.Gases.Air()

    ram = SUAVE.Components.Energy.Converters.Ram()
    ram.tag = 'ram'

    gt_engine.ram = ram

    inlet_nozzle = SUAVE.Components.Energy.Converters.Compression_Nozzle()
    inlet_nozzle.tag = 'inlet nozzle'

    inlet_nozzle.polytropic_efficiency = 0.98
    inlet_nozzle.pressure_ratio        = 0.98

    gt_engine.inlet_nozzle = inlet_nozzle

    low_pressure_compressor = SUAVE.Components.Energy.Converters.Compressor()
    low_pressure_compressor.tag = 'lpc'

    low_pressure_compressor.polytropic_efficiency = 0.91
    low_pressure_compressor.pressure_ratio        = 1.9

    gt_engine.low_pressure_compressor = low_pressure_compressor

    high_pressure_compressor = SUAVE.Components.Energy.Converters.Compressor()
    high_pressure_compressor.tag = 'hpc'

    high_pressure_compressor.polytropic_efficiency = 0.91
    high_pressure_compressor.pressure_ratio        = 10.0

    gt_engine.high_pressure_compressor = high_pressure_compressor
    low_pressure_turbine = SUAVE.Components.Energy.Converters.Turbine()
    low_pressure_turbine.tag='lpt'

    low_pressure_turbine.mechanical_efficiency = 0.99
    low_pressure_turbine.polytropic_efficiency = 0.93

    gt_engine.low_pressure_turbine = low_pressure_turbine

    high_pressure_turbine = SUAVE.Components.Energy.Converters.Turbine()
    high_pressure_turbine.tag='hpt'

    high_pressure_turbine.mechanical_efficiency = 0.99
    high_pressure_turbine.polytropic_efficiency = 0.93

    gt_engine.high_pressure_turbine = high_pressure_turbine

    combustor = SUAVE.Components.Energy.Converters.Combustor()
    combustor.tag = 'Comb'

    combustor.efficiency                = 0.99 
    combustor.alphac                    = 1.0     
    combustor.turbine_inlet_temperature = 1500
    combustor.pressure_ratio            = 0.95
    combustor.fuel_data                 = SUAVE.Attributes.Propellants.Jet_A() 

    gt_engine.combustor = combustor

    core_nozzle = SUAVE.Components.Energy.Converters.Expansion_Nozzle()
    core_nozzle.tag = 'core nozzle'

    core_nozzle.polytropic_efficiency = 0.95
    core_nozzle.pressure_ratio        = 0.99

    gt_engine.core_nozzle = core_nozzle

    fan_nozzle = SUAVE.Components.Energy.Converters.Expansion_Nozzle()
    fan_nozzle.tag = 'fan nozzle'

    fan_nozzle.polytropic_efficiency = 0.95
    fan_nozzle.pressure_ratio        = 0.99

    gt_engine.fan_nozzle = fan_nozzle

    fan = SUAVE.Components.Energy.Converters.Fan()
    fan.tag = 'fan'

    fan.polytropic_efficiency = 0.93
    fan.pressure_ratio        = 1.7
    fan.spinner_ratio         = 1.25 
    fan.nacelle_length_to_fan_di = 1.5

    gt_engine.fan = fan

    thrust = SUAVE.Components.Energy.Processes.Thrust()

    thrust.tag ='compute_thrust'
    thrust.total_design             = 112191.23505976096 * Units.lbf

    altitude      = 0.0*Units.ft
    mach_number   = 0.25 
    isa_deviation = 0.

    gt_engine.thrust = thrust

    turbofan_sizing(gt_engine,mach_number,altitude,isa_deviation)

    vehicle.append_component(gt_engine)

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
    vehicle.wings['vertical_stabilizer'].rudder = SUAVE.Components.Physical_Component()




    return vehicle

def configs_setup(vehicle):

    configs = SUAVE.Components.Configs.Config.Container()

    base_config = SUAVE.Components.Configs.Config(vehicle)
    base_config.tag = 'base'
    configs.append(base_config)

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'cruise'

    configs.append(config)

    config.maximum_lift_coefficient = 1.2

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'takeoff'

    config.wings['main_wing'].flaps.angle = 20. * Units.deg
    config.wings['main_wing'].slats.angle = 25. * Units.deg

    config.V2_VS_ratio = 1.21
    config.maximum_lift_coefficient = 2.

    configs.append(config)

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'landing'

    config.wings['main_wing'].flaps_angle = 30. * Units.deg
    config.wings['main_wing'].slats_angle = 25. * Units.deg
    config.Vref_VS_ratio = 1.23
    config.maximum_lift_coefficient = 2.6
    configs.append(config)

    config = SUAVE.Components.Configs.Config(base_config)
    config.tag = 'short_field_takeoff'

    config.wings['main_wing'].flaps.angle = 20. * Units.deg
    config.wings['main_wing'].slats.angle = 25. * Units.deg
    config.V2_VS_ratio = 1.21
    config.maximum_lift_coefficient = 2. 
    configs.append(config)
    return configs
