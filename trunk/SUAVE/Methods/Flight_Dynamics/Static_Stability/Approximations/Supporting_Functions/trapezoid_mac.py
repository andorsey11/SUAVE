# trapezoid_mac.py

# Created: Tim Momose, Feb 2014
# IN PROGRESS

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
import SUAVE
import numpy as np
from SUAVE.Attributes import Units as Units
from SUAVE.Structure import (
    Data, Container, Data_Exception, Data_Warning,
)


def trapezoid_mac(wing):
    """ mac = SUAVE.Methods.Flight_Dynamics.Static_Stability.Approximations.Supporting_Functions.trapezoid_mac(wing)
        This method computes the mean aerodynamic chord of a linearly tapered
        trapezoidal aerodynamic surface
        
        Inputs:
            wing - a data dictionary with the fields:
                area - planform area of the trapezoidal wing [meters**s]
                span - wing span [meters]
                taper - wing taper ratio [dimensionless]
               
        Outputs:
            mac - the mean aerodynamic chord of the wing (or equivalent trapezoid)
            [meters]
              
        Assumptions:
            Assumes a simple trapezoidal wing shape.
    """                 

    #Unpack inputs
    S = wing.area
    b = wing.span
    l = wing.taper
    
    #Compute root and tip chords
    mgc = S/b               #mean geometric chord
    c_r = mgc/(1-0.5*(1-l)) #root chord
    c_t = c_r*l             #tip chord
    
    #Compute mean aerodynamic chord
    mac = (2.0/3.0)*(c_r + c_t - c_r*c_t/(c_r + c_t))
    
    return mac
