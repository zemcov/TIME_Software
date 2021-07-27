import numpy as np
from scipy.interpolate import interp1d

def cube_to_ts(det_time,tel_time,tel_ra,tel_dec,cube,cube_ra,cube_dec,
                    noise=None):
    # arguments:
    # - timestamps for detector readout data
    # - timestamps for telescope pointing data
    # - telescope ra
    # - telescope dec
    # - simulated data cube (axes in order of ra, dec, channels)
    # - cube ra bins
    # - cube dec bins
    # - (kwarg) noise sigma [either array-like w/ shape (channels,) or scalar]
    # returns: time series for all channels
    det_ra = interp1d(tel_time,tel_ra,fill_value='extrapolate')(det_time)
    det_dec = interp1d(tel_time,tel_dec,fill_value='extrapolate')(det_time)
    # needs max(cube_ra) > max(det_ra), max(cube_dec) > max(det_dec) to work
    det = cube[np.digitize(det_ra,cube_ra),np.digitize(det_dec,cube_dec)]
    if noise is not None: det+= np.random.normal(size=det.shape,scale=noise)
    return det

def quickmap(det_time,det_ts,tel_time,tel_ra,tel_dec,bins=(21,22)):
    # arguments:
    # - timestamps for detector readout data
    # - detector readout [shape should be (len(det_time),nchan)]
    # - timestamps for telescope pointing data
    # - telescope ra
    # - telescope dec
    # - (kwarg) number of bins in ra and dec to use for map
    # returns: ra bins, dec bins, integrated maps for all channels
    # nb: clearly unsuitable for mapping actual data due to lack of filtering
    ra_det = interp1d(tel_time,tel_ra,fill_value='extrapolate')(det_time)
    dec_det = interp1d(tel_time,fakedec,fill_value='extrapolate')(det_time)
    hitmap = np.histogram2d(ra_det,dec_det,bins=bins)
    detmaps = np.array([(np.histogram2d(ra_det,dec_det,bins=bins,weights=det_ts[:,i])[0]/hitmap[0]) for i in range(det_ts.shape[-1])])
    return hitmap[1],hitmap[2],detmaps

if '__main__' == __name__:
    # a quick demo
    import matplotlib.pyplot as pl
    # load simulated telescope data series
    faketel = np.load('/home/time_user/Downloads/tel_data.npy')
    faketime, fakera, fakedec = faketel[:,-1], faketel[:,5], faketel[:,6]

    # generate timestamps for simulated detector readout
    # the important thing is the sampling is finer than the telescope data
    faketime_det = np.linspace(np.floor(faketime[0]),np.ceil(faketime[-1]),
                                                            len(faketime)*2) #*7 at the end here
    size = 100
    # fake signal cube: single source with frequency-dependent size
    rabins = np.linspace(75.5,76.7,100) #2161
    decbins = np.linspace(23.8,24.8,100) #1801
    ramesh, decmesh = np.meshgrid(rabins,decbins,indexing='ij')
    # symmetric Gaussian, source centre located slightly above scan centre
    fakecube = np.exp(-((ramesh-76.1)**2+(decmesh-24.6)**2)[...,None]/0.001764/(np.arange(size)[None,None,:]+1)**0.25)
    # we generate the simulated time series here
    # we specify frequency-dependent Gaussian noise
    fakecube_det = cube_to_ts(faketime_det,faketime,fakera,fakedec,fakecube,
                                rabins,decbins,noise=0.2*(np.arange(size)+1)**0.5)
    # if the line below were decommented you would actually save something
    # np.savez('20210408_faketstest_.npz',t=faketime_det,pwr=fakecube_det)
    print(fakecube_det.shape)
    fakecube_detcube = np.reshape(fakecube_det, (fakecube_det.shape[0], 10, 10))
    pl.imshow(fakecube_detcube[0,:,:])
    pl.show()

    # check 1: plot time series
    # pl.plot(faketime_det,fakecube_det[:,42],label='chan42')
    pl.plot(faketime_det,fakecube_det[:,10],label='chan10')
    pl.plot(faketime_det,fakecube_det[:,0],label='chan00')
    pl.xlabel('Unix time')
    pl.ylabel('detector readout')
    pl.legend(loc='best')

    # check 2: put time series back through a basic mapmaker
    mapra,mapdec,maps = quickmap(faketime_det,fakecube_det,
                                    faketime,fakera,fakedec)
    pl.figure(figsize=(6,3))
    pl.subplots_adjust(hspace=0,wspace=0,top=0.96,bottom=0.2)
    pl.subplot(121).set_aspect(1)
    pl.pcolormesh(mapra,mapdec,np.ma.masked_invalid(maps[0].T),
                    vmin=-0.3,vmax=0.9)
    pl.xlabel('ra')
    pl.ylabel('dec')
    pl.subplot(122)
    pl.pcolormesh(range(size),mapdec,np.ma.masked_invalid(maps[:,9].T),
                    vmin=-0.3,vmax=0.9)
    pl.xlabel('channel')
    pl.gca().set_yticks(())
    pl.show()
