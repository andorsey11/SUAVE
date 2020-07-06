import os
import math
from shutil import copyfile
import subprocess
# This file creates seed geometry for configurations, sets requirements and creates the variables for the optimizer to run. 
import time
from threading import Timer
import random
### Needs more work -- Cruise Mach, # of Wheels, Gear Height


def main():
    # It records all data in a new folder for each combination of payload & range. 
    maxIter = 5
    skip_payload = []
    skip_range   = [2000] # Use this to skip to the one that failed

    tech_string = "Turbofan_Econ_RR"
    payload_array = [50,150,250,350]
    range_array   = [3000]#, 2000, 3000, 4000, 5000, 6000, 7000]
    
    for design_range in range_array:
        for payload in payload_array:
   
            converged = False
            counter = 0
            if(payload in skip_payload and design_range in skip_range):
                continue
                converged = True
            

            folder_string = tech_string + "_" + str(payload) + "_" + str(design_range)


            cwd = os.getcwd()
            config_path = cwd + "/" + folder_string + "/config_overview.txt"


            os.system("rm -r " + folder_string)
            os.system("mkdir " + folder_string)
            while(converged == False):
        # create the new directory for this payload range


                payload_fraction = .2 - .1 * (design_range/8000) # Guess at normal payload fractions
                empty_weight_fraction = .6 - .2 * (design_range/8000) # Another guess
                fuel_fraction = 1 - payload_fraction - empty_weight_fraction
                payload_weight = payload * 220
                kmtow = random.uniform(.7,1.3)

                mtow_guess = payload_weight / payload_fraction * kmtow
                kwing = random.uniform(.7,1.3)
                kthrust = random.uniform(.7,1.3)
                ksweep = random.uniform(.7,1.3)
                ktc = random.uniform(.7,1.3)
                kar = random.uniform(.7,1.3)
                kfpr = random.uniform(.9,1.2)
                wing_loading_guess = 100 + 50 * (mtow_guess / 750000) * kwing
                wing_area_guess = mtow_guess / wing_loading_guess
                cruise_alt_guess = min(27000 + 8000 * (mtow_guess/180000),35000)
                min_cruise_altitude = min(cruise_alt_guess, 22000)
                thrust_guess = mtow_guess * .2  / 1.255 * kthrust
                wing_sweep_guess = 25 * ksweep
                wing_tc_guess = .095 * ktc
                wing_ar_guess = 11 * kar
                fan_pressure_guess = 1.5 * kfpr
                cruise_mach_guess = .74 + .11 * (design_range / 8000)
        # os.mkdir(folder_string)
        #copy the seed files to the new folder

                vehicle_path  = cwd +'/' +folder_string + '/' + 'Vehicles.py' #+ str(payload) + '_' + str(design_range) +'.py'
                seed_vehicle_path = cwd + '/Vehicles.py'
                copyfile(seed_vehicle_path,vehicle_path)

                procedure_path = cwd +'/' +folder_string + '/' + 'Procedure.py'# + str(payload) + '_' + str(design_range) +'.py'
                seed_procedure_path = cwd + '/Procedure.py'
                copyfile(seed_procedure_path,procedure_path)

                opt_path = cwd +'/' +folder_string + '/' + 'Optimize.py'# + str(payload) + '_' + str(design_range) +'.py'
                seed_opt_path = cwd + '/Optimize.py'
                copyfile(seed_opt_path,opt_path)
            
                mission_path = cwd +'/' +folder_string + '/' + 'Missions.py'# + str(payload) + '_' + str(design_range) +'.py'
                seed_mission_path = cwd + '/Missions.py'
                copyfile(seed_mission_path,mission_path)

                analyses_path = cwd +'/' +folder_string + '/' + 'Analyses.py'# + str(payload) + '_' + str(design_range) +'.py'
                seed_analyses_path = cwd + '/Analyses.py'
                copyfile(seed_analyses_path,analyses_path)

                plot_path = cwd +'/' +folder_string + '/' + 'Plot_Mission.py'# + str(payload) + '_' + str(design_range) +'.py'
                seed_plot_path = cwd + '/Plot_Mission.py'
                copyfile(seed_plot_path,plot_path)
            
                f_vehicle   = open(vehicle_path,"w")
                f_procedure = open(procedure_path,"r")
                f_opt       = open(opt_path,"r")
                f_mission   = open(mission_path,"a")
                f_analyses  = open(analyses_path,"a")
                f_plot      = open(plot_path,"a")
                header_vehicle_write(f_vehicle,payload,design_range)
                time.sleep(.3)
                top_level_write(f_vehicle,payload,design_range)
                time.sleep(.3)
                fuselage_write(f_vehicle,payload,design_range)
                time.sleep(.3)
                engine_write(f_vehicle,payload,design_range)
                time.sleep(.3)
                config_write(f_vehicle,payload,design_range)
                f_vehicle.close()

            # Now change things in procedure to match. Only thing we need to change is the design range line and econ range
                procedure_data = f_procedure.readlines()
                if(design_range == 1000): # Econ mission is too short at this range
                    procedure_data[87] = '    mission.design_range = ' + str(design_range) + ' *Units.nautical_miles\n'
                    procedure_data[94] = '    mission.design_range = ' + str(design_range / 2) + ' *Units.nautical_miles\n'
                else:
                    procedure_data[87] = '    mission.design_range = ' + str(design_range) + ' *Units.nautical_miles\n'
                    procedure_data[94] = '    mission.design_range = ' + str(design_range / 3) + ' *Units.nautical_miles\n'

                f_write_procedure = open(procedure_path,"w")
                f_write_procedure.writelines(procedure_data)
                time.sleep(.3)
                f_write_procedure.close()

            # We don't need to change anything in Analyses for standard tech, so don't touch that
            # We dont' need to change anything in Plot Mission for standard tech, so don't touch that

            #Change Optimize.py to give 


                optimize_data = f_opt.readlines()

            #Optimization variables
                optimize_data[72] = "        [ 'wing_area'                    , " + str(wing_area_guess) + " , (   " + str(wing_area_guess * .5) +" , " + str(wing_area_guess*1.7) +" ) , "  + str(wing_area_guess) + " , Units['ft^2']],\n"
                optimize_data[73] = "        [ 'thrust'                       , " + str(thrust_guess)  + "  , (  " + str(thrust_guess * .3)  + " , " + str(thrust_guess * 3)  + " ) ,  " + str(thrust_guess) + " , Units.lbf],\n"
                optimize_data[74] = "        [ 'cruise_altitude'              , " + str(cruise_alt_guess/3.28) + " , ( " +   str(min_cruise_altitude/3.28) + " ,  43000/3.28   ) ,  "  + str(cruise_alt_guess/3.28) + "  , Units.m],\n"
                optimize_data[75] = "        [ 'takeoff_weight_guess'         , " + str(mtow_guess/2.205) + " ,  ( " + str(mtow_guess/2.205*.5) + "  ,   "  + str(mtow_guess/2.205 * 2) + ")   ,   "  + str(mtow_guess/2.205) + " , Units.kg],\n"
                optimize_data[76] = "        [ 'wing_sweep'                   , " +  str(wing_sweep_guess) + "        , (5     ,        45)     ,   "  + str(wing_sweep_guess) + "         , Units.deg],\n"
                optimize_data[77] = "        [ 'wing_toverc'                  , " +  str(wing_tc_guess)    + "        , (.07   ,       .16)     ,     "  + str(wing_tc_guess)    + "    , Units.less],\n"
                optimize_data[78] = "        [ 'wing_aspect_ratio'            , " +  str(wing_ar_guess)    + "        , ( 6    ,         14)    ,     " +   str(wing_ar_guess)   + "   , Units.less],\n"
                optimize_data[79] = "        [ 'econ_takeoff_weight_guess'    , " + str(mtow_guess/2.205*.8) + " ,  ( " + str(mtow_guess/2.205*.3) + "  ,   "  + str(mtow_guess/2.205 * 1.5) + ")   ,   "  + str(mtow_guess/2.205*.8) + " , Units.kg],\n"
           # optimize_data[79] = "        [ 'fan_pressure_ratio'           , " +  str(fan_pressure_guess * .98) + ", ( 1.05 ,        " +  str(fan_pressure_guess) + ")     ,   " +   str(fan_pressure_guess)  +  "  , Units.less],\n"
          #  optimize_data[80] = "        [ 'cruise_mach'                  , " +  str(cruise_mach_guess) +         ", (.50   ,    .88)     , " + str(cruise_mach_guess)  +   "   , Units.less],\n"
            
                if(design_range == 1000): # Restrict the econ mission so it doesnt fly backwards in cruise
                    optimize_data[85] = "        [ 'econ_cruise_altitude'         ,   20000/3.28    , (   10000/3.28   ,    28000/3.28   ) ,   20000/3.28  , Units.m],\n"
                    optimize_data[86] = "        #[ 'econ_cruise_step'             ,   1 / 3.28, (200  ,     4000)   ,     2000/3.28   , Units.m   ]" # Enforces basically no step
                elif(design_range == 2000): # Restrict the econ mission so it doesnt fly backwards in cruise
                    optimize_data[86] = "        #[ 'econ_cruise_step'             ,   1 / 3.28, (200  ,     4000)   ,     2000/3.28   , Units.m   ]" # Enforces basically no step

                approach_req_list = [ [129.66611,   130.79912,  131.978,    133.15382,  134.38559,  135.93143,  137.01593,  138.54269],
                                      [129.85178,   131.14865,  132.52592,  133.87415,  135.69314,  137.25941,  138.563,    139.91582],
                                      [129.98237,   131.43833,  132.96065,  134.36966,  136.38368,  137.96576,  139.2077,   141.11771],
                                      [130.22867,   131.7203,   133.42103,  135.0164,   137.35985,  138.96707,  140.66369,  142.62188],
                                      [130.57,    132.22,  134.03,  135.70,  138.26,  140.32,  141.93,  144.39],
                                       [131.12,   132.77,  135.04,  136.97,  139.32,  141.59,  143.63,  146.18],
                                       [131.65,   133.33,  136.10,  138.27,  140.28,  142.88,  145.10,  148.17]]
                tofl_list  =          [[5481.702,       7218.984,   8187.92,    8450.5198,  8725.6151,  9070.8527,  9313.0577,  9654.0341],
                                       [5766.396,       7754.93,    8310.2888,  8611.3935,  9017.6346,  9367.4349,  9658.57,    9960.6998],
                                       [5966.634,       8199.106,   8407.3785,  8722.0574,  9171.8552,  9525.1864,  9802.553,   10229.1219],
                                       [6344.294,       8130.367,   8510.1967,  8866.496,   9389.8665,  9748.8123,  10127.7241, 10565.0532],
                                       [6872,           8242,       8646,   9020,       9592,   10051,      10410,  10960],
                                       [7714,           8365,       8872,   9303,       9828,   10334,      10789,  11360],
                                       [8115,           8489,       9109,   9594,       10042,  10622,      11119,  11803]]
               
                payload_indice = int((payload / 50) - 1)
                range_indice   = int((design_range/1000)-1)
                approach_req = approach_req_list[range_indice][payload_indice]
                takeoff_req  = tofl_list[range_indice][payload_indice]  


            #Requirements
                optimize_data[106] = "        [ 'approach_speed', '<', " + str(approach_req * .51444) + " , " + str(approach_req * .51444) + " , Units['m/sec']],\n"
                optimize_data[108] = "        [ 'takeoff_field_length', '<', " + str(takeoff_req / 3.28) + " , " + str(takeoff_req / 3.28) + " , Units.m],\n"
            
                f_write_opt = open(opt_path,"w")
                f_write_opt.writelines(optimize_data)
                time.sleep(.3)

                f_write_opt.close()
            #Wait one second
            #Run it

                change_path = cwd + "/" + folder_string
            #os.chdir(change_path)
            #os.system("cd " + cwd +  "/" + folder_string)
                #import pdb; pdb.set_trace()
                try:
                    p = subprocess.Popen(['python3' ,'Optimize.py'], cwd=change_path) # Don't go longer than 30 minutes
                    p.wait()
                except Exception as e:
                  raise e
                if counter == 4:
                    converged = True
                  #  import pdb; pdb.set_trace()
                counter = counter + 1
                os.rename(config_path, config_path + "_" + str(counter))


    return



