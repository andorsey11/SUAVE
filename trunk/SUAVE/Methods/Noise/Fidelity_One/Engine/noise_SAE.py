#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      CARIDSIL
#
# Created:     26/06/2015

# Licence:     <your licence>
#-------------------------------------------------------------------------------

import numpy as np
from SUAVE.Core            import Units

from angle_of_attack_effect import angle_of_attack_effect
from external_plug_effect import external_plug_effect
from ground_proximity_effect import ground_proximity_effect
from jet_installation_effect import jet_installation_effect
from mixed_noise_component import mixed_noise_component
from noise_source_location import noise_source_location
from primary_noise_component import primary_noise_component
from secondary_noise_component import secondary_noise_component


from SUAVE.Methods.Noise.Fidelity_One.Noise_Tools import pnl_noise
from SUAVE.Methods.Noise.Fidelity_One.Noise_Tools import noise_tone_correction
from SUAVE.Methods.Noise.Fidelity_One.Noise_Tools import epnl_noise


def noise_SAE (turbofan,trajectory,configs,analyses):

    #SAE ARP*876D 1994
    """This method predicts the free-field 1/3 Octave Band SPL of coaxial subsonic
    jets for turbofan engines under the following conditions:
        a) Flyover (observer on ground)
        b) Static (observer on ground)
        c) In-flight or in-flow (observer on airplane or in a wind tunnel)

        Inputs:
                    vehicle	 - SUAVE type vehicle

                    includes these fields:
                        Velocity_primary           - Primary jet flow velocity
                        Temperature_primary        - Primary jet flow temperature
                        Pressure_primary           - Primary jet flow pressure
                        Area_primary               - Area of the primary nozzle
                        Velocity_secondary         - Secondary jet flow velocity
                        Temperature_secondary      - Secondary jet flow temperature
                        Pressure_secondary         - Secondary jet flow pressure
                        Area_secondary             - Area of the secondary nozzle
                        AOA                        - Angle of attack
                        Velocity_aircraft          - Aircraft velocity
                        Altitute                   - Altitude
                        N1                         - Fan rotational speed [rpm]
                        EXA                        - Distance from fan face to fan exit/ fan diameter
                        Plug_diameter              - Diameter of the engine external plug [m]
                        Engine_height              - Engine centerline height above the ground plane
                        distance_microphone        - Distance from the nozzle exhaust to the microphones
                        angles                     - Array containing the desired polar angles


                    airport   - SUAVE type airport data, with followig fields:
                        atmosphere                  - Airport atmosphere (SUAVE type)
                        altitude                    - Airport altitude
                        delta_isa                   - ISA Temperature deviation


                Outputs: One Third Octave Band SPL [dB]
                    SPL_p                           - Sound Pressure Level of the primary jet
                    SPL_s                           - Sound Pressure Level of the secondary jet
                    SPL_m                           - Sound Pressure Level of the mixed jet
                    SPL_total                       - Sound Pressure Level of the total jet noise

                Assumptions:
                    ."""


    #unpack
