# wing_planform.py
#
# Created:  Apr 2014, T. Orra
# Modified: Jan 2016, E. Botero

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import numpy as np

# ----------------------------------------------------------------------
#  Methods
# ----------------------------------------------------------------------
def wing_planform_BWB(wing):
    """Computes standard wing planform values.

    Assumptions:
    Trapezoidal wing with no leading/trailing edge extensions

    Source:
    None

    Inputs:
    wing.
      areas.reference          [m^2]
      taper                    [-]
      sweeps.quarter_chord     [radians]
      aspect_ratio             [-]
      thickness_to_chord       [-]
      dihedral                 [radians]
      vertical                 <boolean> Determines if wing is vertical
      symmetric                <boolean> Determines if wing is symmetric
      origin                   [m]       x, y, and z position
      high_lift                <boolean> Determines if wing is in a high lift configuration
      flaps.                             Flap values are only used if high lift is True
        span_start             [-]       Span start position (.1 is 10% span)
        span_end               [-]       Span end position (.1 is 10% span)
        chord                  [-]       Portion of wing chord used (.1 is 10% chord)

    Outputs:
    wing.
      chords.root              [m]
      chords.tip               [m]
      chords.mean_aerodynamics [m]
      areas.wetted             [m^2]
      areas.affected           [m^2]
      spans.projected          [m]
      aerodynamic_center       [m]      x, y, and z location
      flaps.chord_dimensional  [m]
      flaps.area               [m^2]
        

    Properties Used:
    N/A
    """      
    
    # unpack
    num_segments              = len(wing.Segments.keys())     
    quartchordsweep = 0
    mac = 0
    sref = 0
    cabinarea = 0
    aftcenterbody = 0
    quartchordlocation = 0
    swet = 0
    fuelvolume = 0
    for i_segs in range(num_segments):
        segment = wing.Segments[i_segs]

        if i_segs == num_segments-1:
            continue 
        nextseg = wing.Segments[i_segs + 1]    
        #Calculate effective quarter chord sweep
        srefseg =  ((segment.root_chord_percent + nextseg.root_chord_percent)*wing.chords.root)/2 * ((nextseg.percent_span_location - segment.percent_span_location )* wing.spans.projected)
        sref += srefseg
        #Quarter chord location from wing origin
        quartchordlocation += (nextseg.percent_span_location - segment.percent_span_location ) * wing.spans.projected * np.tan(segment.sweeps.quarter_chord)

        #Sum (MAC1 * Seg Area1 + MAC2 * Seg Area2+ ...) / (Area1 + Area2 + ...)
        taper = nextseg.root_chord_percent / segment.root_chord_percent
        macseg = 2/3 * segment.root_chord_percent *((1+taper+taper**2)/(1+taper))* wing.chords.root
        mac += macseg * srefseg
        #Aft centerbody is defined as area behind 70% chord for the first 5 segments (index of 4)
        swet += 2 * srefseg *  (1.0 + 0.2*segment.thickness_to_chord)
        #### Linear t/c and sweep
        if (i_segs > 0 and i_segs < 4): ## Sections 2,3,4 are linear between 1 and 5 design variables
            #(Segment 5 - Segment 1) / span * span_delta + previous
            segment.thickness_to_chord = ((wing.Segments[4].thickness_to_chord - wing.Segments[0].thickness_to_chord) /  (wing.Segments[4].percent_span_location - wing.Segments[0].percent_span_location)) * (segment.percent_span_location - wing.Segments[i_segs-1].percent_span_location) + wing.Segments[i_segs-1].thickness_to_chord        
            segment.sweeps.quarter_chord = ((wing.Segments[4].sweeps.quarter_chord - wing.Segments[0].sweeps.quarter_chord) /  (wing.Segments[4].sweeps.quarter_chord - wing.Segments[0].sweeps.quarter_chord)) * (segment.sweeps.quarter_chord - wing.Segments[i_segs-1].sweeps.quarter_chord) + wing.Segments[i_segs-1].sweeps.quarter_chord        
        elif (i_segs == 5): ## Section 6 is linear between 5 and 7. 
            segment.thickness_to_chord = ((wing.Segments[6].thickness_to_chord - wing.Segments[4].thickness_to_chord) /  (wing.Segments[6].percent_span_location - wing.Segments[4].percent_span_location)) * (segment.percent_span_location - wing.Segments[i_segs-1].percent_span_location) + wing.Segments[i_segs-1].thickness_to_chord                    
            segment.sweeps.quarter_chord = ((wing.Segments[6].sweeps.quarter_chord - wing.Segments[4].sweeps.quarter_chord) /  (wing.Segments[6].sweeps.quarter_chord - wing.Segments[4].sweeps.quarter_chord)) * (segment.sweeps.quarter_chord - wing.Segments[i_segs-1].sweeps.quarter_chord) + wing.Segments[i_segs-1].sweeps.quarter_chord                    
        elif (i_segs == 7): ##Tip is just Section 7
            segment.thickness_to_chord = wing.Segments[6].thickness_to_chord 
            segment.sweeps.quarter_chord = wing.Segments[6].sweeps.quarter_chord 
        if i_segs <= 3:
            aftcenterbody += srefseg * .3
                    #Next check the available cabin area, defined as thickness above 8.25 ft per Bradley. This is only for sections 1-4
            sectionroot_t = segment.root_chord_percent * wing.chords.root
            sectiontip_t = nextseg.root_chord_percent * wing.chords.root
            if sectionroot_t > 8.25 / 3.28084 and sectiontip_t > 8.25 / 3.28084:
                cabinarea += srefseg * .7 # Give it everything but the aft centerbody
            elif sectionroot_t < 8.25 / 3.28084 and sectiontip_t < 8.25/3.28084:
                cabinarea += 0 # give it nothing
            elif sectionroot_t > 8.25 / 3.28084 and sectiontip_t < 8.25/3.28084:
                # Need to figure out how much of this segment is good

                # Assume the t/c goes linearly as does chord, which gives a quadratic
                #  t (y) = (t/c slope * chord slope )*y**2 + ((root t - tip t)-(t/c slope * chord slope)*y + root chord
                # A  = (t/c slope * chord slope), B = (root t - tip t) - A, C = root chord
                tcslope = (nextseg.thickness_to_chord - segment.thickness_to_chord) # Do it all with length 1
                chordslope = (nextseg.root_chord_percent - segment.root_chord_percent) * wing.chords.root
                A = tcslope * chordslope
                B = ((segment.root_chord_percent - nextseg.root_chord_percent)* wing.chords.root) - A
                C = segment.root_chord_percent * wing.chords.root
                disc = B**2 - 4 *A*C
                if A == 0:
                    #Its linear, either in chord or t/c
                    percentspan = (C-8.25/3.2808) / B
                elif disc < 0:
                    #Something went wrong and its imaginary, so just continue
                    continue
                else:
                    #Call 8.25 ft 2.5 meters, solve when A /= 0
                    x1 = (-1*np.sqrt((-4*A*C) + 10*A+B**2) -B) / (2*A)
                    x2 = (np.sqrt((-4*A*C) + 10*A+B**2) -B) / (2*A)
                    percentspan = max(x1,x2) # Take the positive one
                #Find the new area now

                chordavail = (segment.root_chord_percent* wing.chords.root) -  (segment.root_chord_percent - nextseg.root_chord_percent)* wing.chords.root* percentspan * 0.7
                cabinarea += (chordavail + segment.root_chord_percent * wing.chords.root)/2 * percentspan * ((nextseg.percent_span_location - segment.percent_span_location )* wing.spans.projected)
            elif sectionroot_t < 8.25 / 3.28084 and sectiontip_t > 8.25/3.28084:
                cabinarea += 0 # give it nothing, this is mostly to catch weird optimizer choices
        else:
        #add to fuel volume, this is outboard    average t * c between spars * span + knockdowns
            fuelvolume += (((segment.thickness_to_chord * segment.root_chord_percent* wing.chords.root) * (segment.root_chord_percent * wing.chords.root*(.4))) + ((nextseg.thickness_to_chord * nextseg.root_chord_percent* wing.chords.root) * (nextseg.root_chord_percent * wing.chords.root*(.4)))) / 2 * ((nextseg.percent_span_location - segment.percent_span_location )* wing.spans.projected* .9 )  
    
    mac = mac / sref
    quartchordsweep = np.arctan(quartchordlocation / wing.spans.projected)
    #Pack it up
    wing.areas.reference = sref
    wing.sweeps.quarter_chord = quartchordsweep
    wing.aspect_ratio = wing.spans.projected**2 / wing.areas.reference
    wing.cabinarea = cabinarea
    wing.aft_centerbody_area = aftcenterbody
    wing.cabin_area_available = cabinarea
    wing.chords.mean_aerodynamic = mac
    #wing.chords.root = design variable 
    wing.chords.tip =  wing.chords.root * wing.taper
    wing.areas.wetted = swet
    wing.areas.affected = 0
    wing.flaps.chord_dimensional = 0 
    wing.flaps.area = 0
    wing.fuel_volume = fuelvolume 
    
    return wing


# ----------------------------------------------------------------------
#   Module Tests
# ----------------------------------------------------------------------
# this will run from command line, put simple tests for your code here
if __name__ == '__main__':

    from SUAVE.Core import Data,Units
    from SUAVE.Components.Wings import Wing
        
    #imports
    wing = Wing()
    
    wing.areas.reference        =  10.
    wing.taper                  =  0.50
    wing.sweeps.quarter_chord   =  45.  * Units.deg
    wing.aspect_ratio           =  10.
    wing.thickness_to_chord     =  0.13
    wing.dihedral               =  45.  * Units.deg
    wing.vertical               =  1
    wing.symmetric              =  0
    
    wing.flaps.chord = 0.28
    wing.flaps.span_start = 0.50
    wing.flaps.span_end   = 1.00

    wing_planform(wing)
    print(wing)
