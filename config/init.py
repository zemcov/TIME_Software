#!/usr/bin/python
# use this to program the parameters in the software

setting = 'IRC Line Scan' # 'Quasar Line Scan', 'OMC Map Small', 'OMC Map Large', 'IRC Line Scan'

if setting == 'Quasar Line Scan':
    tel_dict = {
                "inittel":'Yes', 
                "kmsonoff":'Yes', 
                "tel_scan":'1D Raster', 
                "coord_space":'RA', 
                "sec":'8', 
                "num_loop":'1000', # roughly 4.5 hours
                "map_size":'1', 
                "map_size_unit":'deg', 
                "map_len":'1', 
                "map_len_unit":'deg',
                "map_angle":'0',
                "map_angle_unit":'deg',
                "step":'.001',
                "step_unit":'deg',
                "coord1":'',
                "coord1_unit":'RA',
                "coord2":'',
                "coord2_unit":'DEC',
                "epoch":"J2000.0",
                "object":''
    }

elif setting == 'OMC Map Small':
    tel_dict = {
                "inittel":'Yes', 
                "kmsonoff":'Yes', 
                "tel_scan":'2D Raster', 
                "coord_space":'RA', 
                "sec":'4', 
                "num_loop":'1', 
                "map_size":'.4', 
                "map_size_unit":'deg', 
                "map_len":'.2', 
                "map_len_unit":'deg', 
                "map_angle":'0', 
                "map_angle_unit":'deg', 
                "step":'.001', 
                "step_unit":'deg', 
                "coord1":'05:35:14.50', 
                "coord1_unit":'RA', 
                "coord2":'-05:22:29.3', 
                "coord2_unit":'DEC', 
                "epoch":"J2000.0", 
                "object":'OMC1' 
    }

elif setting == 'OMC Map Large':
    tel_dict = {
                "inittel":'Yes', 
                "kmsonoff":'Yes', 
                "tel_scan":'2D Raster', 
                "coord_space":'RA', 
                "sec":'8', 
                "num_loop":'1', 
                "map_size":'.8', 
                "map_size_unit":'deg', 
                "map_len":'.8', 
                "map_len_unit":'deg', 
                "map_angle":'0', 
                "map_angle_unit":'deg', 
                "step":'.002', 
                "step_unit":'deg', 
                "coord1":'05:35:14.50', 
                "coord1_unit":'RA', 
                "coord2":'-05:22:29.3', 
                "coord2_unit":'DEC', 
                "epoch":"J2000.0", 
                "object":'OMC1' 
    }

elif setting == 'IRC Line Scan':
    tel_dict = {
                "inittel":'Yes', 
                "kmsonoff":'Yes', 
                "tel_scan":'2D Raster', 
                "coord_space":'RA', 
                "sec":'4', 
                "num_loop":'150', # roughly 20 minutes 
                "map_size":'.4', 
                "map_size_unit":'deg', 
                "map_len":'1', 
                "map_len_unit":'deg', 
                "map_angle":'0', 
                "map_angle_unit":'deg', 
                "step":'.001', 
                "step_unit":'deg', 
                "coord1":'09:47:57.40', 
                "coord1_unit":'RA', 
                "coord2":'+13:16:43.6', 
                "coord2_unit":'DEC', 
                "epoch":"J2000.0", 
                "object":'IRC+10216' 
    }

else:
    tel_dict = {
                "inittel":'Yes', # 'Yes' or 'No'
                "kmsonoff":'Yes', # 'Yes' or 'No'
                "tel_scan":'1D Raster', # Observing mode: '1D Raster' or '2D Raster
                "coord_space":'RA', # Constant coordinate of scan: 'RA', 'DEC', 'AZ', or 'ALT'
                "sec":'', # Number of seconds for individual scans to last
                "num_loop":'', # Number of scans to perform in 1D scan mode
                "map_size":'', # Length of scan along the constant coordinate
                "map_size_unit":'deg', # 'deg', 'arcmin', 'arcsec'
                "map_len":'', # Length of 2D scan perpendicular to the constant coordinate axis
                "map_len_unit":'deg', # 'deg', 'arcmin', 'arcsec'
                "map_angle":'', # Number
                "map_angle_unit":'deg', # 'deg', 'arcmin', 'arcsec'
                "step":'', # Step size of rows for 2D scan
                "step_unit":'deg', # 'deg', 'arcmin', 'arcsec'
                "coord1":'', # Coordinates
                "coord1_unit":'RA', # Units of coord1 - 'RA' or 'AZ'
                "coord2":'', # Coordinates
                "coord2_unit":'DEC', # Unites of coord2 - 'DEC' or 'ALT'
                "epoch":"J2000.0", # Epoch: 'J2000.0' or 'Apparent'
                "object":'' # Target name
    }





# tel_dict = {
# "inittel":"Yes",
# "kmsonoff":"Yes",
# "tel_scan":"2D Raster",
# "coord_space":"RA",
# "sec":"6",
# "num_loop":"2",
# "map_size":"0.5",
# "map_size_unit":"deg",
# "map_len":"0.5", #only need for 2D map
# "map_len_unit":"deg",
# "map_angle":"0",
# "map_angle_unit":"deg",
# "step":"0.005",
# "step_unit":"deg",
# "coord1":"22:25:12.9",
# "coord1_unit":"RA",
# "coord2":"-10:56:08.8",
# "coord2_unit":"DEC",
# "epoch":"J2000.0",
# "object":"Jupiter"
# }

# ===================================
mce_dict = {
"observer":"VLB",
"mceson":"MCE0",
"datamode":"Mixed Mode (25:7)",
"readoutcard":"All",
"framenumber":"1350000",
"alpha":"0.1",
"channeldelete":"No",
"timeinterval":"60",
"showmcedata":"Yes"

}