##    Velocity_primary        =       np.float(turbofan.core_nozzle.outputs.velocity)
##    Temperature_primary     =       np.float(turbofan.core_nozzle.outputs.stagnation_temperature)
##    Pressure_primary        =       np.float(turbofan.core_nozzle.outputs.stagnation_pressure)
##    
##    Velocity_secondary      =       np.float(turbofan.fan_nozzle.outputs.velocity)
##    Temperature_secondary   =       np.float(turbofan.fan_nozzle.outputs.stagnation_temperature)
##    Pressure_secondary      =       np.float(turbofan.fan_nozzle.outputs.stagnation_pressure)

    #Changed August 4th
    Velocity_primary        =       trajectory[:][5][0]
    Temperature_primary     =       trajectory[:][5][1]
    Pressure_primary        =       trajectory[:][5][2]
    
    Velocity_secondary      =       trajectory[:][5][3]
    Temperature_secondary   =       trajectory[:][5][4]
    Pressure_secondary      =       trajectory[:][5][5]
    
    Velocity_aircraft= configs.flight.velocity
    Altitude = trajectory[:][1]
    AOA = configs.flight.angle_of_attack
    
    
    Velocity_aircraft= configs.flight.velocity
    Altitude = trajectory[:][1]
    AOA = configs.flight.angle_of_attack
    
    angles=trajectory[:][3]
    distance_microphone=trajectory[:][2]
    time=trajectory[:][0]
    phi=trajectory[:][4]
    
    nsteps=len(time)
    
    
    N1=np.float(turbofan.fan.rotation)
    
    #Mudan?a 03 de Agosto
    sound_ambient=np.zeros(nsteps)
    density_ambient=np.zeros(nsteps)
    viscosity=np.zeros(nsteps)
    temperature_ambient=np.zeros(nsteps)
    pressure_amb=np.zeros(nsteps)
    Mach_aircraft=np.zeros(nsteps)
    
     # ==============================================
        # Computing atmospheric conditions
    # ==============================================
    
    for id in range (0,nsteps):
        atmo_data = analyses.atmosphere.compute_values(Altitude[id])
    
        sound_ambient[id] =    np.float(atmo_data.speed_of_sound)
        density_ambient[id] =       np.float(atmo_data.density)
        viscosity[id] =     np.float(atmo_data.dynamic_viscosity)
        temperature_ambient[id] =   np.float(atmo_data.temperature)
        pressure_amb[id] = np.float(atmo_data.pressure)
    
    #Necessary input for the code
  #  pressure_amb=997962 #[Pa]
    pressure_isa=101325 #[Pa]
    R_gas=287.1         #[J/kg K]
    gama_primary=1.37 #Corretion for the primary jet
    gama=1.4

    #Primary jet input information
  #  Velocity_primary = 217.2
 #   Temperature_primary = 288
  #  Pressure_primary=112000

    
    Diameter_primary =0.4
    Area_primary = np.pi*(Diameter_primary/2)**2 # 0.001963

    #Secondary jet input information
 #   Velocity_secondary = 216.8
 #   Temperature_secondary = 288.0
 #   Pressure_secondary=110000

    
    Diameter_secondary=1.2
    Area_secondary =  np.pi*(Diameter_secondary/2)**2 #0.00394

    #Aircraft input information
   # Velocity_aircraft = 0.0
   # Altitude=0.0
  #  AOA=0.0

    # Engine input information
    EXA = 1 #(distance from fan face to fan exit/ fan diameter)
 #   N1 = 3000 #Fan rotational speed [rpm]
    Plug_diameter = 0.1

    #distance_microphone = 13.08
 #   angles=[60,70,80,90,100,110,120,130] #Array of desired polar angles
    Xo=0 #1 #Acoustic center of reference [m]
   # dist= 1.5 #Dist?ncia da sa?da de exaust?o at? o microfone(KQ) [m]

    #Flags for definition of near-fiel or wind-tunnel data
    near_field=0
    tunnel=0

    # Geometry information for the installation effects function
    Xe=1
    Ye=1
    Ce=2

    #Engine centerline heigh above the ground plane
    engine_height = 0.5

    """Starting the main program"""


    #Arrays for the calculation of atmospheric attenuation
    Acq=np.array((0, 0, 0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.9, 1.2, 1.5, 1.9, 2.5, 2.9, 3.6, 4.9, 6.8))
    Acf=np.array((0, 0, 0, 0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.3, 1.8, 2.5, 3.0, 4.2, 6.1, 9.0))

    #Desired frequency range for noise evaluation
    frequency=np.array((50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, \
            2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000))