def header_vehicle_write(vehicle_file,payload,design_range):

             vehicle_file.write("import SUAVE\n")
             vehicle_file.write("import numpy\n")
             vehicle_file.write("from SUAVE.Core import Units\n")
             vehicle_file.write("from SUAVE.Methods.Propulsion.turbofan_sizing import turbofan_sizing\n")
             vehicle_file.write("from SUAVE.Methods.Propulsion.ducted_fan_sizing import ducted_fan_sizing\n\n\n\n") 

             vehicle_file.write("def setup():\n")
    
             vehicle_file.write("    base_vehicle = base_setup()\n")
             vehicle_file.write("    configs = configs_setup(base_vehicle)\n")
    
             vehicle_file.write("    return configs\n\n\n\n\n")

             vehicle_file.write("def base_setup():\n")

             vehicle_file.write("    vehicle = SUAVE.Vehicle()\n")
             vehicle_file.write("    vehicle.tag = 'Turbofan" + str(payload) + "_" + str(design_range)+"'\n\n")    
             return vehicle_file


def top_level_write(vehicle_file,payload,design_range):
            if (payload <= 50):
               abreast = 3
               aisles = 1
            elif(payload <= 100):
               abreast = 4
               aisles = 1
            elif(payload <= 140):
               abreast = 5
               aisles = 1
            elif(payload <= 210):
               abreast = 6
               aisles = 1
            elif(payload <= 280):
               abreast = 8
               aisles = 2
            elif(payload <= 350):
               abreast = 9
               aisles = 2
            elif(payload > 350):
               abreast = 10
               aisles = 2                                    
            seat_pitch = 34
            fuselage_width = 18 * abreast * 1.2 + 24 * aisles   #Gives outter diameter in inches
            fuselage_cabin_length = seat_pitch * payload / abreast     # gives cabin assumign 34 inch pitch average
            nose_fineness = 2
            tail_fineness = 3
            nose_length = nose_fineness * fuselage_width          # Inches
            tail_length = tail_fineness * fuselage_width          # Inches
            fuselage_length = fuselage_cabin_length + nose_length + tail_length    #Inches
            fuselage_height = fuselage_width ## just assume its a circle
             #Take a guess at mtow
            payload_fraction = .2 - .1 * (design_range/8000) # Guess at normal payload fractions
            empty_weight_fraction = .6 - .2 * (design_range/8000) # Another guess
            fuel_fraction = 1 - payload_fraction - empty_weight_fraction
            payload_weight = payload * 220
            mtow_guess = payload_weight / payload_fraction
            oew_guess = empty_weight_fraction * mtow_guess
            vehicle_file.write("    vehicle.mass_properties.max_takeoff = " + str(mtow_guess) + " * Units.lbs \n")
            vehicle_file.write("    vehicle.mass_properties.takeoff  = " + str(mtow_guess) + " * Units.lbs \n")                  
            vehicle_file.write("    vehicle.mass_properties.operating_empty = " + str(oew_guess) + " * Units.lbs \n")  
            vehicle_file.write("    vehicle.mass_properties.max_zero_fuel  = " + str(oew_guess + payload_weight) + " * Units.lbs \n")  
            vehicle_file.write("    vehicle.mass_properties.cargo = 0.  * Units.kilogram\n") 
            vehicle_file.write("    vehicle.mass_properties.econ_takeoff = " + str(mtow_guess * .8) + " * Units.lbs \n")

            # envelope properties
            vehicle_file.write("    vehicle.envelope.ultimate_load = 2.5\n")
            vehicle_file.write("    vehicle.envelope.limit_load    = 1.5\n")

             # basic parameters
            wing_loading_guess = 100 + 50 * (mtow_guess / 750000)
            vehicle_file.write("    vehicle.reference_area         = " + str(mtow_guess/wing_loading_guess) + "  * Units['feet**2']\n")
            vehicle_file.write("    vehicle.passengers             = " + str(payload) + "\n")

            vehicle_file.write('    vehicle.systems.control        = "fully powered" \n')
            if (design_range <= 2000):
                range_str = '"short range"'
            elif(design_range <= 4000):
                range_str = '"medium range"'
            else:
                range_str = '"long range"'        
            vehicle_file.write("    vehicle.systems.accessories    = " + range_str + " \n")

            cruise_alt_guess = min(27000 + 8000 * (mtow_guess/180000),35000)
            vehicle_file.write("    vehicle.cruise_altitude    = " + str(cruise_alt_guess) + " \n")
            vehicle_file.write("    vehicle.cruise_step        = 2000 / 3.28 * Units.m \n")
             #Add module for cruise mach here

            mach_req = .73 + .13 * (design_range/8000)
            vehicle_file.write("    vehicle.cruise_mach        =" + str(mach_req) +" \n\n\n\n")
            vehicle_file.write("    landing_gear = SUAVE.Components.Landing_Gear.Landing_Gear()\n")
            vehicle_file.write('    landing_gear.tag = "main_landing_gear"\n\n')
            ## Add regression for # of wheels
            if (mtow_guess >= 300000):
                num_Wheels = 4 # Per gear
            elif(mtow_guess >= 600000):
                num_Wheels = 6
            elif(mtow_guess >= 900000):
                num_Wheels = 8
            else:
                num_Wheels = 2
            main_units = 2
            nose_units = 1    
            vehicle_file.write("    landing_gear.main_units  = " + str(main_units) + "\n")
            vehicle_file.write("    landing_gear.nose_units  = " + str(nose_units) + "\n")
            vehicle_file.write("    landing_gear.main_wheels = " + str(num_Wheels) + "\n")
            vehicle_file.write("    landing_gear.nose_wheels = " + str(num_Wheels/2) + "\n")


            main_tire_diameter = 1.63 * (mtow_guess * .9 / (main_units * num_Wheels))**.315  # Raymer Jet Transport D(in) = A * weight ^ B A =1.63 B = .315
            nose_tire_diameter = 1.63 * (mtow_guess * .1)**.315   # Raymer Jet Transport Width(in) = A * weight ^ B A = .1043 B = .480
            required_tail_scrape = 12 # Degrees
            main_strut_length = fuselage_length *.25 * math.sin(math.radians(required_tail_scrape)) # 12 degree static tail scrape angle
            vehicle_file.write("    landing_gear.main_strut_length  = " + str(main_strut_length) + " * Units.inches\n")
            vehicle_file.write("    landing_gear.nose_strut_length  = " + str(main_strut_length) + " * Units.inches\n")
            vehicle_file.write("    landing_gear.main_tire_diameter = " + str(main_tire_diameter) + " * Units.inches\n")
            vehicle_file.write("    landing_gear.nose_tire_diameter = " + str(nose_tire_diameter) + " * Units.inches\n")     
            vehicle_file.write("    vehicle.landing_gear = landing_gear\n\n\n")



            vehicle_file.write("    wing = SUAVE.Components.Wings.Main_Wing()\n")
            vehicle_file.write("    wing.tag = 'main_wing'\n")
            vehicle_file.write("    wing.areas.reference         = " + str(mtow_guess / wing_loading_guess) + " * Units['feet**2']\n") # Design variable 
            vehicle_file.write("    wing.aspect_ratio            = 11\n") # Design variable. Initial guess here
            vehicle_file.write("    wing.sweeps.quarter_chord    = 26 * Units.deg\n") # Design variable, initial guess
            vehicle_file.write("    wing.sweeps.leading_edge     = 26 * Units.deg\n") # Design variable, initial guess
            vehicle_file.write("    wing.sweeps.trailing_edge    = 26 * Units.deg\n") # Design variable, initial guess
            vehicle_file.write("    wing.thickness_to_chord      = 0.095\n") #Design variable, initial guess
            vehicle_file.write("    wing.taper                   = 0.1\n") 
            vehicle_file.write("    wing.span_efficiency         = 0.95\n") # Inviscid e
            vehicle_file.write("    wing.yehudi_factor           = 1.2\n") # Factor to capture extra root chord due to yehudi, 1.2 good for low wing, close to 1 for high wing
            vehicle_file.write("    wing.spans.projected         = numpy.sqrt(wing.aspect_ratio * wing.areas.reference)\n")
            vehicle_file.write("    wing.chords.root             = wing.yehudi_factor * 2 * wing.areas.reference / wing.spans.projected / (1+wing.taper)\n")   #A = .5 * [ ct + cr ] * s 
            vehicle_file.write("    wing.chords.tip              = wing.chords.root * wing.taper\n")
            vehicle_file.write("    wing.chords.mean_aerodynamic = wing.chords.root - (2*(wing.chords.root-wing.chords.tip)*(.5*wing.chords.root+wing.chords.tip)/(3*(wing.chords.root+wing.chords.tip)))\n")   #A-(2(A-B)(0.5A+B) / (3(A+B))) http://www.nasascale.org/p2/wp-content/uploads/mac-calculator.htm
            vehicle_file.write("    wing.twists.root             = 2 * Units.degrees\n")
            vehicle_file.write("    wing.twists.tip              = 0.0 * Units.degrees\n")
            wing_origin_x = fuselage_length * .48
            wing_origin_z = fuselage_height *-.25
            vehicle_file.write("    wing.origin                  = [" + str(wing_origin_x*.0254) + "," + str(0) + "," + str(wing_origin_z*.0254) + "]# meters\n")
            vehicle_file.write("    wing.vertical                = False\n")
            vehicle_file.write("    wing.symmetric               = True\n")
            vehicle_file.write("    wing.high_lift               = True\n")
            vehicle_file.write("    wing.dynamic_pressure_ratio  = 1.08\n")
            vehicle_file.write("    wing.fuel_volume             = (wing.thickness_to_chord * wing.chords.root * wing.chords.root*(.4) + wing.thickness_to_chord* wing.chords.tip * wing.chords.tip*.4) / 2 *wing.spans.projected* .9 * .7\n") # 70% span, 10% stringer and skin knockdown, average x-sec * span
            vehicle_file.write("    wing.origin_factor             = 0.4 \n\n\n") # 70% span, 10% stringer and skin knockdown, average x-sec * span

    #import pdb; pdb.set_trace()
    # ------------------------------------------------------------------
    #   Flaps
    # ------------------------------------------------------------------
            vehicle_file.write("    wing.flaps.chord      =  0.30\n")   # 30% of the chord
            vehicle_file.write("    wing.flaps.span_start =  0.10\n")   # 10% of the span
            vehicle_file.write("    wing.flaps.span_end   =  0.75\n")
            vehicle_file.write("    wing.flaps.type       = 'double_slotted'\n")
            vehicle_file.write("    vehicle.append_component(wing)\n\n\n\n\n\n")
   # ------------------------------------------------------------------        
    #  Horizontal Stabilizer
    # ------------------------------------------------------------------        
            vehicle_file.write("    wing = SUAVE.Components.Wings.Wing()\n")
            vehicle_file.write("    wing.tag = 'horizontal_stabilizer'\n")
            vehicle_file.write("    wing.yehudi_factor           = 1.0\n")  
            vehicle_file.write("    wing.areas.reference         = " + str(mtow_guess/wing_loading_guess * .25) + " * Units['feet**2']\n") # Resized in loop, need initial guess     
            vehicle_file.write("    wing.aspect_ratio            = 6  \n")     
            vehicle_file.write("    wing.sweeps.quarter_chord    = 40 * Units.deg\n")
            vehicle_file.write("    wing.thickness_to_chord      = 0.08\n")
            vehicle_file.write("    wing.taper                   = 0.2\n")
            vehicle_file.write("    wing.span_efficiency         = 0.9\n")
            vehicle_file.write("    wing.spans.projected         = numpy.sqrt(wing.aspect_ratio * wing.areas.reference)\n")
            vehicle_file.write("    wing.chords.root             = wing.yehudi_factor * 2 * wing.areas.reference / wing.spans.projected / (1+wing.taper)\n")   #A = .5 * [ ct + cr ] * s 
            vehicle_file.write("    wing.chords.tip              = wing.chords.root * wing.taper\n")
            vehicle_file.write("    wing.chords.mean_aerodynamic = wing.chords.root - (2*(wing.chords.root-wing.chords.tip)*(.5*wing.chords.root+wing.chords.tip)/(3*(wing.chords.root+wing.chords.tip)))\n")   #A-(2(A-B)(0.5A+B) / (3(A+B))) http://www.nasascale.org/p2/wp-content/uploads/mac-calculator.htm
            vehicle_file.write("    wing.origin                  = [" + str(fuselage_length*.9*.0254) + ",0," + str(fuselage_height*.75*.0254) + "]\n")
            vehicle_file.write("    wing.vertical                = False\n") 
            vehicle_file.write("    wing.symmetric               = True\n")
            vehicle_file.write("    wing.dynamic_pressure_ratio  = 0.9\n")  
            # add to vehicle
            vehicle_file.write("    vehicle.append_component(wing)\n\n\n\n\n\n")
    
    # ------------------------------------------------------------------
    #   Vertical Stabilizer
    # ------------------------------------------------------------------
    
            vehicle_file.write("    wing = SUAVE.Components.Wings.Wing()\n")
            vehicle_file.write("    wing.tag = 'vertical_stabilizer'\n")    
            vehicle_file.write("    wing.yehudi_factor           = 1\n")
            vehicle_file.write("    wing.areas.reference         = " + str(mtow_guess/wing_loading_guess * .2) + " * Units['feet**2']\n")  # Reszed in loop, needs decent first guess
            vehicle_file.write("    wing.aspect_ratio            = 2\n")
            vehicle_file.write("    wing.sweeps.quarter_chord    = 25. * Units.deg\n")
            vehicle_file.write("    wing.thickness_to_chord      = 0.08\n")
            vehicle_file.write("    wing.taper                   = 0.25\n")
            vehicle_file.write("    wing.span_efficiency         = 0.9\n")
            vehicle_file.write("    wing.spans.projected         = numpy.sqrt(wing.aspect_ratio * wing.areas.reference)\n")
            vehicle_file.write("    wing.chords.root             = wing.yehudi_factor * 2 * wing.areas.reference / wing.spans.projected / (1+wing.taper)\n")   #A = .5 * [ ct + cr ] * s 
            vehicle_file.write("    wing.chords.tip              = wing.chords.root * wing.taper\n")
            vehicle_file.write("    wing.chords.mean_aerodynamic = wing.chords.root - (2*(wing.chords.root-wing.chords.tip)*(.5*wing.chords.root+wing.chords.tip)/(3*(wing.chords.root+wing.chords.tip)))\n")   #A-(2(A-B)(0.5A+B) / (3(A+B))) http://www.nasascale.org/p2/wp-content/uploads/mac-calculator.htm
            vehicle_file.write("    wing.twists.root             = 0.0 * Units.degrees\n")
            vehicle_file.write("    wing.twists.tip              = 0.0 * Units.degrees\n")  
            vehicle_file.write("    wing.origin                  = [" + str(fuselage_length*.85 * .0254) + ",0," + str(fuselage_height*.85 * .0254) + "]\n")
            vehicle_file.write("    wing.vertical                = True\n") 
            vehicle_file.write("    wing.symmetric               = False\n")
            vehicle_file.write("    wing.t_tail                  = False\n")
            vehicle_file.write("    wing.dynamic_pressure_ratio  = 1.0\n")
            vehicle_file.write("    wing.q_cl_vertical           = 2000\n") #Constant variable of maximum tail Cl at engine failure speed to size tail according to thrust      
            # add to vehicle
            vehicle_file.write("    vehicle.append_component(wing)\n\n\n\n\n\n")






            return vehicle_file

