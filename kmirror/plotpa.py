import matplotlib.pyplot as plt
tele_pa = []
kms_pa = []
pa_result = open('pa.txt', 'r')
for line in pa_result :
    tele,kms = pa_results.readline().strip().split(' ')
    tele_pa.append(tele)
    kms_pa.append(kms)

plt.plot(time,kms_pa,'k--',label = 'kms-pa')
plt.plot(time,tele_pa,'r--',label = 'tele-pa')
plt.xlabel('Telescope Time [UTC]')
plt.ylabel('Parallactic Angle [deg]')
plt.grid()
plt.show()
