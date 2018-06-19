# Description
  The purpose of this program is to live graph the data being processed by the
  MCE, K-Mirror, housekeeping, telescope and others for real-time surveillance of the system.
  The data being monitored is simultaneously stored in a NETCDF4 file format, with a dedicated retrieval script written to return the raw data arrays as well as the heatmap. These two tasks are accomplished by using the pyqtgraph and NETCDF4 anaconda package to generate the GUI and to archive the data respectively.


# Installation
  anaconda python 2.7 distribution is recommended for all sub-packages necessary
  (python 2.7 required for mce/mas software requirements)
  64-bit Linux installer (check this link for updated download https://www.anaconda.com/download/#linux)

  https://repo.anaconda.com/archive/Anaconda2-5.2.0-Linux-x86_64.sh

  see this link for included packages with anaconda install (will be out of date from newer versions)
  https://docs.anaconda.com/anaconda/packages/old-pkg-lists/2.3.0/py27

  pyqtgraph:
  pip install pyqtgraph

  NETCDF4:
  conda install -c anaconda netcdf4


# Files Installed
  pyqtgui.py: Main file, runs the GUI and is dependent on all other files

  takedata.py/takedataall.py: Reads/deletes MCE tempfiles and creates arrays of data for
  the graph/heatmap to plot with, different files depending on if 1 or All readout
  cards are being read respectively; also calls netcdf_trial functions to archive
  data, called by pyqtgui

  netcdf_trial.py: Creates and updates data in netCDF4 files, called by both pyqtgui
  and takedata/takedataall

  settings.py: Stores global variables for use by netcdf_trial and takedata/takedataall,
  called by all other files


# Starting the System
  To run the program, navigate to TIME_Software/Beta0.2 and run from the terminal:
  python pyqtgui.py

  this should start the program, prompting for the different parameters required
  to run the MCE and the program.


# Description of GUI Parameters (set by user)

  Observer: 3 initials of current user of program, defaults to JMB

  Datamode: Data mode to run MCE in, defaults to Error

  Readout Card: Readout card to pull data from, any of the 4 up to a maximum of
  two MCEs or All readout cards, defaults to MCE 1 RC 1

  Frame Number: Number of frames to run the MCE for, defaults to 1350000

  Data Rate: Rate for the MCE to collect data at, defaults to 45

  Time Interval: Amount of time the graph displays

  Delete Old Channels: Delete old channels on the live graph after the channel
  has been changed to reduce clutter, defaults to No

  After all the parameters have been set, press the Submit button to start live
  graphing.


# Live Graphing
  Once the submit button has been pressed and the parameters set are valid, the
  program will start live graphing the data depending on the parameters given.
  The top right graph is the current data being plotted, the middle graph being
  the last interval of data plotted. The bottom is the heatmap of the channels,
  with the 8 channels going horizontally and the 32 rows going vertically.
  The left side under the Submit and Quit buttons is a list of all the parameters
  set including the UTC time the live graphing started. Below that is the ability
  to change channels for the live graphing, and if all MCEs are picked, there
  would also be a dropdown menu for changing the current readout card. The bottom
  left is data from the K-Mirror, however currently it just outputs random integers
  as that has not been fully implemented yet.
