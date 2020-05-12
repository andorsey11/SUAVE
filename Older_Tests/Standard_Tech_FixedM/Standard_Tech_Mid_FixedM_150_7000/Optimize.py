# Optimize.py
# Created:  Feb 2016, M. Vegh
# Modified: Aug 2017, E. Botero
#           Aug 2018, T. MacDonald

# ----------------------------------------------------------------------        
#   Imports
# ----------------------------------------------------------------------    

import SUAVE
from SUAVE.Core import Units, Data
import numpy as np
import Vehicles
import Analyses
import Missions
import Procedure
#import Procedure_MTOWConverge
import Plot_Mission
import matplotlib.pyplot as plt
from SUAVE.Optimization import Nexus, carpet_plot
import SUAVE.Optimization.Package_Setups.scipy_setup as scipy_setup
import SUAVE.Optimization.Package_Setups.pyoptsparse_setup as pyopt_setup


# ----------------------------------------------------------------------        
#   Run the whole thing
# ----------------------------------------------------------------------  
def main():
    problem = setup()
    
    ## Base Input Values
   # output = problem.objective()
    
    ## Uncomment to view contours of the design space
    #variable_sweep(problem)
    ## Uncomment for the first optimization
    output = pyopt_setup.Pyoptsparse_Solve(problem,solver='SLSQP', sense_step=1.0E-3)
    #print(output)        
    #output = scipy_setup.SciPy_Solve(problem, solver='SLSQP')
    # print('fuel burn = ', "%.1f" % (problem.summary.base_mission_fuelburn[0] / Units.lbs))
    # #print('fuel margin = ', problem.summary.max_zero_fuel_margin)
    # print('approach speed =',"%.1f" % (problem.summary.approach_Speed / Units.knots))
    # print('max throttle setting =',"%.3f" %(problem.summary.max_throttle))
    # print('takeoff field length (ft)', "%.0f" %(problem.summary.takeoff_field_length[0][0]/ Units.ft))
    # print('MTOW', "%.0f" %(problem.summary.takeoff_weight/ Units.lb))
    # print('OEW', "%.0f" %(problem.summary.operating_empty[0] / Units.lb))
    # print('T/W',  (problem.summary.thrust / Units.lbf) /(problem.summary.takeoff_weight / Units.lb))
    # print('2nd Seg Gradient',"%.4f" % problem.summary.second_seg_grad[0][0])
    # print('Nacelle Diameter (in)', "%.1f" % problem.summary.nacelle_d)
    # print('Engine Length (in)', "%.1f" % problem.summary.engine_length)

    Plot_Mission.plot_mission(problem)
    #plt.show()
    #import pdb; pdb.set_trace()
    return

# ----------------------------------------------------------------------        
#   Inputs, Objective, & Constraints
# ----------------------------------------------------------------------  

