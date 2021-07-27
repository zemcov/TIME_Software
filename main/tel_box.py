import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle, Latitude, Longitude, ICRS, Galactic, FK4, FK5
from astroplan import Observer
import numpy as np
from datetime import datetime
from termcolor import colored

def draw_box(coord1,coord1_unit,coord2,coord2_unit,coord_space,map_size,map_size_unit,map_len,map_len_unit) :
    '''
    coord1 - right ascension of object of interest
    coord1_unit - degrees / arcminutes / arcseconds
    coord2 - declination of object of interest
    coord2_unit - degrees / arcminutes / arcseconds
    coord_space - The coordinate that will be held constant (RA / DEC / ALT / AZ)
    map_size - the size of the map (generally assumed to be a square -> map_len**2)
    map_size_unit - degrees / arcminutes / arcseconds
    map_len - length of the map
    map_len_unit - degrees / arcminutes / arcseconds
    '''
    #location of Kitt Peak hard coded right now
    location = EarthLocation.from_geodetic(lon =-111.5947*u.deg, lat =31.95844*u.deg, height=2097.024*u.m)
    kittpeak = Observer(location=location, name='kitt peak')
    time = thetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    c1 = str(coord1).split(':')
    c2 = str(coord2).split(':')
    if str(coord1_unit) == 'RA' and str(coord2_unit) == 'DEC' :
        old_coord = SkyCoord(c1[0]+'h'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')
        coord1 = old_coord.ra.degree
        coord2 = old_coord.dec.degree
    else :
        old_coord = AltAz(c1[0]+'d'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')
        coord1 = old_coord.az.degree
        coord2 = old_coord.alt.degree

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

    box_leftx = np.linspace((coord1 - (map_size/2.0)) , (coord1 - (map_size/2.0)) , 100)
    box_lefty = np.linspace((coord2 - (map_len/2.0)) , (coord2 + (map_len/2.0)) , 100)

    box_rightx = np.linspace((coord1 + (map_size/2.0)) , (coord1 + (map_size/2.0)) , 100)
    box_righty = np.linspace((coord2 - (map_len/2.0)) , (coord2 + (map_len/2.0)) , 100)

    box_topx = np.linspace((coord1 - (map_size/2.0)) , (coord1 + (map_size/2.0)) , 100)
    box_topy = np.linspace((coord2 + (map_len/2.0)) , (coord2 + (map_len/2.0)) , 100)

    box_botx = np.linspace((coord1 - (map_size/2.0)) , (coord1 + (map_size/2.0)) , 100)
    box_boty = np.linspace((coord2 - (map_len/2.0)) , (coord2 - (map_len/2.0)) , 100)

    return box_leftx,box_lefty,box_rightx,box_righty,box_topx,box_topy,box_botx,box_boty
