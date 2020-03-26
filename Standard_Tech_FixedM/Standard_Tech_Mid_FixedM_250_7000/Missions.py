# Missions.py
# 
# Created:  Mar 2016, M. Vegh
# Modified: Aug 2017, E. Botero

# ----------------------------------------------------------------------        
#   Imports
# ----------------------------------------------------------------------    

import SUAVE
from SUAVE.Core import Units
import pdb
import numpy as np

# ----------------------------------------------------------------------
#   Define the Mission
# ----------------------------------------------------------------------
    
def setup(analyses, vehicle):
    
    # the mission container
    missions = SUAVE.Analyses.Mission.Mission.Container()

    # ------------------------------------------------------------------
    #   Base Mission
    # ------------------------------------------------------------------
    base_mission = base(analyses, vehicle)
    missions.base = base_mission 
 
    return missions  
    
def base(analyses, vehicle):
    
    # ------------------------------------------------------------------
    #   Initialize the Mission
    # ------------------------------------------------------------------
    tolerance = 30
    mission = SUAVE.Analyses.Mission.Sequential_Segments()
    mission.tag = 'the_mission'
    mission.cruise_altitude = vehicle.base.cruise_altitude
    mission.cruise_mach     = vehicle.base.cruise_mach
    #airport
    airport = SUAVE.Attributes.Airports.Airport()
    airport.altitude   =  0.0  * Units.ft
    airport.delta_isa  =  0.0
    airport.atmosphere =  SUAVE.Analyses.Atmospheric.US_Standard_1976()

    mission.airport = airport    

    # unpack Segments module
    Segments = SUAVE.Analyses.Mission.Segments
    # base segment
    base_segment    = Segments.Segment()
    atmosphere      = SUAVE.Attributes.Atmospheres.Earth.US_Standard_1976()
    planet          = SUAVE.Attributes.Planets.Earth()
    #Unpack cruise point as the referene
    cruise_altitude = mission.cruise_altitude
    cruise_atmo     = airport.atmosphere.compute_values(cruise_altitude,0)
    cruise_mach     = mission.cruise_mach
    cruise_speed    = cruise_mach * cruise_atmo.speed_of_sound
   # cruise_speed    = 450 * Units.knots
    #-------------------------------------------------------------------
    #import pdb; pdb.set_trace()
   # print(mission.cruise_altitude / Units.ft)
    segment = Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "climb_1"

    # connect vehicle configuration
    segment.analyses.extend( analyses.cruise )

    # segment attributes
    segment.atmosphere   = atmosphere
    segment.planet       = planet
    segment.altitude_start = 1500  * Units.ft
    segment.altitude_end = cruise_altitude * .5
    climb_atmo = airport.atmosphere.compute_values(segment.altitude_end,0)
    #air_speed_ratio 
    segment.air_speed    = cruise_speed * np.sqrt(cruise_atmo.density/climb_atmo.density)
  #  segment.air_speed    = cruise_speed * .5
 
    if segment.air_speed < 0:
        segment.airspeed = cruise_speed * .3
        print('airspeed error!?!!')
    segment.climb_rate   = 1000. * Units['ft/min']
    segment.state.numerics.number_control_points = tolerance
    # add to mission
    mission.append_segment(segment)
   
    # ------------------------------------------------------------------
    #   Third Climb Segment: Constant Speed, Constant Climb Rate
    # ------------------------------------------------------------------

    segment = Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "climb_3"

    # # connect vehicle configuration
    segment.analyses.extend( analyses.cruise )

    # segment attributes
    segment.atmosphere   = atmosphere
    segment.planet       = planet
    segment.altitude_end = cruise_altitude * .7
    climb_atmo = airport.atmosphere.compute_values(segment.altitude_end,0)
    #air_speed_ratio 
    segment.air_speed    = cruise_speed * np.sqrt(cruise_atmo.density/climb_atmo.density) # flies at or less than the cruise Cl
  #  segment.air_speed    = cruise_speed * .7
    if segment.air_speed < 0:
         segment.airspeed = cruise_speed * .3
    segment.climb_rate   = 500. * Units['ft/min']
    segment.state.numerics.number_control_points = tolerance

    # # add to mission
    mission.append_segment(segment)
    
     # ------------------------------------------------------------------
    #   Fourth Climb Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------

    segment = Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "climb_5"

    # connect vehicle configuration
    segment.analyses.extend( analyses.cruise )

    # segment attributes
    segment.atmosphere   = atmosphere
    segment.planet       = planet
    segment.altitude_end = cruise_altitude
    climb_atmo = airport.atmosphere.compute_values(segment.altitude_end,0)
    #air_speed_ratio 
    segment.air_speed    = cruise_speed * np.sqrt(cruise_atmo.density/climb_atmo.density)
  #  segment.air_speed    = cruise_speed * .8

    segment.climb_rate   = 300. * Units['ft/min']  #  Top of Climb requirement is 300 fpm reserve
    segment.state.numerics.number_control_points = tolerance

    # add to mission
    mission.append_segment(segment)   
    
    # ------------------------------------------------------------------
    #   Cruise Segment: Constant Speed, Constant Altitude
    # ------------------------------------------------------------------

    segment = Segments.Cruise.Constant_Speed_Constant_Altitude()
    segment.tag = "cruise1"

    # connect vehicle configuration
    segment.analyses.extend( analyses.cruise )

    # segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet

    segment.air_speed  = cruise_speed
    segment.distance   = 2050. * Units.nmi
    segment.state.numerics.number_control_points = tolerance

    # add to mission
    mission.append_segment(segment)


    segment = Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "step_climb"

    segment.analyses.extend( analyses.cruise)
    segment.atmosphere   = atmosphere
    segment.planet       = planet
    segment.altitude_end = cruise_altitude + vehicle.base.cruise_step 
    climb_atmo = airport.atmosphere.compute_values(segment.altitude_end - vehicle.base.cruise_step,0)
    #air_speed_ratio 
    segment.air_speed    = cruise_speed
  #  segment.air_speed    = cruise_speed * .8

    segment.climb_rate   = 300. * Units['ft/min']  #  Top of Climb requirement is 300 fpm reserve
    segment.state.numerics.number_control_points = tolerance

    mission.append_segment(segment)


    segment = Segments.Cruise.Constant_Speed_Constant_Altitude()
    segment.tag = "cruise2"

    # connect vehicle configuration
    segment.analyses.extend( analyses.cruise )

    # segment attributes
    segment.atmosphere = atmosphere
    segment.planet     = planet

    segment.air_speed  = cruise_speed
    segment.distance   = 2050. * Units.nmi
    segment.state.numerics.number_control_points = tolerance

    # add to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   First Descent Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------

    segment = Segments.Descent.Constant_Speed_Constant_Rate()
    segment.tag = "descent_1"

    # connect vehicle configuration
    segment.analyses.extend( analyses.cruise )

    # segment attributes
    segment.atmosphere   = atmosphere
    segment.planet       = planet

    segment.altitude_end = cruise_altitude *.7
    climb_atmo = airport.atmosphere.compute_values(segment.altitude_end,0)
    #air_speed_ratio 
    segment.air_speed    = cruise_speed * np.sqrt(cruise_atmo.density/climb_atmo.density)
    segment.descent_rate = 1000. * Units['ft/min']
    segment.state.numerics.number_control_points = tolerance

    # add to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   Second Descent Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------

    segment = Segments.Descent.Constant_Speed_Constant_Rate()
    segment.tag = "descent_2"

    # connect vehicle configuration
    segment.analyses.extend( analyses.cruise )

    # segment attributes
    segment.atmosphere   = atmosphere
    segment.planet       = planet

    segment.altitude_end = cruise_altitude * .5
    climb_atmo = airport.atmosphere.compute_values(segment.altitude_end,0)
    #air_speed_ratio 
    segment.air_speed    = cruise_speed * np.sqrt(cruise_atmo.density/climb_atmo.density)
    segment.descent_rate = 700. * Units['ft/min']
    segment.state.numerics.number_control_points = tolerance

    # append to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   Third Descent Segment: Constant Speed, Constant Rate
    # ------------------------------------------------------------------

    segment = Segments.Descent.Constant_Speed_Constant_Rate()
    segment.tag = "descent_3"

    # connect vehicle configuration
    segment.analyses.extend( analyses.cruise )

    # segment attributes
    segment.atmosphere   = atmosphere
    segment.planet       = planet

    segment.altitude_end = 0.0   * Units.km
    climb_atmo = airport.atmosphere.compute_values(segment.altitude_end,0)
    #air_speed_ratio 
    segment.air_speed    = cruise_speed * np.sqrt(cruise_atmo.density/climb_atmo.density)
    segment.descent_rate = 500. * Units['ft/min']
    segment.state.numerics.number_control_points = tolerance

    # append to mission
    mission.append_segment(segment)

    # ------------------------------------------------------------------
    #   Mission definition complete    
    # ------------------------------------------------------------------
    
    
    #------------------------------------------------------------------
    ###         Reserve mission
    #------------------------------------------------------------------
    
    # ------------------------------------------------------------------
    #   First Climb Segment: Constant Speed, Constant Throttle
    # ------------------------------------------------------------------
 
    segment = Segments.Climb.Constant_Speed_Constant_Rate()
    segment.tag = "reserve_climb"
 
    # connect vehicle configuration
    segment.analyses.extend( analyses.base )
 
    # define segment attributes
    segment.atmosphere     = atmosphere
    segment.planet         = planet
 
    segment.altitude_start = 0    * Units.ft
    segment.altitude_end   = 15000  * Units.ft
    climb_atmo = airport.atmosphere.compute_values(segment.altitude_end,0)
    #air_speed_ratio 
    segment.air_speed    = cruise_speed * np.sqrt(cruise_atmo.density/climb_atmo.density)
    segment.climb_rate     = 1000.  * Units['ft/min']
    segment.state.numerics.number_control_points = tolerance

    # add to misison
    mission.append_segment(segment)
    
    # ------------------------------------------------------------------
    #   Cruise Segment: constant speed, constant altitude
    # ------------------------------------------------------------------
    
    segment = Segments.Cruise.Constant_Mach_Constant_Altitude(base_segment)
    segment.tag = "reserve_cruise"
    
    segment.analyses.extend( analyses.cruise )
    segment.altitude = 15000 * Units.ft
    climb_atmo = airport.atmosphere.compute_values(segment.altitude,0)
    air_speed    = cruise_speed * np.sqrt(cruise_atmo.density/climb_atmo.density)
    segment.mach      = air_speed / climb_atmo.speed_of_sound
    segment.distance  = 140.0 * Units.nautical_mile 
    segment.state.numerics.number_control_points = tolerance
   
    mission.append_segment(segment)
    
    segment = Segments.Descent.Linear_Mach_Constant_Rate(base_segment)

    segment.tag = "reserve_descent_1"
    
    segment.analyses.extend( analyses.cruise )
    
    segment.altitude_end = 1500   * Units.ft
    segment.descent_rate = 3.0   * Units['m/s']
    climb_atmo = airport.atmosphere.compute_values(segment.altitude_end,0)
    #air_speed_ratio 
    air_speed    = cruise_speed * np.sqrt(cruise_atmo.density/climb_atmo.density)
    segment.mach_end    = air_speed / climb_atmo.speed_of_sound
    segment.mach_start  = air_speed / climb_atmo.speed_of_sound
    segment.state.numerics.number_control_points = tolerance
    
    # append to mission
    mission.append_segment(segment)



    # ------------------------------------------------------------------
    #   Loiter Segment: constant mach, constant time
    # ------------------------------------------------------------------
    
    segment = Segments.Cruise.Constant_Mach_Constant_Altitude_Loiter(base_segment)
    segment.tag = "reserve_loiter"
    
    segment.analyses.extend( analyses.cruise )
    segment.altitude = 1500 * Units.ft
    climb_atmo = airport.atmosphere.compute_values(segment.altitude,0)
    #air_speed_ratio 
    air_speed    = cruise_speed * np.sqrt(cruise_atmo.density/climb_atmo.density)
    segment.mach = 0.5 #air_speed / climb_atmo.speed_of_sound
    segment.time = 30.0 * Units.minutes
    segment.state.numerics.number_control_points = tolerance
    
    mission.append_segment(segment)  
    
    #------------------------------------------------------------------
    ###         Reserve mission completed
    #------------------------------------------------------------------
    
    return mission

# ----------------------------------------------------------------------        
#   Call Main
# ----------------------------------------------------------------------    

if __name__ == '__main__':
    import vehicles
    import analyses
    
    vehicles = vehicles.setup()
    analyses = analyses.setup(vehicles)
    missions = setup(analyses)
    
    vehicles.finalize()
    analyses.finalize()
    missions.finalize()
    
    missions.base.evaluate()
