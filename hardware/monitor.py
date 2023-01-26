from psychopy import core, visual, monitor
import numpy as np
import screeninfo


# class psychopy.visual.Window(
# size=(800, 600),
# pos=None,
# color=(0, 0, 0),
# colorSpace='rgb',
# rgb=None,
# dkl=None,
# lms=None,
# fullscr=None,
# allowGUI=None,
# monitor=None,
# bitsMode=None,
# winType=None,
# units=None,
# gamma=None,
# blendMode='avg',
# screen=0,
# viewScale=None,
# viewPos=None,
# viewOri=0.0,
# waitBlanking=True,
# allowStencil=False,
# multiSample=False,
# numSamples=2,
# stereo=False,
# name='window1',
# checkTiming=True,
# useFBO=False,
# useRetina=True,
# autoLog=True,
# gammaErrorPolicy='raise',
# bpc=(8, 8, 8),
# depthBits=8,
# stencilBits=8,
# backendConf=None)

# gammaGrid = np.array([[  0., 107.28029,  2.8466334, np.nan, np.nan, np.nan],
#                       [  0.,  22.207165, 2.8466334, np.nan, np.nan, np.nan],
#                       [  0.,  76.29962,  2.8466334, np.nan, np.nan, np.nan],
#                       [  0.,   8.474467, 2.8466334, np.nan, np.nan, np.nan]], dtype=float)


# distance to target SHOULD only be set in CM if both
# the size of the tracker device (if applicable, e.g. optotrack... not so necessary)
# and the size of the display device are known

# for now there is no check on this, but we rely on users to smart

# resolution and size have to be provided as a list of 2 numbers :
# width and hieght in
# pixels and cm

# if size is not provided, the unit will be the default normalized unit, otherwise cm

class monitorDisplay:

    def __init__(self, resolution, screen=0, size=None, gammafile=None):
        # resolution is in pixels
        # size is in centimeters

        # with the pyglet backend you can specify a monitor backend directly,
        # but if we use screeninfo, that's not necessary

        s = screeninfo.get_monitors()[screen]

        


        # store resolution (in pixels, needs to be checked with created window object later on)
        self.resolution = resolution

        # store size (in cm)
        self.size = size

        # instead of a gammefile, we could input the gammagrid itself?

        # load gammagrid from stored file
        if (gammafile == None):
            # default gammagrid that leaves the color space as is:
            self.gg = np.array([[0., 1., 1., np.nan, np.nan, np.nan],
                                [0., 1., 1., np.nan, np.nan, np.nan],
                                [0., 1., 1., np.nan, np.nan, np.nan],
                                [0., 1., 1., np.nan, np.nan, np.nan]], dtype=float)
        if (isinstance(gammafile, str)):
            # probably a filename
            self.gg = np.loadtxt(fname=gammafile,
                                 delimiter=',')
        if (! isinstance(self.gg, np.array)):
            print('gammafile needs to be None or the name of a csv file with a 4x6 psychopy gammagrid')
        # tempmonitor =

        # make window object using the tempmonitor and viewScale
        if (size == None):
            # the only options available would be pixels or normalized
            # we pick normalized, so we tell the psychopy windows object
            self.units = 'norm'
            pass
        else:
            # now we can have cm available as well
            self.units = 'cm'
