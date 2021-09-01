import matplotlib.pyplot as plt
import numpy as np

data = np.load('/Users/vlb9398/Downloads/kms_longevity_test_090121.npy')
tele_pa = data[:,1]
kms_pa = data[:,2]
utc = data[:,0]
time = data[:,3]

plt.scatter(time,kms_pa,color='red',label = 'kms-pa')
plt.scatter(time,tele_pa,color='blue',label = 'tele-pa')
# plt.plot(time,kms_pa,label = 'kms-pa',color='red')
# plt.plot(time,tele_pa,label = 'tele-pa',color='blue')
plt.legend()
plt.xlabel('Telescope Time [UTC]')
plt.ylabel('Parallactic Angle [deg]')
plt.grid()
plt.show()