def config_write(vehicle_file, payload, design_range):
            payload_fraction = .2 - .1 * (design_range/8000) # Guess at normal payload fractions
            empty_weight_fraction = .6 - .2 * (design_range/8000) # Another guess
            fuel_fraction = 1 - payload_fraction - empty_weight_fraction
            payload_weight = payload * 220
            mtow_guess = payload_weight / payload_fraction
## Write the config definitions
            vehicle_file.write("def configs_setup(vehicle):\n\n")
    
    # ------------------------------------------------------------------
    #   Initialize Configurations
    # ------------------------------------------------------------------

            vehicle_file.write("    configs = SUAVE.Components.Configs.Config.Container()\n\n")

            vehicle_file.write("    base_config = SUAVE.Components.Configs.Config(vehicle)\n")
            vehicle_file.write("    base_config.tag = 'base'\n")
            vehicle_file.write("    configs.append(base_config)\n\n")

    ## Econ Config

            vehicle_file.write("    config = SUAVE.Components.Configs.Config(base_config)\n\n")
            vehicle_file.write("    config.tag = 'econ'\n")
            vehicle_file.write("    config.mass_properties.takeoff = " + str(mtow_guess * .8)+ "* Units.lbs\n\n")
            vehicle_file.write("    config.cruise_altitude = 25000 * Units.ft\n")
            vehicle_file.write("    config.cruise_step = 1/3.28 * Units.m\n")
            vehicle_file.write("    configs.append(config)\n\n")


    # ------------------------------------------------------------------
    #   Cruise Configuration
    # ------------------------------------------------------------------

            vehicle_file.write("    config = SUAVE.Components.Configs.Config(base_config)\n")
            vehicle_file.write("    config.tag = 'cruise'\n\n")

            vehicle_file.write("    configs.append(config)\n\n")
    
            vehicle_file.write("    config.maximum_lift_coefficient = 1.2\n\n")

            vehicle_file.write("    config = SUAVE.Components.Configs.Config(base_config)\n")
            vehicle_file.write("    config.tag = 'takeoff'\n\n")

            vehicle_file.write("    config.wings['main_wing'].flaps.angle = 20. * Units.deg\n")
            vehicle_file.write("    config.wings['main_wing'].slats.angle = 25. * Units.deg\n\n")

            vehicle_file.write("    config.V2_VS_ratio = 1.21\n")
            vehicle_file.write("    config.maximum_lift_coefficient = 2.\n\n")

            vehicle_file.write("    configs.append(config)\n\n")

    # ------------------------------------------------------------------
    #   Landing Configuration
    # ------------------------------------------------------------------

            vehicle_file.write("    config = SUAVE.Components.Configs.Config(base_config)\n")
            vehicle_file.write("    config.tag = 'landing'\n\n")

            vehicle_file.write("    config.wings['main_wing'].flaps_angle = 30. * Units.deg\n")
            vehicle_file.write("    config.wings['main_wing'].slats_angle = 25. * Units.deg\n")

            vehicle_file.write("    config.Vref_VS_ratio = 1.23\n")
            vehicle_file.write("    config.maximum_lift_coefficient = 2.6\n")

            vehicle_file.write("    configs.append(config)\n\n")
    
    # ------------------------------------------------------------------
    #   Short Field Takeoff Configuration
    # ------------------------------------------------------------------ 

            vehicle_file.write("    config = SUAVE.Components.Configs.Config(base_config)\n")
            vehicle_file.write("    config.tag = 'short_field_takeoff'\n\n")
    
            vehicle_file.write("    config.wings['main_wing'].flaps.angle = 20. * Units.deg\n")
            vehicle_file.write("    config.wings['main_wing'].slats.angle = 25. * Units.deg\n")

            vehicle_file.write("    config.V2_VS_ratio = 1.21\n")
            vehicle_file.write("    config.maximum_lift_coefficient = 2. \n")
    
            vehicle_file.write("    configs.append(config)\n")

            vehicle_file.write("    return configs\n")


            return vehicle_file





