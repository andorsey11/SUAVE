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
    #output = problem.objective()
    
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
    #print('Nacelle Diameter (in)', "%.1f" % problem.summary.nacelle_d)
    #print('Engine Length (in)', "%.1f" % problem.summary.engine_length)

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
        [ 'wing_area'                    , 2967.3304221104936 , (   1483.6652110552468 , 5044.461717587839 ) , 2967.3304221104936 , Units['ft^2']],
        [ 'thrust'                       , 69395.61276404613  , (  20818.683829213838 , 208186.83829213842 ) ,  69395.61276404613 , Units.lbf],
        [ 'cruise_altitude'              , 10670.731707317074 , ( 6707.317073170732 ,  43000/3.28   ) ,  10670.731707317074  , Units.m],
        [ 'takeoff_weight_guess'         , 167649.51474307143 ,  ( 83824.75737153571  ,   335299.02948614286)   ,   167649.51474307143 , Units.kg],
        [ 'wing_sweep'                   , 21.234738088681492        , (5     ,        45)     ,   21.234738088681492         , Units.deg],
        [ 'wing_toverc'                  , 0.123327597944601        , (.07   ,       .16)     ,     0.123327597944601    , Units.less],
        [ 'wing_aspect_ratio'            , 8.099202382429208        , ( 6    ,         14)    ,     8.099202382429208   , Units.less],
        [ 'econ_takeoff_weight_guess'    , 134119.61179445716 ,  ( 50294.854422921424  ,   251474.27211460716)   ,   134119.61179445716 , Units.kg],
        [ 'cruise_step'                  ,   2000 / 3.28, (200  ,     4000)   ,     2000/3.28   , Units.m   ],
        [ 'v2_vs'                        ,   1.2        ,  (1.2 ,   1.8)      ,     1.2         , Units.less],
        [ 'fan_pressure_ratio'           ,   1.7       ,   (1.4, 2.5)        ,     1.2         , Units.less],
        [ 'bypass_factor'                ,   .99       ,   (.65, 1)        ,     .99        , Units.less],
        [ 'wing_origin'                  ,   .4       ,   (.1, .6)        ,    .5        , Units.less],
        [ 'econ_cruise_altitude'         ,   20000/3.28    , (   10000/3.28   ,    28000/3.28   ) ,   20000/3.28  , Units.m],
        #[ 'econ_cruise_step'             ,   1 / 3.28, (200  ,     4000)   ,     2000/3.28   , Units.m   ]
    ])
    # -------------------------------------------------------------------
    # Objective
    # -------------------------------------------------------------------

    # throw an error if the user isn't specific about wildcards
    # [ tag, scaling, units ]
    problem.objective = np.array([
        #[ 'fuel_burn', 10000, Units.kg ] # Design range fuel burn
       # ['mtowobj'  , 100000, Units.kg] # MTOW
        ['econ_fb'   , 10000, Units.kg] # econ range fb
    ])
    # -------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------
    # [ tag, sense, edge, scaling, units ]
    problem.constraints = np.array([
        [ 'takeoff_diff', '>', 0, 1, Units.less],
        [ 'approach_speed', '<', 70.4864750292 , 70.4864750292 , Units['m/sec']],
        [ 'max_throttle', '<', .95, .95, Units.less],
        [ 'takeoff_field_length', '<', 2839.3468597560977 , 2839.3468597560977 , Units.m],
        [ 'second_seg_grad', '>', .024, .024, Units.less],
        [ 'fuel_margin'    , '>',   .05, .05, Units.less],
        [ 'cg_error'       ,  '>', -.01 , .01, Units.less],
        [ 'cg_error_neg'   ,  '<',  .01 ,  .01, Units.less],
        [ 'econ_takeoff_diff'   ,  '>', -.01 , .01, Units.less],
        [ 'econ_takeoff_diff_neg'   ,  '<',  .01 ,  .01, Units.less],
        [ 'max_throttle_econ', '<', .95, .95, Units.less]
        #[ 'wing_span'      , '<',   118/3.28, 118/3.28, Units.m]
    ])
    
    # -------------------------------------------------------------------
    #  Aliases
    # -------------------------------------------------------------------
    
    # [ 'alias' , ['data.path1.name','data.path2.name'] ]
    problem.aliases = [
        [ 'wing_area'                        ,   ['vehicle_configurations.*.wings.main_wing.areas.reference',
                                                  'vehicle_configurations.*.reference_area'                              ]],
        [ 'cruise_altitude'                  ,    'vehicle_configurations.base.cruise_altitude'                              ],
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
        [ 'wing_sweep'                       ,      ['vehicle_configurations.*.wings.main_wing.sweeps.quarter_chord',
                                                    'vehicle_configurations.*.wings.main_wing.sweeps.leading_edge',
                                                    'vehicle_configurations.*.wings.main_wing.sweeps.trailing_edge'      ]],
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
        [ 'cruise_step'                      ,      'vehicle_configurations.base.cruise_step'                             ],
        [ 'econ_cruise_step'                      ,      'vehicle_configurations.econ.cruise_step'                        ],
        [ 'v2_vs'                            ,      'vehicle_configurations.takeoff.V2_VS_ratio'                          ],
        [ 'bypass_ratio'                     ,      'vehicle_configurations.*.propulsors.turbofan.bypass_ratio'           ],                                                                                                                                                                  
        [ 'bypass_factor'                    ,      'vehicle_configurations.*.propulsors.turbofan.bypass_factor'          ],                                                                                                                                                                  
        [ 'cg_error'                         ,      'summary.cg_error'                                                    ],                                                                                                                                                                  
        [ 'cg_error_neg'                     ,      'summary.cg_error_neg'                                                ],                                                                                                                                                                  
        [ 'wing_origin'                      ,     'vehicle_configurations.*.wings.main_wing.origin_factor'               ],                                                                                                                                                                                                       
        [ 'econ_fb'                          ,     'summary.econ_mission_fuelburn'                                        ],                                     
        [ 'econ_takeoff_diff'                ,     'summary.takeoff_econ_diff'                                            ],
        [ 'econ_takeoff_diff_neg'            ,     'summary.takeoff_econ_diff_neg'                                        ],
        [ 'econ_takeoff_weight_guess'        ,       'vehicle_configurations.econ.mass_properties.takeoff'                ],   
        [ 'econ_cruise_altitude'             ,       'vehicle_configurations.econ.cruise_altitude'                        ],
        [ 'max_throttle_econ'                ,       'summary.max_throttle_econ'                                          ],

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
