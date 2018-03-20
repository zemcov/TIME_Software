from netCDF4 import Dataset
# creating a file for GUI parameters
gui_params = Dataset("gui_data.nc","w",format="NETCDF4")
#when done adding data....
gui_params.close()