def engine_write(vehicle_file,payload,design_range):
  # ------------------------------------------------------------------
    #  Turbofan Network
    # ------------------------------------------------------------------    

            payload_fraction = .2 - .1 * (design_range/8000) # Guess at normal payload fractions
            empty_weight_fraction = .6 - .2 * (design_range/8000) # Another guess
            fuel_fraction = 1 - payload_fraction - empty_weight_fraction
            payload_weight = payload * 220
            mtow_guess = payload_weight / payload_fraction

    #initialize the gas turbine network
            vehicle_file.write("    gt_engine                   = SUAVE.Components.Energy.Networks.Turbofan()\n")
            vehicle_file.write("    gt_engine.tag               = 'turbofan'\n\n")

            vehicle_file.write("    gt_engine.number_of_engines = 2.0\n")
            vehicle_file.write("    gt_engine.bypass_ratio      = 7\n") # Design variable. Initial guess
            vehicle_file.write("    gt_engine.engine_length     = 2.71\n") #Resized down below, doesn't matter
            vehicle_file.write("    gt_engine.nacelle_diameter  = 2.05\n\n") # ''
            vehicle_file.write("    gt_engine.bypass_factor     = 1\n\n") # ''

    #set the working fluid for the network
            vehicle_file.write("    gt_engine.working_fluid = SUAVE.Attributes.Gases.Air()\n\n")


    #Component 1 : ram,  to convert freestream static to stagnation quantities
            vehicle_file.write("    ram = SUAVE.Components.Energy.Converters.Ram()\n")
            vehicle_file.write("    ram.tag = 'ram'\n\n")

    #add ram to the network
            vehicle_file.write("    gt_engine.ram = ram\n\n")

    #Component 2 : inlet nozzle
            vehicle_file.write("    inlet_nozzle = SUAVE.Components.Energy.Converters.Compression_Nozzle()\n")
            vehicle_file.write("    inlet_nozzle.tag = 'inlet nozzle'\n\n")

            vehicle_file.write("    inlet_nozzle.polytropic_efficiency = 0.98\n")
            vehicle_file.write("    inlet_nozzle.pressure_ratio        = 0.98\n\n")

    #add inlet nozzle to the network
            vehicle_file.write("    gt_engine.inlet_nozzle = inlet_nozzle\n\n")

    #Component 3 :low pressure compressor    
            vehicle_file.write("    low_pressure_compressor = SUAVE.Components.Energy.Converters.Compressor()\n")    
            vehicle_file.write("    low_pressure_compressor.tag = 'lpc'\n\n")

            vehicle_file.write("    low_pressure_compressor.polytropic_efficiency = 0.91\n")
            vehicle_file.write("    low_pressure_compressor.pressure_ratio        = 1.9\n\n")    

    #add low pressure compressor to the network    
            vehicle_file.write("    gt_engine.low_pressure_compressor = low_pressure_compressor\n\n")

    #Component 4: high pressure compressor  
            vehicle_file.write("    high_pressure_compressor = SUAVE.Components.Energy.Converters.Compressor()\n")    
            vehicle_file.write("    high_pressure_compressor.tag = 'hpc'\n\n")

            vehicle_file.write("    high_pressure_compressor.polytropic_efficiency = 0.91\n")
            vehicle_file.write("    high_pressure_compressor.pressure_ratio        = 10.0\n\n")   

    #add the high pressure compressor to the network    
            vehicle_file.write("    gt_engine.high_pressure_compressor = high_pressure_compressor\n")

    #Component 5 :low pressure turbine  
            vehicle_file.write("    low_pressure_turbine = SUAVE.Components.Energy.Converters.Turbine()\n")   
            vehicle_file.write("    low_pressure_turbine.tag='lpt'\n\n")

            vehicle_file.write("    low_pressure_turbine.mechanical_efficiency = 0.99\n")
            vehicle_file.write("    low_pressure_turbine.polytropic_efficiency = 0.93\n\n")

    #add low pressure turbine to the network    
            vehicle_file.write("    gt_engine.low_pressure_turbine = low_pressure_turbine\n\n")

    #Component 5 :high pressure turbine  
            vehicle_file.write("    high_pressure_turbine = SUAVE.Components.Energy.Converters.Turbine()\n")   
            vehicle_file.write("    high_pressure_turbine.tag='hpt'\n\n")

            vehicle_file.write("    high_pressure_turbine.mechanical_efficiency = 0.99\n")
            vehicle_file.write("    high_pressure_turbine.polytropic_efficiency = 0.93\n\n")

    #add the high pressure turbine to the network    
            vehicle_file.write("    gt_engine.high_pressure_turbine = high_pressure_turbine\n\n") 

    #Component 6 :combustor  
            vehicle_file.write("    combustor = SUAVE.Components.Energy.Converters.Combustor()\n")   
            vehicle_file.write("    combustor.tag = 'Comb'\n\n")

            vehicle_file.write("    combustor.efficiency                = 0.99 \n")
            vehicle_file.write("    combustor.alphac                    = 1.0     \n")
            vehicle_file.write("    combustor.turbine_inlet_temperature = 1500\n")
            vehicle_file.write("    combustor.pressure_ratio            = 0.95\n")
            vehicle_file.write("    combustor.fuel_data                 = SUAVE.Attributes.Propellants.Jet_A() \n\n")   

    #add the combustor to the network    
            vehicle_file.write("    gt_engine.combustor = combustor\n\n")

    #Component 7 :core nozzle
            vehicle_file.write("    core_nozzle = SUAVE.Components.Energy.Converters.Expansion_Nozzle()\n")   
            vehicle_file.write("    core_nozzle.tag = 'core nozzle'\n\n")

            vehicle_file.write("    core_nozzle.polytropic_efficiency = 0.95\n")
            vehicle_file.write("    core_nozzle.pressure_ratio        = 0.99\n\n")    

    #add the core nozzle to the network    
            vehicle_file.write("    gt_engine.core_nozzle = core_nozzle\n\n")

    #Component 8 :fan nozzle
            vehicle_file.write("    fan_nozzle = SUAVE.Components.Energy.Converters.Expansion_Nozzle()\n")   
            vehicle_file.write("    fan_nozzle.tag = 'fan nozzle'\n\n")

            vehicle_file.write("    fan_nozzle.polytropic_efficiency = 0.95\n")
            vehicle_file.write("    fan_nozzle.pressure_ratio        = 0.99\n\n")

    #add the fan nozzle to the network
            vehicle_file.write("    gt_engine.fan_nozzle = fan_nozzle\n\n")

    #Component 9 : fan   
            vehicle_file.write("    fan = SUAVE.Components.Energy.Converters.Fan()\n")   
            vehicle_file.write("    fan.tag = 'fan'\n\n")

            vehicle_file.write("    fan.polytropic_efficiency = 0.93\n")
            vehicle_file.write("    fan.pressure_ratio        = 1.7\n") # Design variable
            vehicle_file.write("    fan.spinner_ratio         = 1.2 \n")
            vehicle_file.write("    fan.nacelle_length_to_fan_di = 1.6\n\n")


    #add the fan to the network
            vehicle_file.write("    gt_engine.fan = fan\n\n")    

    #Component 10 : thrust (to compute the thrust)
            vehicle_file.write("    thrust = SUAVE.Components.Energy.Processes.Thrust()\n\n")       
            vehicle_file.write("    thrust.tag ='compute_thrust'\n")

    #total design thrust (includes all the engines)
            vehicle_file.write("    thrust.total_design             = " + str(mtow_guess * .2 * 2 / 1.255) + " * Units.lbf\n\n") # Design variable. First guess
 
    #design sizing conditions
            vehicle_file.write("    altitude      = 0.0*Units.ft\n")
            vehicle_file.write("    mach_number   = 0.25 \n")
            vehicle_file.write("    isa_deviation = 0.\n\n")

    # add thrust to the network
            vehicle_file.write("    gt_engine.thrust = thrust\n\n")

    #size the turbofan
            vehicle_file.write("    turbofan_sizing(gt_engine,mach_number,altitude,isa_deviation)\n\n")   
    #ducted_fan_sizing(gt_engine,mach_number,altitude,isa_deviation)
    # add  gas turbine network gt_engine to the vehicle
            vehicle_file.write("    vehicle.append_component(gt_engine)\n\n")      
    #now add weights objects
            vehicle_file.write("    vehicle.landing_gear       = SUAVE.Components.Landing_Gear.Landing_Gear()\n")
            vehicle_file.write("    vehicle.control_systems    = SUAVE.Components.Physical_Component()\n")
            vehicle_file.write("    vehicle.electrical_systems = SUAVE.Components.Physical_Component()\n")
            vehicle_file.write("    vehicle.avionics           = SUAVE.Components.Energy.Peripherals.Avionics()\n")
            vehicle_file.write("    vehicle.passenger_weights  = SUAVE.Components.Physical_Component()\n")
            vehicle_file.write("    vehicle.furnishings        = SUAVE.Components.Physical_Component()\n")
            vehicle_file.write("    vehicle.air_conditioner    = SUAVE.Components.Physical_Component()\n")
            vehicle_file.write("    vehicle.fuel               = SUAVE.Components.Physical_Component()\n")
            vehicle_file.write("    vehicle.apu                = SUAVE.Components.Physical_Component()\n")
            vehicle_file.write("    vehicle.hydraulics         = SUAVE.Components.Physical_Component()\n")
            vehicle_file.write("    vehicle.optionals          = SUAVE.Components.Physical_Component()\n")
            vehicle_file.write("    vehicle.wings['vertical_stabilizer'].rudder = SUAVE.Components.Physical_Component()\n\n\n\n\n")
            vehicle_file.write("    return vehicle\n\n")

    # ------------------------------------------------------------------
    #   Vehicle Definition Complete
    # ------------------------------------------------------------------

            return vehicle_file







