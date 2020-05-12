# Plot_Mission.py
# 
# Created:  May 2015, E. Botero
# Modified: 

# ----------------------------------------------------------------------        
#   Imports
# ----------------------------------------------------------------------    

import SUAVE
from SUAVE.Core import Units
from SUAVE.Input_Output.Results import print_weight_breakdown
import pylab as plt
import pandas as pd
# ----------------------------------------------------------------------
#   Plot Mission
# ----------------------------------------------------------------------

def plot_mission(nexus,line_style='bo-'):
    results   = nexus.results.base
    axis_font = {'fontname':'Arial', 'size':'14'}    


    # ------------------------------------------------------------------
    #   Aerodynamics 
    # ------------------------------------------------------------------
    fig = plt.figure("Aerodynamic Coefficients",figsize=(8,10))
    for segment in results.segments.values():

        time   = segment.conditions.frames.inertial.time[:,0] / Units.min
        CLift  = segment.conditions.aerodynamics.lift_coefficient[:,0]
        CDrag  = segment.conditions.aerodynamics.drag_coefficient[:,0]
        #aoa = segment.conditions.aerodynamics.angle_of_attack[:,0] / Units.deg
        throttle = segment.conditions.propulsion.throttle[:,0]
        l_d = CLift/CDrag

        axes = fig.add_subplot(3,1,1)
        axes.plot( time , CLift , line_style )
        axes.set_ylabel('Lift Coefficient',axis_font)
        axes.grid(True)

        axes = fig.add_subplot(3,1,2)
        axes.plot( time , l_d , line_style )
        axes.set_ylabel('L/D',axis_font)
        axes.grid(True)

        axes = fig.add_subplot(3,1,3)
        axes.plot( time , throttle , 'ro-' )
        axes.set_xlabel('Time (min)',axis_font)
        axes.set_ylabel('Throttle ()',axis_font)
        axes.grid(True)
        if segment.tag == 'cruise': # Grab the aero buildups
             fuselagedrag   = segment.conditions.aerodynamics.drag_breakdown.parasite.fuselage
             wingdrag       = segment.conditions.aerodynamics.drag_breakdown.parasite.main_wing
             horizontaldrag = segment.conditions.aerodynamics.drag_breakdown.parasite.horizontal_stabilizer
             verticaldrag   = segment.conditions.aerodynamics.drag_breakdown.parasite.vertical_stabilizer
             enginedrag     = segment.conditions.aerodynamics.drag_breakdown.parasite.turbofan
             pylondrag      = segment.conditions.aerodynamics.drag_breakdown.parasite.pylon
             parasitetotal  = segment.conditions.aerodynamics.drag_breakdown.parasite.total
             induceddrag    = segment.conditions.aerodynamics.drag_breakdown.induced
             compressdrag   = segment.conditions.aerodynamics.drag_breakdown.compressible
             miscdrag       = segment.conditions.aerodynamics.drag_breakdown.miscellaneous
             dragdelta      = segment.conditions.aerodynamics.drag_breakdown.drag_coefficient_increment
             totaldrag      = segment.conditions.aerodynamics.drag_breakdown.total
             clcruise       = CLift

    # ------------------------------------------------------------------
    #   Aerodynamics 2
    # ------------------------------------------------------------------
    fig = plt.figure("Drag Components",figsize=(8,10))
    axes = plt.gca()
    for i, segment in enumerate(results.segments.values()):

        time   = segment.conditions.frames.inertial.time[:,0] / Units.min
        drag_breakdown = segment.conditions.aerodynamics.drag_breakdown
        cdp = drag_breakdown.parasite.total[:,0]
        cdi = drag_breakdown.induced.total[:,0]
        cdc = drag_breakdown.compressible.total[:,0]
        cdm = drag_breakdown.miscellaneous.total[:,0]
        cd  = drag_breakdown.total[:,0]

        if line_style == 'bo-':
            axes.plot( time , cdp , 'ko-', label='CD parasite' )
            axes.plot( time , cdi , 'bo-', label='CD induced' )
            axes.plot( time , cdc , 'go-', label='CD compressibility' )
            axes.plot( time , cdm , 'yo-', label='CD miscellaneous' )
            axes.plot( time , cd  , 'ro-', label='CD total'   )
            if i == 0:
                axes.legend(loc='upper center')            
        else:
            axes.plot( time , cdp , line_style )
            axes.plot( time , cdi , line_style )
            axes.plot( time , cdc , line_style )
            axes.plot( time , cdm , line_style )
            axes.plot( time , cd  , line_style )            

    axes.set_xlabel('Time (min)')
    axes.set_ylabel('CD')
    axes.grid(True)

    # ------------------------------------------------------------------
    #   Altitude, sfc, vehicle weight
    # ------------------------------------------------------------------

    fig = plt.figure("Altitude_sfc_weight",figsize=(8,10))
    for segment in results.segments.values():

        time     = segment.conditions.frames.inertial.time[:,0] / Units.min
        aoa      = segment.conditions.aerodynamics.angle_of_attack[:,0] / Units.deg
        mass     = segment.conditions.weights.total_mass[:,0] / Units.lb
        altitude = segment.conditions.freestream.altitude[:,0] / Units.ft
        mdot     = segment.conditions.weights.vehicle_mass_rate[:,0]
        thrust   =  segment.conditions.frames.body.thrust_force_vector[:,0]
        sfc      = (mdot / Units.lb) / (thrust /Units.lbf) * Units.hr
        #import pdb; pdb.set_trace()
        eta      = segment.conditions.freestream.velocity[:,0] / Units.knots * 7.807 / 18580 / sfc

        axes = fig.add_subplot(3,1,1)
        axes.plot( time , altitude , line_style )
        axes.set_ylabel('Altitude (ft)',axis_font)
        axes.grid(True)

        axes = fig.add_subplot(3,1,3)
        axes.plot( time , eta , line_style )
        axes.set_xlabel('Time (min)',axis_font)
        axes.set_ylabel('eta',axis_font)
        axes.grid(True)

        axes = fig.add_subplot(3,1,2)
        axes.plot( time , mass , 'ro-' )
        axes.set_ylabel('Weight (lb)',axis_font)
        axes.grid(True)
   # import pdb; pdb.set_trace()


    fig = plt.figure("Weight Breakdown",figsize=(8,10))
    ax = fig.add_subplot(2,1,2)
    #fig.patch.set_visible(False)
    ax.axis('off')
    #ax.axis('tight')
    vehicle = nexus.vehicle_configurations.base
    columns = ('Units', 'Value')
    rows    = ('Wing','Fuselage', 'Landing Gear', 'Horizontal Tail','Vertical Tail & Rudder','Propulsion','Systems','OEW', 'MZFW','MLW','MTOW')
    data    = [['lbm' ,  "%.0f" % (vehicle.mass_properties.breakdown.wing / Units.lb)],
                ['lbm' , "%.0f" % (vehicle.mass_properties.breakdown.fuselage[0] / Units.lb)],
                ['lbm' , "%.0f" % (vehicle.mass_properties.breakdown.landing_gear / Units.lb)],
                ['lbm' , "%.0f" % (vehicle.mass_properties.breakdown.horizontal_tail / Units.lb)],
                ['lbm', "%.0f" % ((vehicle.mass_properties.breakdown.vertical_tail + vehicle.mass_properties.breakdown.rudder) / Units.lb)],
                ['lbm' , "%.0f" % (vehicle.mass_properties.breakdown.propulsion / Units.lb)],
                ['lbm' , "%.0f" % (vehicle.mass_properties.breakdown.systems / Units.lb)],
                [ 'lbm' , "%.0f" % (vehicle.mass_properties.operating_empty[0] / Units.lb)],
                [ 'lbm' , "%.0f" % (vehicle.mass_properties.max_zero_fuel[0]   / Units.lb)],
                [ ' lbm',  "%.0f" % (vehicle.mass_properties.max_landing    / Units.lb)],
                [ 'lbm' ,  "%.0f" % (vehicle.mass_properties.max_takeoff     / Units.lb)]]
   # plt.pie( data[1,:],labels = data[:,0])
  # roundeddata = ["%.2f" % data for data in vars]
    the_1table =  ax.table (cellText = data, rowLabels = rows, colLabels = columns, bbox = [0.3,.5,.5,.5], loc = 'center')
    the_1table.auto_set_font_size(False)
    the_1table.set_fontsize(9) 


    #fig.tight_layout()
    ax = fig.add_subplot(2,1,1)
    datapie    = [(vehicle.mass_properties.breakdown.wing / Units.lb),
                (vehicle.mass_properties.breakdown.fuselage[0] / Units.lb),
                (vehicle.mass_properties.breakdown.landing_gear / Units.lb),
                (vehicle.mass_properties.breakdown.horizontal_tail / Units.lb),
                ((vehicle.mass_properties.breakdown.vertical_tail + vehicle.mass_properties.breakdown.rudder) / Units.lb),
                (vehicle.mass_properties.breakdown.propulsion / Units.lb),
                (vehicle.mass_properties.breakdown.systems / Units.lb)]
    rows    = ('Wing','Fuselage', 'Landing Gear', 'Horizontal Tail','Vertical Tail & Rudder','Propulsion','Systems')

    ax.pie(datapie,labels = rows, autopct='%1.1f%%' , shadow=True, startangle=90)

    fig = plt.figure("Drag Breakdown",figsize=(8,10))
    ax = fig.add_subplot(2,1,2)
    #fig.patch.set_visible(False)
    ax.axis('off')
    #ax.axis('tight')
  #  import pdb; pdb.set_trace()

 #   columns = ('Wetted Area (sqft)', 'Cf', 'Form Factor','f (sqft)', 'Cd')
 #   rows    = ('Wing','Fuselage', 'Horizontal Tail','Vertical Tail','Engine', 'Pylon', 'Cdo')#, 'Cl', 'Viscous e', 'AR', 'Cdi', 'Cdc', 'Cdmisc', 'Cdtrim', 'Cdtotal', 'L/D')
 #   data    = [ ["%.0f" % (wingdrag.wetted_area / Units.ft / Units.ft), "%.5f" % wingdrag.skin_friction_coefficient[0], "%.4f" % wingdrag.form_factor[5][0], "%.2f" % (wingdrag.parasite_drag_coefficient[5][0] * vehicle.wings.main_wing.areas.reference / Units.ft / Units.ft) ,"%.5f" % wingdrag.parasite_drag_coefficient[5][0] ], 
 #               ["%.0f" % (fuselagedrag.wetted_area / Units.ft / Units.ft), "%.5f" % fuselagedrag.skin_friction_coefficient[5][0], "%.4f" % fuselagedrag.form_factor[5][0], "%.2f" % (fuselagedrag.parasite_drag_coefficient[5][0]  * vehicle.wings.main_wing.areas.reference / Units.ft / Units.ft),"%.5f" % fuselagedrag.parasite_drag_coefficient[5][0] ],
 #               ["%.0f" % (horizontaldrag.wetted_area / Units.ft / Units.ft), "%.5f" % horizontaldrag.skin_friction_coefficient[5][0],"%.4f" % horizontaldrag.form_factor[5][0], "%.2f" % (horizontaldrag.parasite_drag_coefficient[5][0]  * vehicle.wings.main_wing.areas.reference / Units.ft / Units.ft),"%.5f" % horizontaldrag.parasite_drag_coefficient[5][0] ],
 #               ["%.0f" % (verticaldrag.wetted_area / Units.ft / Units.ft), "%.5f" % verticaldrag.skin_friction_coefficient[5][0],"%.4f" % verticaldrag.form_factor[5][0], "%.2f" % (verticaldrag.parasite_drag_coefficient[5][0]  * vehicle.wings.main_wing.areas.reference / Units.ft / Units.ft),"%.5f" % verticaldrag.parasite_drag_coefficient[5][0] ],
  #           ["%.0f" % (enginedrag.wetted_area / Units.ft / Units.ft), "%.5f" % enginedrag.skin_friction_coefficient[5][0],"%.4f" % enginedrag.form_factor, "%.2f" % (enginedrag.parasite_drag_coefficient[5][0]  * vehicle.wings.main_wing.areas.reference / Units.ft / Units.ft),"%.5f" % enginedrag.parasite_drag_coefficient[5][0] ],
  #              ["%.0f" % (pylondrag.wetted_area / Units.ft / Units.ft), "%.5f" % pylondrag.skin_friction_coefficient[5][0],"%.4f" % pylondrag.form_factor, "%.2f" % (pylondrag.parasite_drag_coefficient[5][0]  * vehicle.wings.main_wing.areas.reference / Units.ft / Units.ft), "%.5f" % pylondrag.parasite_drag_coefficient[5][0]],
  #              [ '-','-','-' ,"%.2f" % ( parasitetotal[5][0] * vehicle.wings.main_wing.areas.reference / Units.ft / Units.ft) , "%.5f" % parasitetotal[5][0]]]
