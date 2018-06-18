# Description
  The purpose of this program is to live graph the data being processed by the
  MCE for real-time surveillance of the system and verification the data is
  getting collected correctly. Additionally, the data is archived in a NETCDF
  database to be analyzed later. These two tasks are accomplished by using
  the pyqtgraph and NETCDF4 to generate the GUI and to archive the data
  respectively.

# Installation
  To install the required Python libraries to run this program, pip is needed

  numpy:
  pip install numpy (may need to run as sudo to fix permission errors)

  pyqtgraph:
  pip install pyqtgraph (may need to run as sudo to fix permission errors)

  NETCDF4:
  pip install netCDF4 (may need to run as sudo to fix permission errors)

# Starting the System
  To run the program, navigate to TIME_Software/cryo and run:
  python pyqtgui.py
  this should start the program, prompting for the different parameters required
  to run the MCE and the program. The different parameters are as follows:

  Observer: 3 initials of current user of program, defaults to JMB

  Datamode: Data mode to run MCE in, defaults to Error

  Readout Card: Readout card to pull data from, any of the 4 up to a maximum of
  two MCEs or All readout cards, defaults to MCE 1 RC 1

  Frame Number: Number of frames to run the MCE for, defaults to 1350000

  Data Rate: Rate for the MCE to collect data at, defaults to 45

  Delete Old Channels: Delete old channels on the live graph after the channel
  has been changed to reduce clutter, defaults to No

  After all the parameters have been set, press the Submit button to start live
  graphing.

#Live Graphing
  Once the submit button has been pressed and the parameters set are valid, the
  program will start live graphing the data depending on the parameters given.
  The top right graph is the current data being plotted, the middle graph being
  the last interval of data plotted, currently set to 120 seconds. The bottom is
  the heatmap of the channels, with the 8 channels going horizontally and the 32
  rows going vertically. The left side under the Submit and Quit buttons is a
  list of all the parameters set including the UTC time the live graphing
  started. Below that is the ability to change channels for the live graphing,
  and if all MCEs are picked, there would also be a dropdown menu for changing
  the current readout card. The bottom left is data from the K-Mirror, however
   currently it just outputs random integers as that has not been fully
   implemented yet.
