import mce_data_jon
import os

os.path.join('/home/time/Desktop/time-data/mce1/')

file = '/home/time/Desktop/time-data/mce1/temp.010'
f = mce_data_jon.MCEFile(file)
h = f.Read(row_col=True, unfilter='DC', all_headers=True)

keys = []
values = []
frame_num = []
print(len(h.headers))
for i in range(len(h.headers)):
    for key,value in h.headers[i].items():
        if key == 'sync_box_num' :
            frame_num.append(value)
print(frame_num)