#Defining each array before the main loop - Changed August 03rd
  #  theta=np.zeros(24)
    B=np.zeros(24)
    theta_p=np.ones(24)*np.pi/2
    theta_s=np.ones(24)*np.pi/2
    theta_m=np.ones(24)*np.pi/2
    EX_p=np.zeros(24)
    EX_s=np.zeros(24)
    EX_m=np.zeros(24)
    exc=np.zeros(24)
    SPL_p=np.zeros(24)
    SPL_s=np.zeros(24)
    SPL_m=np.zeros(24)
    PG_p=np.zeros(24)
    PG_s=np.zeros(24)
    PG_m=np.zeros(24)
    
    SPL_total_history = np.zeros((nsteps,24))
    SPL_primary_history = np.zeros((nsteps,24))
    SPL_secondary_history = np.zeros((nsteps,24))
    SPL_mixed_history = np.zeros((nsteps,24))

    # Open output file to print the results
    filename = 'SAE_Noise_try_2.dat'
    fid = open(filename,'w')
    
    
    #Calculation of ambient properties
   # temperature_ambient = 288.15 - 6.5*10**(-3)*Altitude           #temperature, K
  #  sound_ambient=np.sqrt(1.4*287*temperature_ambient)           #sound speed, m/s
  #  density_ambient = (1/(temperature_ambient/288.15))*1.225     #density, kg/m3


 #START LOOP FOR EACH POSITION OF AIRCRAFT   
    for id in range(0,nsteps):

        # Jet Flow Parameters
    
        #Primary and Secondary jets
        Cpp=R_gas/(1-1/gama_primary)
        Cp=R_gas/(1-1/gama)
        density_primary=Pressure_primary[id]/(R_gas*Temperature_primary[id]-(0.5*R_gas*Velocity_primary[id]**2/Cpp))
        density_secondary=Pressure_secondary[id]/(R_gas*Temperature_secondary[id]-(0.5*R_gas*Velocity_secondary[id]**2/Cp))
    
        mass_flow_primary=Area_primary*Velocity_primary[id]*density_primary
        mass_flow_secondary=Area_secondary*Velocity_secondary[id]*density_secondary
    
        #Mach number of the external flow - based on the aircraft velocity
        Mach_aircraft[id]=Velocity_aircraft/sound_ambient[id]
    
        #Calculation Procedure for the Mixed Jet Flow Parameters
        Velocity_mixed = (mass_flow_primary*Velocity_primary[id]+mass_flow_secondary*Velocity_secondary[id])/ \
                (mass_flow_primary+mass_flow_secondary)
        Temperature_mixed =(mass_flow_primary*Temperature_primary[id]+mass_flow_secondary*Temperature_secondary[id])/ \
                (mass_flow_primary+mass_flow_secondary)
        density_mixed = pressure_amb[id]/(R_gas*Temperature_mixed-(0.5*R_gas*Velocity_mixed**2/Cp))
        Area_mixed = Area_primary*density_primary*Velocity_primary[id]*(1+(mass_flow_secondary/mass_flow_primary))/ \
                (density_mixed*Velocity_mixed)
        Diameter_mixed = (4*Area_mixed/np.pi)**0.5
    
        #**********************************************
        # START OF THE NOISE PROCEDURE CALCULATIONS
        #**********************************************
    
        XBPR = mass_flow_secondary/mass_flow_primary - 5.5
        if XBPR<0:
                XBPR=0
        elif XBPR>4:
                XBPR=4
    
        #Auxiliary parameter defined as DVPS
        DVPS = np.abs((Velocity_primary[id] - (Velocity_secondary[id]*Area_secondary+Velocity_aircraft*Area_primary)/(Area_secondary+Area_primary)))
        if DVPS<0.3:
            DVPS=0.3
    
        # Calculation of the Strouhal number for each jet component (p-primary, s-secondary, m-mixed)
        Str_p = frequency*Diameter_primary/(DVPS)  #Primary jet
        Str_s = frequency*Diameter_mixed/(Velocity_secondary[id]-Velocity_aircraft) #Secondary jet
        Str_m = frequency*Diameter_mixed/(Velocity_mixed-Velocity_aircraft) #Mixed jet
    
        #Calculation of the Excitation adjustment parameter
        #Excitation Strouhal Number
        excitation_Strouhal = (N1/60)*(Diameter_mixed/Velocity_mixed)
        if (excitation_Strouhal > 0.25 and excitation_Strouhal < 0.5):
            SX=0.0
        else:
            SX=50*(excitation_Strouhal-0.25)*(excitation_Strouhal-0.5)
    
        #Effectiveness
        exps = np.exp(-SX)
    
        #Spectral Shape Factor
        exs=5*exps*np.exp(-(np.log10(Str_m/(2*excitation_Strouhal+0.00001)))**2)
    
        #Fan Duct Lenght Factor
        exd=np.exp(0.6-(EXA)**0.5)
    
        #Excitation source location factor (zk)
        zk=1-0.4*(exd)*(exps)
    
    ##    #Defining each array before the main loop
    ##    theta=np.zeros(24)
    ##    B=np.zeros(24)
    ##    theta_p=np.ones(24)*np.pi/2
    ##    theta_s=np.ones(24)*np.pi/2
    ##    theta_m=np.ones(24)*np.pi/2
    ##    EX_p=np.zeros(24)
    ##    EX_s=np.zeros(24)
    ##    EX_m=np.zeros(24)
    ##    exc=np.zeros(24)
    ##    SPL_p=np.zeros(24)
    ##    SPL_s=np.zeros(24)
    ##    SPL_m=np.zeros(24)
    ##    PG_p=np.zeros(24)
    ##    PG_s=np.zeros(24)
    ##    PG_m=np.zeros(24)
    ##
    ##    # Open output file to print the results
    ##    filename = 'SAE_Noise_try.dat'
    ##    fid = open(filename,'w')
    
        #Main loop for the desired polar angles
     #   for jind in range (8):
        theta=angles[id]  #*np.pi/180
    
      #Call function noise source location for the calculation of theta
        thetaj=noise_source_location(B,Xo,zk,Diameter_primary,theta_p,Area_primary,Area_secondary,distance_microphone[id],Diameter_secondary,theta,theta_s,theta_m,Diameter_mixed,Velocity_primary[id],Velocity_secondary[id],Velocity_mixed,Velocity_aircraft,sound_ambient[id],Str_m,Str_s)
    
      # Loop for the frequency array range
        for i in range(0,24):
               #Calculation of the Directivity Factor
                if (theta_m[i] <=1.4):
                    exc[i]= sound_ambient[id]/Velocity_mixed
                elif (theta_m[i]>1.4):
                    exc[i]=(sound_ambient[id]/Velocity_mixed)*(1-(1.8/np.pi)*(theta_m[i]-1.4))
    
                #Acoustic excitation adjustment (EX)
                EX_m[i]=exd*exs[i]*exc[i]   #mixed component - dependant of the frequency
        EX_p=+5*exd*exps   #primary component - no frequency dependance
        EX_s=2*sound_ambient[id]/(Velocity_secondary[id]*(zk)) #secondary component - no frequency dependance
    
    
        distance_primary=distance_microphone[id] # dist #*sin(theta)/sin(thetaj(i,1));
        distance_secondary=distance_microphone[id] # #*sin(theta)/sin(thetaj(i,2));
        distance_mixed=distance_microphone[id] # #*sin(theta)/sin(thetaj(i,3));
    
        #Noise attenuation due to Ambient Pressure
        dspl_ambient_pressure = 20*np.log10(pressure_amb[id]/pressure_isa)
    
        #Noise attenuation due to Density
        dspl_density_p=20*np.log10((density_primary+density_secondary)/(2*density_ambient[id]))
        dspl_density_s=20*np.log10((density_secondary+density_ambient[id])/(2*density_ambient[id]))
        dspl_density_m=20*np.log10((density_mixed+density_ambient[id])/(2*density_ambient[id]))
    
        #Noise attenuation due to Spherical divergence
        dspl_spherical_p=20*np.log10(Diameter_primary/distance_primary)
        dspl_spherical_s=20*np.log10(Diameter_mixed/distance_secondary)
        dspl_spherical_m=20*np.log10(Diameter_mixed/distance_mixed)
    
       #Noise attenuation due to Geometric Near-Field
        if near_field ==0:
                dspl_geometric_p=0.0
                dspl_geometric_s=0.0
                dspl_geometric_m=0.0
        elif near_field ==1:
                dspl_geometric_p=-10*np.log10(1+(2*Diameter_primary+(Diameter_primary*sound_ambient[id]/frequency))/distance_primary)
                dspl_geometric_s=-10*np.log10(1+(2*Diameter_mixed+(Diameter_mixed*sound_ambient[id]/frequency))/distance_secondary)
                dspl_geometric_m=-10*np.log10(1+(2*Diameter_mixed+(Diameter_mixed*sound_ambient[id]/frequency))/distance_mixed)
    
       #Noise attenuation due to Acoustic Near-Field
        if near_field ==0:
                dspl_acoustic_p=0.0;
                dspl_acoustic_s=0.0;
                dspl_acoustic_m=0.0;
        elif near_field ==1:
                dspl_acoustic_p=10*np.log10(1+0.13*(sound_ambient[id]/(distance_primary*frequency))**2)
                dspl_acoustic_s=10*np.log10(1+0.13*(sound_ambient[id]/(distance_secondary*frequency))**2)
                dspl_acoustic_m=10*np.log10(1+0.13*(sound_ambient[id]/(distance_mixed*frequency))**2)
    
            #Atmospheric attenuation coefficient
        if tunnel==0:
                f_primary=frequency/(1-Mach_aircraft[id]*np.cos(theta_p))
                f_secondary=frequency/(1-Mach_aircraft[id]*np.cos(theta_s))
                f_mixed=frequency/(1-Mach_aircraft[id]*np.cos(theta_m))
                Aci= Acf + ((temperature_ambient[id]-273)-15)/10*(Acq-Acf)
                Ac_primary=np.interp(f_primary,frequency,Aci)
                Ac_secondary=np.interp(f_secondary,frequency,Aci)
                Ac_mixed=np.interp(f_mixed,frequency,Aci)
                
                dspl_attenuation_p=np.zeros(24) #-Ac_primary*distance_primary
                dspl_attenuation_s=np.zeros(24) #-Ac_secondary*distance_secondary
                dspl_attenuation_m=np.zeros(24) #-Ac_mixed*distance_mixed
    
        elif tunnel==1: #These corrections are not applicable for jet rigs or static conditions
                dspl_attenuation_p=np.zeros(24)
                dspl_attenuation_s=np.zeros(24)
                dspl_attenuation_m=np.zeros(24)
                EX_m=np.zeros(24)
                EX_p=0
                EX_s=0
    
       #Calculation of the total noise attenuation (p-primary, s-secondary, m-mixed components)
        DSPL_p=dspl_ambient_pressure+dspl_density_p+dspl_geometric_p+dspl_acoustic_p+dspl_attenuation_p+dspl_spherical_p
        DSPL_s=dspl_ambient_pressure+dspl_density_s+dspl_geometric_s+dspl_acoustic_s+dspl_attenuation_s+dspl_spherical_s
        DSPL_m=dspl_ambient_pressure+dspl_density_m+dspl_geometric_m+dspl_acoustic_m+dspl_attenuation_m+dspl_spherical_m
    
    
      #Calculation of interference effects on jet noise
        ATK_m=angle_of_attack_effect(AOA,Mach_aircraft[id],theta_m)
        INST_s= jet_installation_effect(Xe,Ye,Ce,theta_s,Diameter_mixed)
        Plug=external_plug_effect(Velocity_primary[id],Velocity_secondary[id], Velocity_mixed, Diameter_primary,Diameter_secondary,Diameter_mixed, Plug_diameter, sound_ambient[id], theta_p,theta_s,theta_m)
        GPROX_m=ground_proximity_effect(Velocity_mixed,sound_ambient[id],theta_m,engine_height,Diameter_mixed,frequency)
    
      #Calculation of the sound pressure level for each jet component
        SPL_p=primary_noise_component(SPL_p,Velocity_primary[id],Temperature_primary[id],R_gas,theta_p,DVPS,sound_ambient[id],Velocity_secondary[id],Velocity_aircraft,Area_primary,Area_secondary,DSPL_p,EX_p,Str_p) + Plug[0]
        SPL_s=secondary_noise_component(SPL_s,Velocity_primary[id],theta_s,sound_ambient[id],Velocity_secondary[id],Velocity_aircraft,Area_primary,Area_secondary,DSPL_s,EX_s,Str_s) + Plug[1] + INST_s
        SPL_m=mixed_noise_component(SPL_m,Velocity_primary[id],theta_m,sound_ambient[id],Velocity_secondary[id],Velocity_aircraft,Area_primary,Area_secondary,DSPL_m,EX_m,Str_m,Velocity_mixed,XBPR) + Plug[2] + ATK_m + GPROX_m
    
     #Sum of the Total Noise
        SPL_total = 10 * np.log10(10**(0.1*SPL_p)+10**(0.1*SPL_s)+10**(0.1*SPL_m))
        
        
     #modification 03 Agosto, 2015
     
        SPL_total_history[id][:]=SPL_total[:]
        SPL_primary_history[id][:]=SPL_p[:]
        SPL_secondary_history[id][:]=SPL_s[:]
        SPL_mixed_history[id][:]=SPL_m[:]
        
     
    #Calculation of the Perceived Noise Level EPNL based on the sound time history
    PNL_total               =  pnl_noise(SPL_total_history)    
    PNL_primary               =  pnl_noise(SPL_primary_history)  
    PNL_secondary               =  pnl_noise(SPL_secondary_history)  
    PNL_mixed               =  pnl_noise(SPL_mixed_history)  
    
   #Calculation of the tones corrections on the SPL for each component and total
    tone_correction_total =noise_tone_correction(SPL_total_history) 
    tone_correction_primary = noise_tone_correction(SPL_primary_history) 
    tone_correction_secondary = noise_tone_correction(SPL_secondary_history) 
    tone_correction_mixed = noise_tone_correction(SPL_mixed_history) 
    
    #Calculation of the PLNT for each component and total
    PNLT_total=PNL_total+tone_correction_total
    PNLT_primary=PNL_primary+tone_correction_primary
    PNLT_secondary=PNL_secondary+tone_correction_secondary
    PNLT_mixed=PNL_mixed+tone_correction_mixed
    
    #Calculation of the EPNL for each component and total
    EPNL_total=epnl_noise(PNLT_total)
    EPNL_primary=epnl_noise(PNLT_primary)
    EPNL_secondary=epnl_noise(PNLT_secondary)
    EPNL_mixed=epnl_noise(PNLT_mixed)
    
   # print EPNL_total
    
     #Printing the output solution for the engine noise calculation
     
    fid.write('Engine noise module - SAE Model for Turbofan' + '\n')
    fid.write('Certification point = FLYOVER' + '\n')
    fid.write('EPNL = ' + str('%3.2f' % EPNL_total) + '\n')
    fid.write('PNLTM = ' + str('%3.2f' % np.max(PNLT_total)) + '\n')
    
    
    fid.write('Reference speed =  ')
    fid.write(str('%2.2f' % (Velocity_aircraft/Units.kts))+'  kts')
    fid.write('\n')
    fid.write('PNLT history')
    fid.write('\n')
    fid.write('time     	altitude     Mach     Core Velocity   Fan Velocity  Polar angle    Azim angle    distance    Primary	  Secondary 	 Mixed        Total')
    fid.write('\n')
    for id in range (0,nsteps):
        fid.write(str('%2.2f' % time[id])+'        ')
        fid.write(str('%2.2f' % Altitude[id])+'        ')
        fid.write(str('%2.2f' % Mach_aircraft[id])+'        ')
        fid.write(str('%3.3f' % Velocity_primary[id])+'        ')
        fid.write(str('%3.3f' % Velocity_secondary[id])+'        ')
        fid.write(str('%2.2f' % (angles[id]*180/np.pi))+'        ')
        fid.write(str('%2.2f' % (phi[id]*180/np.pi))+'        ')
        fid.write(str('%2.2f' % distance_microphone[id])+'        ')
        fid.write(str('%2.2f' % PNLT_primary[id])+'        ')
        fid.write(str('%2.2f' % PNLT_secondary[id])+'        ')
        fid.write(str('%2.2f' % PNLT_mixed[id])+'        ')
        fid.write(str('%2.2f' % PNLT_total[id])+'        ')
        fid.write('\n')
    fid.write('\n')
    fid.write('PNLT max =  ')
    fid.write(str('%2.2f' % (np.max(PNLT_total)))+'  dB')
    fid.write('\n')
    fid.write('EPNdB')
    fid.write('\n')
    fid.write('Primary  Secondary  	Mixed  		Total')
    fid.write('\n')
    fid.write(str('%2.2f' % EPNL_primary)+'        ')
    fid.write(str('%2.2f' % EPNL_secondary)+'        ')
    fid.write(str('%2.2f' % EPNL_mixed)+'        ')
    fid.write(str('%2.2f' % EPNL_total)+'        ')
    fid.write('\n')
    
    for id in range (0,nsteps):
        fid.write('\n')
        fid.write('Emission angle = ' + str(angles[id]*180/np.pi) + '\n')
        fid.write('Altitute = ' + str(Altitude[id]) + '\n')
        fid.write('Distance = ' + str(distance_microphone[id]) + '\n')
        fid.write('Time = ' + str(time[id]) + '\n')
        fid.write('f		Primary  Secondary  	Mixed  		Total' + '\n')
     
   
        for ijd in range(0,24):
                   fid.write(str((frequency[ijd])) + '       ')
                   fid.write(str('%3.2f' % SPL_primary_history[id][ijd]) + '       ')
                   fid.write(str('%3.2f' % SPL_secondary_history[id][ijd]) + '       ')
                   fid.write(str('%3.2f' % SPL_mixed_history[id][ijd]) + '       ')
                   fid.write(str('%3.2f' % SPL_total_history[id][ijd]) + '       ')
                   fid.write('\n')
        
           
    fid.close
    
    return(EPNL_total,SPL_total_history)