# TIME_Software

*Description of Repo Branches*

**Master** <br>
  Formerly Caltech_testing , this branch will be the most up to date stable branch of the TIME software. Changes from Dev will be moved over once they are deamed stable. <br>

**Dev** <br>
  Formerly rit-dev, this branch is used for introducting and testing new code that has not yet been proven stable. Changes from this branch will be added to master frequently when they are deamed stable. <br>

**eng_2019** <br>
  Formerly Caltech_eng, this is a frozen copy of the software from the TIME 2019 engineering run. This is not to be modified without prior permission, since it is used to track changes to certain bugs that have yet to be resolved. <br>

**kms-dev** <br>
  This branch is used to test new features and updates to the software controlling the Kmirror System. It is in constant flux and should not be considered stable. <br>

**kms_working_copy** <br>
  This is a frozen copy of the Kmirror System software from its testing in the RIT lab from Nov 2018. It is not to be modified without prior permission. This code was is capable of replicating smooth tracking of the system in multiple modes, has the SICK safety system enabled for use with limit switches and emergency stop buttons, and can communicate by sockets to simulate command position inputs from a telescope. <br>

*Installation*

Now running on Python 3.x

sudo pip3 install PyQt5 pyqtgraph PyQtWebEngine termcolor hanging_threads netcdf4 astropy astroplan
