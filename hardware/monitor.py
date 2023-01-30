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

    def __init__(self, cfg):

        self.screen_idx = copy.deepcopy(cfg['settings']['devices']['display']['screen_idx'])
        self.size_px    = copy.deepcopy(cfg['settings']['devices']['display']['size_px'])
        self.size_cm    = copy.deepcopy(cfg['settings']['devices']['display']['size_cm'])
        self.viewscale  = copy.deepcopy(cfg['settings']['devices']['display']['viewscale'])
        self.gammafile  = copy.deepcopy(cfg['settings']['devices']['display']['gammafile'])

        # resolution is in pixels
        # size is in centimeters

        # with the pyglet backend you can specify a monitor backend directly,
        # but if we use screeninfo, that's not necessary
        if (isinstance(self.screen_idx), int)):
            s = screeninfo.get_monitors()[self.screen_idx]
        else:
            # pick the first monitor?
            s = screeninfo.get_monitors()[0]

        # load gammagrid from stored file
        if (gammafile == None):
            # default gammagrid that leaves the color space as is:
            self.gg = np.array([[0., 1., 1., np.nan, np.nan, np.nan],
                                [0., 1., 1., np.nan, np.nan, np.nan],
                                [0., 1., 1., np.nan, np.nan, np.nan],
                                [0., 1., 1., np.nan, np.nan, np.nan]], dtype=float)
        if (isinstance(self.gammafile, str)):
            # probably a filename
            self.gg = np.loadtxt(fname=self.gammafile,
                                 delimiter=',')
        if (! isinstance(self.gg, np.array)):
            print('gammafile needs to be None or the name of a csv file with a 4x6 psychopy gammagrid')
        # tempmonitor =

        if (self.size_px == None):
            try:
                self.size_px = [s.width, s.height]
                fullscreen = True
            except e:
                print(e)
                self.size_px = [400,300]
                fullscreen = False
        else:
            fullscreen = True
            if ((s.width != self.size_px[0]) or (s.height != self.size_px[1])):
                print('user-defined monitor pixel size does not match screeninfo')
                print('trying to set the user-defined monitor pixel size')


        # make window object using the tempmonitor and viewScale
        if (self.size_cm == None):
            # the only options available would be pixels or normalized
            # we pick normalized, so we tell the psychopy windows object
            self.units = 'norm'
            # but this _can_ be overruled:
            if (cfg['settings']['preferred_unit'] == 'cm' and isinstance(s.width_mm, int) and isinstance(s.height_mm, int)):
                self.units = 'cm'
                self.size_cm = [s.width_mm/10., s.height_mm/10.]
                print('using the screeninfo monitor size in centimeters')
        else:
            # now we can have cm available as well
            self.units = 'cm'
            if (((s.width_mm/10.) != self.size_cm[0]) or ((s.height_mm/10.) != slef.size_cm[1])):
                print('user-defined monitor centimeter size does not match screeninfo')
                print('keeping the user-defined monitor centimeter size')


# we will only need a dummyDisplay object if we have non-psychopy trackers

# class dummyDisplay:
#
#     def __init__(self, cfg):
#
#         # using the main monitor:
#         s = screeninfo.get_monitors()
#
#         print('this is the UNFINISHED dummy display initialization')
#         print('please define a monitor display')
#         print('this is what screeninfo knows about the monitor(s):')
#         print(s)
