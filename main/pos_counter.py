# this is the calculator for determining number of linear scans
# to be run and automates starting position for map at the bottom

import astropy.units as u
from astropy.coordinates import SkyCoord, AltAz
from termcolor import colored
import sys

def scan_params(type,coord_space,map_size,map_size_unit,map_len,map_len_unit,coord1,coord1_unit,coord2,coord2_unit,step,step_unit):

    if str(step_unit) != 'deg':
        if str(step_unit) == 'arcmin' :
            step = float(step) / 60.0
        else :
            step = float(step) / 3600.0
    else :
        step = float(step)

    if str(map_len_unit) != 'deg':
        if str(map_len_unit) == 'arcmin' :
            map_len = float(map_len) / 60.0
        else :
            map_len = float(map_len) / 3600.0
    else :
        map_len = float(map_len)

    if str(map_size_unit) != 'deg':
        if str(map_size_unit) == 'arcmin' :
            map_size = float(map_size) / 60.0
        else :
            map_size = float(map_size) / 3600.0
    else :
        map_size = float(map_size)

    if type == 1:
        num_loop = 1
    elif type == 2:
        num_loop = int(map_len / step) + 1

    # ============================================================================================

    ''' ######################################################################
    MIGHT STILL NEED TO PUT CHECKS ON POSITIVE AND NEGATIVE POSITION CHECKING
    WHEN ADDING STARTING VALUES TO POSITIONS
    #######################################################################'''

    c1 = str(coord1).replace(';',':').split(':')
    c2 = str(coord2).replace(';',':').split(':')

    if str(coord1_unit) == 'RA' and str(coord2_unit) == 'DEC' :
        old_coord = SkyCoord(c1[0]+'h'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')
        c = SkyCoord(ra = (map_size / 2.0)* u.degree, dec = (map_len / 2.0) * u.degree)
        if type == 1 :
            if coord_space == 'RA':
                sys.stdout.flush()
                start_coord1 = old_coord.ra.degree
                start_coord2 = old_coord.dec.degree
            else :
                start_coord1 = old_coord.ra.degree
                start_coord2 = old_coord.dec.degree

        elif type == 2:
            if coord_space == 'RA':
                start_coord1 = old_coord.ra.degree
                start_coord2 = (old_coord.dec - c.dec).degree
            elif coord_space == 'DEC':
                start_coord1 = (old_coord.ra - c.ra).degree
                start_coord2 = old_coord.dec.degree

    else :
        old_coord = AltAz(c1[0]+'d'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')
        c = AltAz(az = (map_size / 0.5)* u.degree, alt = (map_len / 0.5) * u.degree)
        if type == 1 :

            if coord_space == 'ALT':
                start_coord1 = (c.az - old_coord.az).degree
                start_coord2 = old_coord.alt.degree
            else :
                start_coord1 = c.az.degree
                start_coord2 = (c.alt - old_coord.alt).degree

        elif type == 2 :
            start_coord1 = (c.az - old_coord.az).degree
            start_coord2 = (c.alt - old_coord.alt).degree
            
    # ============================================================================================

    return num_loop,start_coord1,start_coord2
