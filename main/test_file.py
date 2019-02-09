import mce_data_jon
import os
import numpy as np

# os.path.join('/home/time/Desktop/time-data/mce1/')
#
# file = '/home/time/Desktop/time-data/mce1/temp.010'
# f = mce_data_jon.MCEFile(file)
# h = f.Read(row_col=True, unfilter='DC', all_headers=True)
#
# keys = []
# values = []
# frame_num = []
# print(len(h.headers))
# for i in range(len(h.headers)):
#     for key,value in h.headers[i].items():
#         if key == 'sync_box_num' :
#             frame_num.append(value)
# print(frame_num)

hk = np.load('/home/time/Desktop/hk_data.npy') # this contains hk time
hk_data = np.load('/home/time/Desktop/final_hk.npy')
utc_time = np.load('/home/time/Desktop/utc.npy') # this is from mce

''' Currently, the mce data is ahead of the housekeeping data by quite a lot. Like 3 files.'''

def test_hk():
    for i in range(len(utc_time)) :
        for j in range(len(hk[0])):
            for k in range(len(hk[0][0])) :
                if hk[j][0][k] != 0.0 :
                    if hk[j][0][k] == utc_time[i] :
                        hk_data[i] = hk[j,:,:]
                    print(hk[j][0][k],utc_time[i])

if __name__ == '__main__':
    test_hk()
