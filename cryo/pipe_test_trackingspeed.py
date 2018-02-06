
'''The maximum slew speed of the telescope is rated at 60 deg/min or 1 deg/sec or 3600 "/s. Since the sidereal rate is at 15 "/s, we must
be incrementing our position vectors by 3585 "/s. Since we are updating the position 20 times/sec , this means that each update should move
the position by 179.25 arcseconds ("), or, since our position vectors are in degrees... 0.04979 deg. The following code produces this result.'''

# initialize coordinates of source on sky and time stepper ----------------------------------------------------------------------------------
n = 0
dec = 20.0 # degrees
ra = 20.0 # degrees

''' The rest of the code should be the same so I won't bother including it here. The behavior will look like tracking accross RA positions as
constant DEC, then moving up slightly by DEC and tracking again backwards through RA. This will not create a zigzag pattern, but it will make
a "box" on the sky, which is good enough for our testing purposes.'''
newra = [0,20]
newdec = [0,20]
for i in range(1000000): #same for loop that exists in the other code...
    if newra[1] > newra[0] and newra[1] < 90.0:
        newra[0] = newra[1]
        newra[1] = ra + (0.04979*n)
        if newra <= 20.0:
            newdec = dec + (0.04979*n)
    elif newra > = 90.0:
        newdec = dec + (0.04979*m)
        newra = ra - (0.04929*n)
''' The difference here is that the new coordinates have to be fed to SkyCoord each iteration to get updated alt and az, and requires them
to be in the for loop with everything else.'''
