# Plot_Mission.py
# 
# Created:  May 2015, E. Botero
# Modified: 

# ----------------------------------------------------------------------        
#   Imports
# ----------------------------------------------------------------------    

import SUAVE
from SUAVE.Core import Units, Data
from SUAVE.Input_Output.Results import print_weight_breakdown
from SUAVE.Input_Output.Results import print_engine_data
from SUAVE.Input_Output.Results import print_mission_breakdown
from SUAVE.Input_Output.Results import print_parasite_drag
from SUAVE.Input_Output.Results import print_compress_drag
import pylab as plt
import pandas as pd
import numpy as np
from SUAVE.Input_Output.Results import print_sectional_cl

# ----------------------------------------------------------------------
#   Plot Mission
# ----------------------------------------------------------------------

def plot_mission(nexus,line_style='bo-'):
    results   = nexus.results.base
    axis_font = {'fontname':'Arial', 'size':'14'}    

    vehicle = nexus.vehicle_configurations.base

  #   # ------------------------------------------------------------------
  #   #   Altitude, sfc, vehicle weight
  #   # ------------------------------------------------------------------
   # fig = plt.figure("Altitude_sfc_weight",figsize=(8,10))
    for segment in results.segments.values():
         # 
            
          if segment.tag == 'cruise1':
              mdot     = segment.conditions.weights.vehicle_mass_rate[:,0]
              thrust   =  segment.conditions.frames.body.thrust_force_vector[:,0]
              sfc      = (mdot / Units.lb) / (thrust /Units.lbf) * Units.hr
              eta      = segment.conditions.freestream.velocity[:,0] / Units.knots * 7.807 / 18580 / sfc
              CLift  = segment.conditions.aerodynamics.lift_coefficient[:,0]
              CDrag  = segment.conditions.aerodynamics.drag_coefficient[:,0]
              loverd = CLift/ CDrag
              velocity = segment.conditions.freestream.velocity[:,0]
              reynolds = segment.conditions.freestream.reynolds_number
              ref_condition = segment.conditions.freestream
              Cdp   = segment.conditions.aerodynamics.drag_breakdown.parasite.total[0]
              Cdi   = segment.conditions.aerodynamics.drag_breakdown.induced.total[0]
              visce = segment.conditions.aerodynamics.drag_breakdown.induced.efficiency_factor[0]
              Cdc = segment.conditions.aerodynamics.drag_breakdown.compressible.total[0]
              Cdm  = segment.conditions.aerodynamics.drag_breakdown.miscellaneous.total[0]
              Cdt  = segment.conditions.aerodynamics.drag_breakdown.trim_corrected_drag[0]- segment.conditions.aerodynamics.drag_breakdown.untrimmed[0]
              print_sectional_cl(segment,vehicle,'design_sectional_cl.txt')
              
    
    #plt.show(block = True)
    print_weight_breakdown(vehicle, 'weight_output.txt')
    #print_engine_data(vehicle,'engine_output.txt')
    print_mission_breakdown(results,'mission_output.txt')

   # import pdb; pdb.set_trace()

    ref_conditions = Data()
    ref_conditions.freestream = Data()

    altitude   = vehicle.cruise_altitude
    atmosphere = SUAVE.Analyses.Atmospheric.US_Standard_1976()
    freestream_ref = atmosphere.compute_values(vehicle.cruise_altitude)
    ref_conditions.freestream.velocity           = vehicle.cruise_mach * freestream_ref.speed_of_sound
    ref_conditions.freestream.density            = freestream_ref.density
    ref_conditions.freestream.dynamic_viscosity  = freestream_ref.dynamic_viscosity

    ref_condition.mach_number = vehicle.cruise_mach
    ref_condition.reynolds_number = reynolds[0] * vehicle.wings.main_wing.chords.mean_aerodynamic 
  
    print_parasite_drag(ref_condition, vehicle, nexus.analyses)
    #print_compress_drag(vehicle, nexus.analyses)
    config = nexus.vehicle_configurations.base
    econ_config = nexus.vehicle_configurations.econ
    #vertical_arm = (config.wings.vertical_stabilizer.origin[0] + config.wings.vertical_stabilizer.aerodynamic_center[0]) - (config.wings.main_wing.origin[0] + config.wings.main_wing.aerodynamic_center[0])
    #horizontal_arm = (config.wings.horizontal_stabilizer.origin[0] + config.wings.horizontal_stabilizer.aerodynamic_center[0]) - (config.wings.main_wing.origin[0] + config.wings.main_wing.aerodynamic_center[0])
    empty_weight     = vehicle.mass_properties.operating_empty
    passenger_weight = vehicle.passenger_weights.mass_properties.mass 
    bags             = vehicle.mass_properties.breakdown.bag  
    f_write_config = open('config_overview.txt', "w+")
    #Write config key parameters
    #f_write_config.write("Configuration Name                         = " + str(vehicle.tag) " \n")
    f_write_config.write("MTOW                                       = " + "%.0f" % (vehicle.mass_properties.max_takeoff * 2.20462) + "  lbm\n")
    f_write_config.write("MLW                                        = " + "%.0f" % (vehicle.mass_properties.max_landing * 2.20462) + "  lbm \n")
   # f_write_config.write("MZFW                                       = " + "%.0f" % (vehicle.mass_properties.max_zero_fuel[0] * 2.20462) + "  lbm \n")
    f_write_config.write("Payload                                    = " + "%.0f" % ((passenger_weight + bags + vehicle.mass_properties.cargo)  * 2.20462) + " lbm \n")
    f_write_config.write("OEW                                        = " + "%.0f" % (vehicle.mass_properties.operating_empty * 2.20462) + " lbm \n\n")

    f_write_config.write("Engine Type                                = " + str(vehicle.propulsors['turbofan'].tag) + "\n")
    f_write_config.write("Engine Thrust (M0.25)                      = " + "%.0f" % ((vehicle.propulsors['turbofan'].thrust.design_thrust*.2248) / vehicle.propulsors['turbofan'].number_of_engines) + "  lbf\n")
    f_write_config.write("Number of Engines                          = " + str(vehicle.propulsors['turbofan'].number_of_engines) + " \n")
    f_write_config.write("Engine Bypass Ratio                        = " + str(vehicle.propulsors['turbofan'].bypass_ratio) +  "\n")
    f_write_config.write("Nacelle Diameter                           = " + "%.1f" % (nexus.summary.nacelle_d)+ " inches\n")
    f_write_config.write("Fan Diameter                               = " + "%.1f" % (vehicle.propulsors['turbofan'].fan_diameter * 39.37)+ " Inches\n")
    f_write_config.write("Fan Pressure Ratio                         = " + str(vehicle.propulsors['turbofan'].fan.pressure_ratio) +  "\n")
    f_write_config.write("Thrust to Weight (SLS)                     = " + "%.3f" % ((vehicle.propulsors['turbofan'].sealevel_static_thrust*.2248 * vehicle.propulsors['turbofan'].number_of_engines) / (vehicle.mass_properties.max_takeoff*2.20462)) +  "\n\n")

    f_write_config.write("Wing Area                                  = " + "%.0f" % (vehicle.wings.main_wing.areas.reference * 10.7639) + "  sqft\n")
    f_write_config.write("Wing AR                                    = " + "%.2f" % (vehicle.wings.main_wing.aspect_ratio) + "\n")
    f_write_config.write("Wing t/c                                   = " + "%.3f" % (vehicle.wings.main_wing.thickness_to_chord) + "\n")
    f_write_config.write("Wing Span                                  = " + "%.1f" % (vehicle.wings.main_wing.spans.projected * 3.2808) +"  ft\n")
    f_write_config.write("Wing Loading                               = " + "%.1f" % ((vehicle.mass_properties.max_takeoff * 2.20462 ) / (vehicle.wings.main_wing.areas.reference * 10.7639)) + "  lbs/sqft\n")
   #f_write_config.write("Wing Origin                                = " + "%.2f" % (vehicle.wings.main_wing.origin[0] * 3.2808) + "  ft\n")  
    f_write_config.write("Fuel Volume                                = " + "%.0f" % (vehicle.wings.main_wing.fuel_volume * 264.172) + "  USG\n")
    f_write_config.write("Wing Sweep                                 = " + "%.1f" % (vehicle.wings.main_wing.sweeps.quarter_chord *180/3.14)  + " deg \n")
    #f_write_config.write("Horizontail Tail Area / Volume Coefficient = " + "%.0f" % (vehicle.wings.horizontal_stabilizer.areas.reference * 10.7639) + " / "+ "%.3f" %((vehicle.wings.horizontal_stabilizer.areas.reference * horizontal_arm) / (vehicle.wings.main_wing.areas.reference * vehicle.wings.main_wing.chords.mean_aerodynamic)) + "  sqft / nd\n")
    f_write_config.write("Winglet Tail Area (per side)               = " + "%.0f" % (vehicle.wings.vertical_stabilizer_l.areas.reference * 10.7639) +" sqft\n\n")

    f_write_config.write("--------------------------DESIGN RANGE-----------------------------------" + "\n")
    f_write_config.write("Cruise Altitude                            = " + "%.0f" % (vehicle.cruise_altitude * 3.2808) + "  ft\n")
    f_write_config.write("Cruise Mach                                = " + "%.3f" % (vehicle.cruise_mach) +"\n")
    f_write_config.write("Initial Cruise Thrust                      = " + "%.2f" % (thrust[0] * .2248) +  " lbf\n")    
    f_write_config.write("Initial Cruise Cl                          = " + "%.2f" % (CLift[0]) +  "\n")    
    f_write_config.write("Initial Parasite Cd                        = " + "%.5f" % (Cdp) +  "\n")    
    f_write_config.write("Initial Induced Cd                         = " + "%.5f" % (Cdi) +  "\n")    
    f_write_config.write("Initial Viscous e                          = " + "%.5f" % (visce) +  "\n")    
    f_write_config.write("Initial Compressible Cd                    = " + "%.5f" % (Cdc) +  "\n")    
    f_write_config.write("Initial Misc Cd                            = " + "%.5f" % (Cdm) +  "\n")    
    f_write_config.write("Initial Trim Cd                            = " + "%.5f" % (Cdt) +  "\n")    
    f_write_config.write("Initial Total Cd                           = " + "%.5f" % (CDrag[0]) +  "\n")    
    f_write_config.write("Initial Cruise L/D                         = " + "%.1f" % (loverd[0]) +  "\n")
    f_write_config.write("Initial Cruise SFC                         = " + "%.3f" % (sfc[0]) + "  lbm/lbf-hr\n")
    f_write_config.write("Initial Cruise Engine Efficiency           = " + "%.3f" % (eta[0]) + " percent  \n")
    f_write_config.write("Cruise Range Factor                        = " + "%.1f" % ((1/sfc[0])*loverd[0]*velocity[0]) + " \n\n")
    f_write_config.write("Design Mission Fuel Burn                   = " + "%.0f" % (nexus.summary.base_mission_fuelburn[0] / Units.lbs) + "  lbs \n\n")



    results   = nexus.results.econ
    for segment in results.segments.values():
         # 

          if segment.tag == 'cruise1':
              mdot     = segment.conditions.weights.vehicle_mass_rate[:,0]
              thrust   =  segment.conditions.frames.body.thrust_force_vector[:,0]
              sfc      = (mdot / Units.lb) / (thrust /Units.lbf) * Units.hr
              eta      = segment.conditions.freestream.velocity[:,0] / Units.knots * 7.807 / 18580 / sfc
              CLift  = segment.conditions.aerodynamics.lift_coefficient[:,0]
              CDrag  = segment.conditions.aerodynamics.drag_coefficient[:,0]
              loverd = CLift/ CDrag
              velocity = segment.conditions.freestream.velocity[:,0]
              reynolds = segment.conditions.freestream.reynolds_number
              ref_condition = segment.conditions.freestream
              Cdp   = segment.conditions.aerodynamics.drag_breakdown.parasite.total[0]
              Cdi   = segment.conditions.aerodynamics.drag_breakdown.induced.total[0]
              visce = segment.conditions.aerodynamics.drag_breakdown.induced.efficiency_factor[0]
              Cdc = segment.conditions.aerodynamics.drag_breakdown.compressible.total[0]
              Cdm  = segment.conditions.aerodynamics.drag_breakdown.miscellaneous.total[0]
              Cdt  = segment.conditions.aerodynamics.drag_breakdown.trim_corrected_drag[0]- segment.conditions.aerodynamics.drag_breakdown.untrimmed[0]
              print_sectional_cl(segment,vehicle,'econ_sectional_cl.txt')

    vehicle     = nexus.vehicle_configurations.econ
    f_write_config.write("--------------------------ECON RANGE-----------------------------------" + "\n")
    f_write_config.write("Cruise Altitude - Econ                     = " + "%.0f" % (vehicle.cruise_altitude * 3.2808) + "  ft\n")
    f_write_config.write("Cruise Mach                                = " + "%.3f" % (vehicle.cruise_mach) +"\n")
    f_write_config.write("Initial Cruise Thrust                      = " + "%.2f" % (thrust[0] * .2248) +  " lbf\n")    
    f_write_config.write("Initial Cruise Cl                          = " + "%.2f" % (CLift[0]) +  "\n")    
    f_write_config.write("Initial Parasite Cd                        = " + "%.5f" % (Cdp) +  "\n")    
    f_write_config.write("Initial Induced Cd                         = " + "%.5f" % (Cdi) +  "\n")    
    f_write_config.write("Initial Viscous e                          = " + "%.5f" % (visce) +  "\n")    
    f_write_config.write("Initial Compressible Cd                    = " + "%.5f" % (Cdc) +  "\n")    
    f_write_config.write("Initial Misc Cd                            = " + "%.5f" % (Cdm) +  "\n")    
    f_write_config.write("Initial Trim Cd                            = " + "%.5f" % (Cdt) +  "\n")    
    f_write_config.write("Initial Total Cd                           = " + "%.5f" % (CDrag[0]) +  "\n")    
    f_write_config.write("Initial Cruise L/D                         = " + "%.1f" % (loverd[0]) +  "\n")
    f_write_config.write("Initial Cruise SFC                         = " + "%.3f" % (sfc[0]) + "  lbm/lbf-hr\n")
    f_write_config.write("Initial Cruise Engine Efficiency           = " + "%.3f" % (eta[0]) + " percent  \n")
    f_write_config.write("Cruise Range Factor                        = " + "%.1f" % ((1/sfc[0])*loverd[0]*velocity[0]) + " \n\n")
    f_write_config.write("Econ Mission Takeoff Weight                = " + "%.0f" % (nexus.summary.econ_mission_fuelburn[0] / Units.lbs) + "  lbs \n\n")
    f_write_config.write("--------------------------REQUIREMENTS-----------------------------------" + "\n")

    f_write_config.write("Maximum Throttle Setting / Requirement     = " + "%.2f" % (nexus.summary.max_throttle) + " / " + str(nexus.optimization_problem.constraints[2][3]) + "\n")
    f_write_config.write("Takeoff Field Length / Requirement         = " + "%.0f" % (nexus.summary.takeoff_field_length[0][0] * 3.2808) + " / " + "%.0f" % (nexus.optimization_problem.constraints[3][3] * 3.2808) + "  ft/ft\n")
    f_write_config.write("Approach Speed / Requirement               = " + "%.1f" % (nexus.summary.approach_Speed * 1.9438) + " / " + "%.1f" % (nexus.optimization_problem.constraints[1][3] * 1.9438) + "  KCAS / KCAS \n")
    f_write_config.write("Fuel Margin   / Requirement                = " + "%.3f" % (nexus.summary.fuel_margin[0]) + " / " + str(nexus.optimization_problem.constraints[5][3]) +"\n")
    f_write_config.write("Second Segment Gradient / Requirement      = " + "%.3f" % (nexus.summary.second_seg_grad[0][0]) + " / " + str(nexus.optimization_problem.constraints[4][3]) + " deg / deg\n")
    f_write_config.write("Takeoff Convergence                        = " + "%.4f" % (nexus.summary.takeoff_diff) + "\n")
    f_write_config.write("Econ Throttle Max                          = " + "%.2f" % (nexus.summary.max_throttle_econ) + "\n\n")

    print_mission_breakdown(results,'mission_output_econ.txt')




    return f_write_config




if __name__ == '__main__': 
    main()    
    plt.show()