def setup():

    nexus = Nexus()
    problem = Data()
    nexus.optimization_problem = problem

    # -------------------------------------------------------------------
    # Inputs
    # -------------------------------------------------------------------

    #   [ tag                            , initial, (lb,ub)             , scaling , units ]
    problem.inputs = np.array([
        [ 'wing_area'                    , 1894.7256221510588 , (   947.3628110755294 , 3221.0335576568 ) , 1894.7256221510588 , Units['ft^2']],
        [ 'thrust'                       , 34560.318725099605  , (  10368.095617529882 , 103680.95617529881 ) ,  34560.318725099605 , Units.lbf],
        [ 'cruise_altitude'              , 10670.731707317074 , ( 6707.317073170732 ,  43000/3.28   ) ,  10670.731707317074  , Units.m],
        [ 'takeoff_weight_guess'         , 226000*.3048 ,  ( 216000*.3048 ,   196703.85487528343)   ,   226000*.3048 , Units.kg],
        [ 'wing_sweep'                   , 35        , (25     ,        45)     ,   35         , Units.deg],
        [ 'wing_toverc'                  , 0.095        , (.07   ,       .16)     ,     0.095    , Units.less],
        [ 'wing_aspect_ratio'            , 11        , ( 6    ,         14)    ,     11   , Units.less],
      #  [ 'fan_pressure_ratio'              ,   1.65     , ( 1.05    ,         1.7)     ,       1.65      , Units.less],
      #  [ 'cruise_mach'                  ,   .79       , (.65   ,    .85)     ,      .79        , Units.less],
        [ 'cruise_step'                  ,   2000 / 3.28, (200  ,     4000)   ,     2000/3.28   , Units.m   ],
        [ 'v2_vs'                        ,   1.2        ,  (1.2 ,   1.8)      ,     1.2         , Units.less]
    ])
    # -------------------------------------------------------------------
    # Objective
    # -------------------------------------------------------------------

    # throw an error if the user isn't specific about wildcards
    # [ tag, scaling, units ]
    problem.objective = np.array([
        #[ 'fuel_burn', 10000, Units.kg ] # Design range fuel burn
        ['mtowobj'  , 100000, Units.kg] # MTOW
    ])
    # -------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------
    
    # [ tag, sense, edge, scaling, units ]
    problem.constraints = np.array([
        [ 'takeoff_diff', '>', 0, 1, Units.less],
        [ 'approach_speed', '<', 69.42675435119999 , 69.42675435119999 , Units['m/sec']],
        [ 'max_throttle', '<', .95, .95, Units.less],
        [ 'takeoff_field_length', '<', 2699.0860365853664 , 2699.0860365853664 , Units.m],
        [ 'second_seg_grad', '>', .024, .024, Units.less],
        [ 'fuel_margin'    , '>',   .05, .05, Units.less]
        #[ 'wing_span'      , '<',   118/3.28, 118/3.28, Units.m]
    ])
    
    # -------------------------------------------------------------------
    #  Aliases
    # -------------------------------------------------------------------
    
    # [ 'alias' , ['data.path1.name','data.path2.name'] ]

    problem.aliases = [
        [ 'wing_area'                        ,   ['vehicle_configurations.*.wings.main_wing.areas.reference',
                                                  'vehicle_configurations.*.reference_area'                              ]],
        [ 'cruise_altitude'                  ,    'vehicle_configurations.*.cruise_altitude'                              ],
        [ 'cruise_mach'                      ,    'vehicle_configurations.*.cruise_mach'                                  ],
        [ 'fuel_burn'                        ,    'summary.base_mission_fuelburn'                                         ],
        [ 'design_range_fuel_margin'         ,    'summary.max_zero_fuel_margin'                                          ],
        [ 'approach_speed'                   ,     'summary.approach_Speed'                                               ],
        [ 'max_throttle'                     ,      'summary.max_throttle'                                                ],  
        [ 'thrust'                           ,     ['vehicle_configurations.*.propulsors.turbofan.thrust.total_design',
                                                    'vehicle_configurations.*.propulsors.turbofan.thrust.design_thrust'  ]],
        [ 'takeoff_field_length'             ,     'summary.takeoff_field_length'                                         ],
        [ 'takeoff_diff'                     ,     'summary.takeoff_diff'                                                 ],
        [ 'takeoff_weight_guess'             ,           ['vehicle_configurations.*.mass_properties.max_takeoff',
                                                              'vehicle_configurations.*.mass_properties.takeoff'         ]],  
        ['second_seg_grad'                   ,     'summary.second_seg_grad'                                              ],
        [ 'fuel_margin'                      ,      'summary.fuel_margin'                                                 ],
        [ 'wing_sweep'                       ,      'vehicle_configurations.*.wings.main_wing.sweeps.quarter_chord'       ],
        [ 'wing_toverc'                      ,      'vehicle_configurations.*.wings.main_wing.thickness_to_chord'         ], 
        [ 'mtowobj'                          ,      'summary.takeoff_weight'                                              ],
        [ 'approach_speed_diff'              ,      'summary.approach_speed_diff'                                         ],
        [ 'max_throttle_diff'                ,      'summary.max_throttle_diff'                                           ],
        [ 'tofl_diff'                        ,      'summary.takeoff_length_diff'                                         ],
        [ 'fuel_margin_diff'                 ,      'summary.fuel_margin_diff'                                            ],
        [ 'second_seg_diff'                  ,      'summary.second_seg_diff'                                             ],
        [ 'takeoff_diff_lower'               ,      'summary.takeoff_diff_lower'                                          ],
        [ 'fuel_margin_no_reserve'           ,      'summary.takeoff_error'                                               ],
        [ 'wing_aspect_ratio'                ,      'vehicle_configurations.*.wings.main_wing.aspect_ratio'               ],
        [ 'wing_span'                        ,      'vehicle_configurations.base.wings.main_wing.spans.projected'         ],
        [ 'landing_diff'                     ,      'summary.landing_diff'                                                ],
        [ 'mzfw_diff'                        ,      'summary.mzfw_diff'                                                   ],
        [ 'fan_pressure_ratio'               ,      'vehicle_configurations.*.propulsors.turbofan.fan.pressure_ratio'     ],
        [ 'cruise_step'                      ,      'vehicle_configurations.*.cruise_step'                                ],
        [ 'v2_vs'                            ,      'vehicle_configurations.takeoff.V2_VS_ratio'                          ]                                                                                                                                                                 
                                                                                                                                                                 
    ]     
    
    # -------------------------------------------------------------------
    #  Vehicles
    # -------------------------------------------------------------------
    nexus.vehicle_configurations = Vehicles.setup()
    
    # -------------------------------------------------------------------
    #  Analyses
    # -------------------------------------------------------------------
    nexus.analyses = Analyses.setup(nexus.vehicle_configurations)

    nexus.procedure = Procedure.setup()
    #nexus.procedure = Procedure_MTOWConverge.setup()

    # -------------------------------------------------------------------
    #  Missions
    # -------------------------------------------------------------------
    nexus.missions = Missions.setup(nexus.analyses,nexus.vehicle_configurations)
    
    # -------------------------------------------------------------------
    #  Procedure
    # -------------------------------------------------------------------    
    
    # -------------------------------------------------------------------
    #  Summary
    # -------------------------------------------------------------------    
    nexus.summary = Data()
    nexus.total_number_of_iterations = 0
    return nexus
    