#    columns = ('Wetted Area (sqft)', 'Cf', 'Compress Factor', 'Reynolds Factor' , 'Form Factor', 'Cd')
#    rows    = ('Wing','Fuselage', 'Horizontal Tail','Vertical Tail','Engine', 'Pylon', 'Cdo')#, 'Cl', 'Viscous e', 'AR', 'Cdi', 'Cdc', 'Cdmisc', 'Cdtrim', 'Cdtotal', 'L/D')
#    data    = [ ["%.0f" % (wingdrag.wetted_area / Units.ft / Units.ft), "%.5f" % wingdrag.skin_friction_coefficient[0][0], "%.5f" % wingdrag.compressibility_factor[0][0] , "%.4f" % wingdrag.reynolds_factor[0][0], "%.4f" % wingdrag.form_factor[0][0], "%.5f" % wingdrag.parasite_drag_coefficient[0][0]], 
#                ["%.0f" % (fuselagedrag.wetted_area / Units.ft / Units.ft), "%.5f" % fuselagedrag.skin_friction_coefficient[0][0], "%.5f" % fuselagedrag.compressibility_factor[0][0] , "%.4f" % fuselagedrag.reynolds_factor[0][0], "%.4f" % fuselagedrag.form_factor[0][0], "%.5f" % fuselagedrag.parasite_drag_coefficient[0][0]],
#                ["%.0f" % (horizontaldrag.wetted_area / Units.ft / Units.ft), "%.5f" % horizontaldrag.skin_friction_coefficient[0][0], "%.5f" % horizontaldrag.compressibility_factor[0][0] , "%.4f" % horizontaldrag.reynolds_factor[0][0], "%.4f" % horizontaldrag.form_factor[0][0], "%.5f" % horizontaldrag.parasite_drag_coefficient[0][0]],
#                ["%.0f" % (verticaldrag.wetted_area / Units.ft / Units.ft), "%.5f" % verticaldrag.skin_friction_coefficient[0][0], "%.5f" % verticaldrag.compressibility_factor[0][0] , "%.4f" % verticaldrag.reynolds_factor[0][0], "%.4f" % verticaldrag.form_factor[0][0], "%.5f" % verticaldrag.parasite_drag_coefficient[0][0]],
#                ["%.0f" % (enginedrag.wetted_area / Units.ft / Units.ft), "%.5f" % enginedrag.skin_friction_coefficient[0][0], "%.5f" % enginedrag.compressibility_factor[0][0] , "%.4f" % enginedrag.reynolds_factor[0][0], "%.4f" % enginedrag.form_factor, "%.5f" % enginedrag.parasite_drag_coefficient[0][0]],
#                ["%.0f" % (pylondrag.wetted_area / Units.ft / Units.ft), "%.5f" % pylondrag.skin_friction_coefficient[0][0], "%.5f" % pylondrag.compressibility_factor[0][0] , "%.4f" % pylondrag.reynolds_factor[0][0], "%.4f" % pylondrag.form_factor, "%.5f" % pylondrag.parasite_drag_coefficient[0][0]],
#                [ 0 , 0 , 0 ,0 ,0 , "%.5f" % parasitetotal[0][0]]]


    
   # the_table = ax.table (cellText = data, rowLabels = rows, colLabels = columns, bbox = [0.3,.5,.5,.8], loc = 'center')
   # the_table.auto_set_font_size(False)
   # the_table.set_fontsize(9)    #fig.tight_layout()
   # rows    = ('Cdo', 'Cl', 'Viscous e', 'AR', 'Cdi', 'Cdc', 'Cdmisc', 'Cdtrim', 'Cdtotal', 'L/D')
   # columns = ('Value')
   # ax = fig.add_subplot(2,1,1)
   # data    =   [["%.5f" % parasitetotal[5][0]],
   #              [ clcruise[5]],
   #              [ induceddrag.efficiency_factor[5][0]],
   #              [  induceddrag.aspect_ratio],
   #              [  induceddrag.total[5][0]],
   #              [  compressdrag.total[5][0]],
   #              [  miscdrag.total[5][0]],
   #              [  dragdelta],
   #              [  totaldrag[5][0]]
   #              [   (clcruise[5] / totaldrag[5][0])]]
   # the_table = ax.table (cellText = data, rowLabels = rows, colLabels = columns, bbox = [0.1,.2,.8,.8], loc = 'center')
    # the_table.auto_set_font_size(False)
    # the_table.set_fontsize(9) 

    #plt.show(block = True)


    print_weight_breakdown(vehicle, 'weight_output.txt')


    return

if __name__ == '__main__': 
    main()    
    plt.show()