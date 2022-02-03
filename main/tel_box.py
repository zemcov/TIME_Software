import astropy.units as u
from astropy.time import Time as thetime
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, TETE
import numpy as np
from datetime import datetime

def draw_box(coord1,coord1_unit,coord2,coord2_unit,coord_space,map_size,map_size_unit,map_len,map_len_unit,epoch) :

    location = EarthLocation.from_geodetic(lon =-111.61485416666*u.deg, lat =31.95333333333*u.deg, height=1914*u.m)
    time = thetime(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + 7*u.h
    frame = TETE(obstime=time, location=location)

    c1 = str(coord1).split(':')
    c2 = str(coord2).split(':')

    if str(coord1_unit) == 'RA' and str(coord2_unit) == 'DEC' :
        # rpk: telesocpe is going to give us data in apparent coordinates, so we'll need to convert the box to those units
        if epoch == 'J2000.0':
            old_coord = SkyCoord(c1[0]+'h'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s').transform_to(frame)
        elif epoch == 'Apparent':
            old_coord = SkyCoord(c1[0]+'h'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')
        else:
            raise ValueError('tel_box does not recognize epoch provided')
        coord1 = old_coord.ra.degree
        coord2 = old_coord.dec.degree
    else :
        old_coord = AltAz(c1[0]+'d'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')
        coord1 = old_coord.az.degree
        coord2 = old_coord.alt.degree

    if str(map_len_unit) != 'deg' or str(map_size_unit) != 'deg':
        raise ValueError('tel_box expecting units in degrees')
    else :
        map_len = float(map_len)
        map_size = float(map_size)
    
    if coord_space == 'RA' or coord_space == 'AZ':
        x_size = map_size
        y_size = map_len
    elif coord_space == 'DEC' or coord_space == 'ALT':
        x_size = map_len
        y_size = map_size

    # rpk: Need to correct map ra dimension for the cosine of dec
    if str(coord1_unit) == 'RA':
        x_size = x_size/np.cos(coord2*np.pi/180)

    box_leftx = np.linspace((coord1 - (x_size/2.0)) , (coord1 - (x_size/2.0)) , 100)
    box_lefty = np.linspace((coord2 - (y_size/2.0)) , (coord2 + (y_size/2.0)) , 100)

    box_rightx = np.linspace((coord1 + (x_size/2.0)) , (coord1 + (x_size/2.0)) , 100)
    box_righty = np.linspace((coord2 - (y_size/2.0)) , (coord2 + (y_size/2.0)) , 100)

    box_topx = np.linspace((coord1 - (x_size/2.0)) , (coord1 + (x_size/2.0)) , 100)
    box_topy = np.linspace((coord2 + (y_size/2.0)) , (coord2 + (y_size/2.0)) , 100)

    box_botx = np.linspace((coord1 - (x_size/2.0)) , (coord1 + (x_size/2.0)) , 100)
    box_boty = np.linspace((coord2 - (y_size/2.0)) , (coord2 - (y_size/2.0)) , 100)

    return box_leftx,box_lefty,box_rightx,box_righty,box_topx,box_topy,box_botx,box_boty
