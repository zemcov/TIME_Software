# this is the calculator for determining number of linear scans
# to be run and automates starting position for map at the bottom

def scan_params(map_len,map_len_unit,coord1,coord1_unit,coord2,coord2_unit,step,step_unit):

    if str(step_unit) != 'arcsec':
        if str(step_unit) == 'arcmin' :
            step = float(step) * 60
        else :
            step = float(step) * 3600

    if str(map_len_unit) != 'arcsec':
        if str(map_len_unit) == 'arcmin' :
            map_len = float(map_len) * 60
        else :
            map_len = float(map_len) * 3600

    num_loop = int(float(map_len) // float(step))

    # ============================================================================================

    ''' ######################################################################
    MIGHT STILL NEED TO PUT CHECKS ON POSITIVE AND NEGATIVE POSITION CHECKING
    WHEN ADDING STARTING VALUES TO POSITIONS
    #######################################################################'''

    c1 = str(coord1).split(':')
    c2 = str(coord2).split(':')

    if str(coord1_unit) == 'RA' and str(coord2_unit) == 'DEC' :
        old_coord = SkyCoord(c1[0]+'h'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')
        c = SkyCoord(ra = (float(map_len // 3600 // 0.5))* u.degree, dec = (float(map_len // 3600 // 0.5)) * u.degree)

        start_coord1 = (c.ra + old_coord.ra).to_string()
        start_coord2 = (c.dec + old_coord.dec).to_string()

    else :
        old_coord = AltAz(c1[0]+'d'+c1[1]+'m'+c1[2]+'s', c2[0]+'d'+c2[1]+'m'+c2[2]+'s')
        c = AltAz(az = (float(map_len // 3600 // 0.5))* u.degree, alt = (float(map_len // 3600 // 0.5)) * u.degree)

        start_coord1 = (c.az + old_coord.az).to_string()
        start_coord2 = (c.alt + old_coord.alt).to_string()

    # ============================================================================================

    return num_loop,start_coord1,start_coord2
