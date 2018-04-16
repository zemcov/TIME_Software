#!/usr/bin/python
import mce_data
import matplotlib.pyplot as plt
import sys
sys.path.append('/usr/mce/mce_script/python')

f = mce_data.MCEFile('/data/cryo/current_data/temp.000')
d = f.Read(row_col=True, unfilter='DC').data
print d.shape


i = 0
T = range(d.shape[0]) #row numbers
for i in range(d.shape[1]):
	plt.plot(T,d[:,0])

print(d[:,0].shape)
print(len(d[:,0]))
plt.show()
