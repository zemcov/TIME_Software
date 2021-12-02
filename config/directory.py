import os

repo_dir = os.path.abspath(os.path.join(__file__,'..','..')) # Auto-detect the directory where the repo is
netcdf_dir = '/data/netcdffiles/' #the directory for the netcdf files
master_dir = repo_dir + '/main/' # the main directory for the time software ex: path/to/TIME_Software/main/
mce_dir_template = '/data/mce%i/'
mce0_dir = mce_dir_template % 0 #the directory where you want to store mce0 data
mce1_dir = mce_dir_template % 1 #the directory where you want to store mce1 data
temp_dir = repo_dir + '/main/tempfiles/' #the directory for tempfiles ex: path/to/TIME_Software/main/tempfiles/
hk_dir = '/data/hk/' #the directory where you want to store hk data
lc_data_dir = '/data/lc_netcdffiles/'
time_analysis = '/home/time/time_analysis/py/timefpu/'
temp_lc = temp_dir + 'temp_lc/'
# Ensure the main directories exist upon import
for d in [mce0_dir, mce1_dir, temp_dir, hk_dir]:
	try:
		os.makedirs(d)
	except OSError:
		pass # Already exists, or bad permissions

	# assert os.path.isdir(d), "Failed to locate or create a needed folder '" + d + "', are permissions set properly?  Probably you need to change the owner of the parent folder."

if __name__ == '__main__':
	print("Repo dir: " + repo_dir)