def variable_sweep(problem):    

    number_of_points = 5
    outputs     = carpet_plot(problem, number_of_points, 0, 0)  #run carpet plot, suppressing default plots
    inputs      = outputs.inputs
    objective   = outputs.objective
    constraints = outputs.constraint_val
    plt.figure(0)
    CS   = plt.contourf(inputs[0,:],inputs[1,:], objective, 20, linewidths=2)
    cbar = plt.colorbar(CS)

    cbar.ax.set_ylabel('fuel burn (kg)')
    CS_const = plt.contour(inputs[0,:],inputs[1,:], constraints[0,:,:])
    plt.clabel(CS_const, inline=1, fontsize=10)
    cbar = plt.colorbar(CS_const)
    cbar.ax.set_ylabel('Fuel Margin')
    CS_const = plt.contour(inputs[0,:],inputs[1,:], constraints[1,:,:])
    plt.clabel(CS_const, inline=1, fontsize=10)
    cbar = plt.colorbar(CS_const)
    cbar.ax.set_ylabel('Approach Speed (m/s)')
    CS_const = plt.contour(inputs[0,:],inputs[1,:], constraints[2,:,:])
    plt.clabel(CS_const, inline=1, fontsize=10)
    cbar = plt.colorbar(CS_const)
    cbar.ax.set_ylabel('Max Throttle Setting')
    plt.xlabel('Wing Area (sqft)')
    plt.ylabel('Thrust (Newtons)')
    
    plt.legend(loc='upper left')  
    plt.show(block=True)    
    
    return

if __name__ == '__main__':
    main()