def fuselage_write(vehicle_file,payload,design_range):

            if (payload <= 50):
               abreast = 3
               aisles = 1
            elif(payload <= 100):
               abreast = 4
               aisles = 1
            elif(payload <= 140):
               abreast = 5
               aisles = 1
            elif(payload <= 210):
               abreast = 6
               aisles = 1
            elif(payload <= 280):
               abreast = 8
               aisles = 2
            elif(payload <= 350):
               abreast = 9
               aisles = 2
            elif(payload > 350):
               abreast = 10
               aisles = 2                                    
            seat_pitch = 34
            fuselage_width = 18 * abreast * 1.2 + 24 * aisles   #Gives outter diameter in inches
            fuselage_cabin_length = seat_pitch * payload / abreast     # gives cabin assumign 34 inch pitch average
            fuselage_height = fuselage_width ## just assume its a circle

            nose_fineness = 2
            tail_fineness = 3

            nose_length = nose_fineness * fuselage_width          # Inches
            tail_length = tail_fineness * fuselage_width          # Inches
            fuselage_length = fuselage_cabin_length + nose_length + tail_length    #Inches
            fuselage_differential_pressure = 5.0e4   #* Units.pascal # Maximum differential pressure

            vehicle_file.write("    fuselage = SUAVE.Components.Fuselages.Fuselage()\n")
            vehicle_file.write("    fuselage.tag = 'fuselage'\n")
            vehicle_file.write("    fuselage.number_coach_seats      = vehicle.passengers\n")
            vehicle_file.write("    fuselage.seats_abreast           = " + str(abreast)+"\n")
            vehicle_file.write("    fuselage.seat_pitch              = " + str(seat_pitch * .0254) + " * Units.meter\n")
            vehicle_file.write("    fuselage.fineness.nose           = " + str(nose_fineness) + "\n")
            vehicle_file.write("    fuselage.fineness.tail           = " + str(tail_fineness) + "\n")
            vehicle_file.write("    fuselage.lengths.nose            = " + str(nose_length * .0254) + " * Units.meter \n")
            vehicle_file.write("    fuselage.lengths.tail            = " + str(tail_length * .0254) + " * Units.meter \n")
            vehicle_file.write("    fuselage.lengths.cabin           = " + str(fuselage_cabin_length * .0254) + " * Units.meter \n")
            vehicle_file.write("    fuselage.lengths.total           = " + str(fuselage_length * .0254) + " * Units.meter \n")
            vehicle_file.write("    fuselage.lengths.fore_space      = " + str(nose_length * .8 * .0254) +  " * Units.meter \n")
            vehicle_file.write("    fuselage.lengths.aft_space       = " + str(tail_length * .8 * .0254) + " * Units.meter \n")
            vehicle_file.write("    fuselage.width                   = " + str(fuselage_width * .0254) + " * Units.meter\n")
            vehicle_file.write("    fuselage.heights.maximum         = " + str(fuselage_height * .0254) + " * Units.meter\n")
            vehicle_file.write("    fuselage.effective_diameter      = " + str(fuselage_width * .0254) + " * Units.meter \n")
            vehicle_file.write("    fuselage.areas.side_projected    = fuselage.width * fuselage.lengths.total *  Units['meters**2']\n")
            vehicle_file.write("    fuselage.areas.wetted            = 2*3.14*fuselage.width/2*(fuselage.lengths.cabin+(fuselage.lengths.total - fuselage.lengths.cabin)*.5)  * Units['meters**2']\n")
            vehicle_file.write("    fuselage.areas.front_projected   = fuselage.width / 2 * fuselage.width / 2 * 3.14 * Units['meters**2']\n")
            vehicle_file.write("    fuselage.differential_pressure   = 5.0e4 * Units.pascal\n")
            vehicle_file.write("    fuselage.heights.at_quarter_length = " + str(fuselage_height * .0254) + " * Units.meter\n")
            vehicle_file.write("    fuselage.heights.at_three_quarters_length = " + str(fuselage_height * .0254) + " * Units.meter\n")
            vehicle_file.write("    fuselage.heights.at_wing_root_quarter_chord = " + str(fuselage_height * .0254) + "* Units.meter\n")
            vehicle_file.write("    vehicle.append_component(fuselage)\n\n\n\n\n\n\n")

            return vehicle_file




if __name__ == '__main__':
    main()



