from PyVMEC2.exp import *
from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB', 'sounddevice', 'pyo', 'pygame']
from psychopy import core, visual, monitors, event, sound
import numpy as np
import screeninfo, copy, os, glob
from time import time


from psychopy.hardware import keyboard
from pyglet.window import key



# let's try using the psychopy IOHUB server system
# this will allow better time-resolution for trajectory recording at least
# as IOHUB can store mouse positions as soon as they come in
# (either as often as they are polled, or whenever there is a change)

# when using the PsychoPy Window system for a display object:
# this also requires setting the backend to pyglet
# when creating the Window object, set winType='pyglet'

# BTW, when using displays that are not PsychoPy Windows, the
# mouse-based trackers will still require a PsychoPy Window

# there is no tablet interface there yet, but for now we just use it as a mouse
# the main difference between mouse and tablet then is a matter of scale:
# - mouse: float positions, where the home-target distance is (probably 0.4) in
#          norm coordinates, and 1.0 in the stored data
# - tablet: float position in centimeters

# since the monitor will likely ALWAYS have a size in centimeters,
# the mouse object will also need to know how to convert to centimeters
# which is essentially using the current trials' home-target distance to
# scale the normalized position

# that means that target distance in the JSON and trial sequence will need to
# be set as a fraction of the maximum home-target distance
# and that will have to be defined outside of the tasks and trials


from psychopy.iohub.client import launchHubServer
from psychopy import core, visual

# this will be a function to run,
# it will create objects that are reffed in the cfg dictionary

def setupHardware(cfg):

    # new section in the cfg for hardware:
    cfg['hw'] = {}
    # this will have many binary objects that can not be stored in JSON output
    # so this part will be ejected before making safety backups of the cfg

    # first, a PsychoPy window object has to be made
    if cfg['settings']['devices']['display']['type'] == "monitor":
        cfg['hw']['display'] = monitorDisplay(cfg)
    else:
        # this is not made yet, and is meant for non-psychopy displays
        cfg['hw']['display'] = dummyDisplay(cfg)
        # so if the display object is not a monitor, there will be errors
        # and it should/will be a monitor anyway

        # once we have non-psychopy displays (VR?) any psychopy tracker
        # should still be related to a window object (a psychopy display)
        # that's where a dummyDisplay comes in, but we don't need it now


    # THESE ARE LARGELY THE SAME (for now) MERGE OBJECTS?
    if cfg['settings']['devices']['tracker']['type'] == "tablet":
        cfg['hw']['tracker'] = tabletTracker(cfg)
    if cfg['settings']['devices']['tracker']['type'] == "mouse":
        cfg['hw']['tracker'] = mouseTracker(cfg)

    # in case there are any 'wav' files in the resources folder
    # they are added as playable sound objects to the cfg
    cfg = addSounds(cfg)

    # cfg = addMovies(cfg) #? some day...

    return(cfg)

    # winType='pyglet'

    # cfg['hw']['io'] = launchHubServer(win=cfg['hw']['display'].win)
    # ok, no IOhub for now... it throws errors


# gammaGrid = np.array([[  0., 107.28029,  2.8466334, np.nan, np.nan, np.nan],
#                       [  0.,  22.207165, 2.8466334, np.nan, np.nan, np.nan],
#                       [  0.,  76.29962,  2.8466334, np.nan, np.nan, np.nan],
#                       [  0.,   8.474467, 2.8466334, np.nan, np.nan, np.nan]], dtype=float)


# distance to target SHOULD only be set in CM if both
# the size of the tracker device (if applicable, e.g. optotrack... not so necessary)
# and the size of the display device are known

# despite some checks, there is no guarantee for this...
# we rely on users to smart

# resolution and size have to be provided as a list of 2 numbers :
# width and hieght in
# pixels and cm

# if size is not provided, the unit will be the default normalized unit, otherwise cm

class monitorDisplay:

    def __init__(self, cfg):

        display = copy.deepcopy(cfg['settings']['devices']['display'])

        # for these properties there are sensible defaults:
        if 'screen_idx' in display.keys():
            self.screen_idx = display['screen_idx']
        else:
            self.screen_idx = 0
        if 'gammafile' in display.keys():
            self.gammafile = display['gammafile']
        else:
            self.gammafile = None

        # do we want a viewscale still? cm units make this superfluous...
        if 'viewscale' in display.keys():
            self.viewscale = display['viewscale']
        else:
            self.viewscale = [1,1]

        # with the pyglet backend you can specify a monitor index directly,
        # but if we use screeninfo, that's not necessary
        # we want to use pyglet anyway, so we can use the iohub
        # still we get the screeninfo, as it's useful to have
        if (isinstance(self.screen_idx, int)):
            self.si = screeninfo.get_monitors()[self.screen_idx]
        else:
            # pick the first monitor? maybe not a good default...
            self.si = screeninfo.get_monitors()[0]

        # pixel size is necessary, it should be in screeninfo:
        self.fullscreen = None # use system default?
        if 'size_px' in display.keys():
            self.size_px = display['size_px']
            if ('size_px' == None):
                self.size_px = [self.si.width, self.si.height]
            self.fullscreen = True
            if ((self.si.width != self.size_px[0]) or (self.si.height != self.size_px[1])):
                print('physical monitor reports different pixel size than configured')
                print('using configured pixel size in windowed mode')
                print('this may invalidate physical size')
                self.fullscreen = False
        else:
            self.size_px = [self.si.width, self.si.height]
            self.fullscreen = True

        # physical size is nice, but normalized units are acceptable
        if 'size_cm' in display.keys():
            self.size_cm = display['size_cm']
            self.units = 'cm'
        else:
            if (cfg['settings']['preferred_unit'] == 'cm' and isinstance(self.si.width_mm, int) and isinstance(self.si.height_mm, int)):
                self.units = 'cm'
                self.size_cm = [self.si.width_mm/10., self.si.height_mm/10.]
        if (self.size_cm == None):
            self.units = 'norm'


        # we'd need this to create the window as well:
        self.pos = [self.si.x, self.si.y]

        default_gg = np.array([[0., 1., 1., np.nan, np.nan, np.nan],
                               [0., 1., 1., np.nan, np.nan, np.nan],
                               [0., 1., 1., np.nan, np.nan, np.nan],
                               [0., 1., 1., np.nan, np.nan, np.nan]], dtype=float)
        # load gammagrid from stored file
        if (self.gammafile == None):
            # default gammagrid that leaves the color space as is:
            self.gg = default_gg
            print('using default gamma settings')
        if (isinstance(self.gammafile, str)):
            # probably a filename
            try:
                self.gg = np.loadtxt(fname='experiments/%s/resources/hw/%s'%(cfg['name'],self.gammafile), # that path is probably not what we want
                                     delimiter=',')
                print('loaded gamma-file')
            except:
                print('could not load gamma-file, using defaults')
                self.gg = default_gg
        # if not(isinstance(self.gg, numpy.ndarray)):
        #     print('gammafile needs to be None or the name of a csv file with a 4x6 psychopy gammagrid')
        # tempmonitor =


        # if (self.size_px == None):
        #     try:
        #         self.size_px = [s.width, s.height]
        #         fullscreen = True
        #     except e:
        #         print(e)
        #         self.size_px = [400,300]
        #         fullscreen = False
        # else:
        #     fullscreen = True
        #     if ((s.width != self.size_px[0]) or (s.height != self.size_px[1])):
        #         print('user-defined monitor pixel size does not match screeninfo')
        #         print('trying to set the user-defined monitor pixel size')


        # # make window object using the tempmonitor and viewScale
        # if (self.size_cm == None):
        #     # the only options available would be pixels or normalized
        #     # we pick normalized, so we tell the psychopy windows object
        #     self.units = 'norm'
        #     # but this _can_ be overruled -- if we have the necessary info:
        #     if (cfg['settings']['preferred_unit'] == 'cm' and isinstance(s.width_mm, int) and isinstance(s.height_mm, int)):
        #         self.units = 'cm'
        #         self.size_cm = [s.width_mm/10., s.height_mm/10.]
        #         print('using the screeninfo monitor size in centimeters')
        # else:
        #     # now we can have cm available as well
        #     self.units = 'cm'
        #     if (((s.width_mm/10.) != self.size_cm[0]) or ((s.height_mm/10.) != slef.size_cm[1])):
        #         print('user-defined monitor centimeter size does not match screeninfo')
        #         print('keeping the user-defined monitor centimeter size')

        # now we create the actual window object:
        self.createWindow(cfg)
        # and the visual stimuli we might want:
        self.createStimuli(cfg)


    def createWindow(self, cfg):

        mymonitor = monitors.Monitor(name='PyVMEC_display')
        mymonitor.setGammaGrid(self.gg)
        mymonitor.setSizePix(self.size_px)

        if self.units == 'cm':
            mymonitor.setWidth(self.size_cm[0])

        self.monitor = mymonitor

        # now set the window object using this monitor:
        self.win = visual.Window( screen = self.screen_idx,
                                  size = self.size_px,
                                  pos = self.pos,
                                  winType = 'pyglet',
                                  color = [-1,-1,-1],
                                  monitor = self.monitor,
                                  units = self.units,
                                  fullscr = self.fullscreen,
                                  viewScale = self.viewscale)

        stimuli = copy.deepcopy(cfg['settings']['stimuli'])

        # this is set here once, but as properties that could be changed later on:
        if self.units == 'cm':
            self.home_radius   = stimuli['home']['radius_cm']
            self.target_radius = stimuli['target']['radius_cm']
            self.cursor_radius = stimuli['cursor']['radius_cm']
        else:
            self.home_radius   = (stimuli['home']['radius_cm']   / cfg['settings']['basictrial']['targetdistance_cm']) * cfg['settings']['basictrial']['targetdistance_norm']
            self.target_radius = (stimuli['target']['radius_cm'] / cfg['settings']['basictrial']['targetdistance_cm']) * cfg['settings']['basictrial']['targetdistance_norm']
            self.cursor_radius = (stimuli['cursor']['radius_cm'] / cfg['settings']['basictrial']['targetdistance_cm']) * cfg['settings']['basictrial']['targetdistance_norm']

        self.pyg_keyboard = key.KeyStateHandler()
        self.win.winHandle.push_handlers(self.pyg_keyboard)
        
        cfg['hw']['win']    = self.win
        cfg['hw']['pyglet'] = {'keyboard' : self.pyg_keyboard,
                               'key'      : key }





    def createStimuli(self, cfg):

        # we might want other stimuli, but for now, there are only 3:
        # a home position (open circle)
        # a target position (open circle)
        # a cursor (a filled disc)

        # maybe initial positions should be way of the screen... depends on the unit?
        self.off_pos = [max(self.size_px)*3,max(self.size_px)*3]

        stimuli = copy.deepcopy(cfg['settings']['stimuli'])

        # seems like units are inherited from the window object, so they should NEVER be set

        self.home = visual.Circle( win = self.win,
                                   edges = stimuli['home']['edges'],
                                   lineWidth = stimuli['home']['lineWidth'],
                                   lineColor = stimuli['home']['lineColor'],
                                   fillColor = stimuli['home']['fillColor'],
                                   radius = self.home_radius,
                                   pos = self.off_pos)

        self.target = visual.Circle( win = self.win,
                                     edges = stimuli['target']['edges'],
                                     lineWidth = stimuli['target']['lineWidth'],
                                     lineColor = stimuli['target']['lineColor'],
                                     fillColor = stimuli['target']['fillColor'],
                                     radius = self.target_radius,
                                     pos = self.off_pos)

        self.cursor = visual.Circle( win = self.win,
                                     edges = stimuli['cursor']['edges'],
                                     lineWidth = stimuli['cursor']['lineWidth'],
                                     lineColor = stimuli['cursor']['lineColor'],
                                     fillColor = stimuli['cursor']['fillColor'],
                                     radius = self.cursor_radius,
                                     pos = self.off_pos)

        self.cursor_imprint = visual.Circle( win = self.win,
                                             edges = stimuli['cursor_imprint']['edges'],
                                             lineWidth = stimuli['cursor_imprint']['lineWidth'],
                                             lineColor = stimuli['cursor_imprint']['lineColor'],
                                             fillColor = stimuli['cursor_imprint']['fillColor'],
                                             radius = self.cursor_radius,
                                             pos = self.off_pos)

        self.target_imprint = visual.Circle( win = self.win,
                                             edges = stimuli['target_imprint']['edges'],
                                             lineWidth = stimuli['target_imprint']['lineWidth'],
                                             lineColor = stimuli['target_imprint']['lineColor'],
                                             fillColor = stimuli['target_imprint']['fillColor'],
                                             radius = self.cursor_radius,
                                             pos = self.off_pos)

        self.target_arc = Arc(        win = self.win,
                                      units = self.units,
                                      edges = stimuli['target_arc']['edges'],
                                      lineWidth = stimuli['target_arc']['lineWidth'],
                                      lineColor = stimuli['target_arc']['lineColor'],
                                      fillColor = stimuli['target_arc']['fillColor'],
                                      radius = stimuli['target_arc']['radius'],
                                      width = stimuli['target_arc']['width'],
                                      start = stimuli['target_arc']['start'],
                                      end = stimuli['target_arc']['end'],
                                      pos = self.off_pos )

        self.aiming_arrow =  visual.ShapeStim( win        = self.win, 
                                               lineWidth  = stimuli['aiming_arrow']['lineWidth'],
                                               lineColor  = stimuli['aiming_arrow']['lineColor'],
                                               fillColor  = stimuli['aiming_arrow']['fillColor'],
                                               vertices   = stimuli['aiming_arrow']['vertices'],
                                               closeShape = stimuli['aiming_arrow']['closeShape'], 
                                               size       = stimuli['aiming_arrow']['size'] )


        # self.cursor_arc = visual.Pie( win = self.win,
        #                               edges = stimuli['cursor_arc']['edges'],
        #                               lineWidth = stimuli['cursor_arc']['lineWidth'],
        #                               lineColor = stimuli['cursor_arc']['lineColor'],
        #                               fillColor = None,
        #                               radius = stimuli['cursor_arc']['radius'],
        #                               start = stimuli['cursor_arc']['start'],
        #                               end = stimuli['cursor_arc']['end'],
        #                               pos = self.off_pos)

        # ADD TEXT STIMULI
        # - instructions

        # we put the counter in the top-left corner

        # setting the position and size should be a function, so that
        # we can easily revert back to defaults... later
        if (self.units == 'cm'):
            self.trialcounter_pos = [ 1 * cfg['settings']['basictrial']['targetdistance_cm'], 1 * cfg['settings']['basictrial']['targetdistance_cm']]
            self.trialcounter_height = 0.05 * min(self.size_cm)

        if (self.units == 'norm'):
            self.trialcounter_pos = [ 1 * cfg['settings']['basictrial']['targetdistance_norm'], 1 * cfg['settings']['basictrial']['targetdistance_norm']]
            self.trialcounter_height = 0.05 * min(self.size_norm)

        flipHoriz = cfg['settings']['devices']['display']['text_flips'][0]
        flipVert  = cfg['settings']['devices']['display']['text_flips'][1]

        self.trialcounter = visual.TextStim( win = self.win,
                                             text = '0/0',
                                             pos = self.trialcounter_pos,
                                             height = self.trialcounter_height,
                                             flipHoriz = flipHoriz,
                                             flipVert = flipVert)

        # points counter:
        if (self.units == 'cm'):
            self.pointscounter_pos = [-1 * cfg['settings']['basictrial']['targetdistance_cm'], 1 * cfg['settings']['basictrial']['targetdistance_cm']]
            self.pointscounter_height = 0.05 * min(self.size_cm)

        if (self.units == 'norm'):
            self.pointscounter_pos = [-1 * cfg['settings']['basictrial']['targetdistance_norm'], 1 * cfg['settings']['basictrial']['targetdistance_norm']]
            self.pointscounter_height = 0.05 * min(self.size_norm)

        self.pointscounter = visual.TextStim( win = self.win,
                                              text = '0/0',
                                              pos = self.pointscounter_pos,
                                              height = self.pointscounter_height,
                                              flipHoriz = flipHoriz,
                                              flipVert = flipVert)

        # instructions will be in the middle of the screen:
        self.instructions_pos = [0, 0]
        if (self.units == 'cm'):
            self.instructions_height = 0.025 * min(self.size_cm)

        if (self.units == 'norm'):
            self.instructions_height = 0.025 * min(self.size_norm)

        self.instructions = visual.TextStim( win = self.win,
                                             text = '[no instructions]',
                                             pos = self.instructions_pos,
                                             height = self.instructions_height,
                                             flipHoriz = flipHoriz,
                                             flipVert = flipVert)

        # pause time countdown:
        if (self.units == 'cm'):
            self.pausecountdown_pos = [0,-0.4*min(self.size_cm)]
            self.pausecountdown_height = 0.05 * min(self.size_cm)
        if (self.units == 'norm'):
            self.pausecountdown_pos = [0,-0.4*min(self.size_norm)]
            self.pausecountdown_height = 0.05 * min(self.size_cm)
        self.pausecountdown = visual.TextStim( win = self.win,
                                               text = '',
                                               pos = self.pausecountdown_pos,
                                               height = self.instructions_height,
                                               flipHoriz = flipHoriz,
                                               flipVert = flipVert)

    def showHome(self, homePos):
        self.home.pos = homePos
        self.home.draw()

    def showTarget(self, targetPos):
        self.target.pos = targetPos
        self.target.draw()

    def showTargetArc(self, targetArcPos):
        self.target_arc.pos = targetArcPos
        self.target_arc.draw()

    def showCursor(self, cursorPos):
        self.cursor.pos = cursorPos
        self.cursor.draw()

    def showCursorImprint(self, cursorImprintPos):
        self.cursor_imprint.pos = cursorImprintPos
        self.cursor_imprint.draw()

    def showTargetImprint(self, targetImprintPos):
        self.target_imprint.pos = targetImprintPos
        self.target_imprint.draw()

    def showAimingarrow(self, aimingArrowPos=None, aimingArrowOri=None):
        if aimingArrowOri != None:
            self.aiming_arrow.ori = aimingArrowOri
        if aimingArrowPos != None:
            self.aiming_arrow.pos = aimingArrowPos
        self.aiming_arrow.draw()
        

    def showPointsCounter(self, points, pos=None):
        txt = '%d'%points
        self.pointscounter.setText(text = txt)
        if pos is not None:
            self.pointscounter.pos = pos
        self.pointscounter.draw()

    def showInstructions(self, txt=None, pos=None):
        if txt is not None:
            self.instructions.setText(text  = txt)
        if pos is not None:
            self.instructions.pos = pos
        self.instructions.draw()

    def showPauseCountdown(self, txt=None, pos=None):
        if txt is not None:
            self.pausecountdown.setText(text = txt)
        if pos is not None:
            self.pausecountdown.pos = pos
        self.pausecountdown.draw()

    
    def setProperties(self, propdict):
        
        references = {'cursor'          : self.cursor,
                      'home'            : self.home,
                      'target'          : self.target,
                      'target_imprint'  : self.target_imprint,
                      'cursor_imprint'  : self.cursor_imprint,
                      'target_arc'      : self.target_arc}

        if propdict['stimulus'] in references.keys():
            refered = references[propdict['stimulus']]
        else:
            return

        if propdict['property'] == 'fillColor':
            refered.fillColor = propdict['value']
        if propdict['property'] == 'lineColor':
            refered.lineColor = propdict['value']


    def doFrame(self): # THIS WILL GET THE TRIAL STATE DICTIONARY !!!!
        
        # AND HERE:
        # FIRST DECIDE WHAT IS SHOWN... 
        # rather than leaving this to the trial loop
        
        # show stimuli:
        self.win.flip()

        # move stimuli off screen for now:
        self.home.pos = self.off_pos
        self.target.pos = self.off_pos
        self.cursor.pos = self.off_pos
        self.cursor_imprint.pos = self.off_pos
        self.target_arc.pos = self.off_pos
        self.aiming_arrow.pos = self.off_pos


    def shutDown(self):

        self.win.close()

        # there are no:
        # - return feedback arrowhead
        # - aiming arrow
        # - aiming landmarks


        # and we might want to have some graphics objects:
        # - for showing larger images (as visual instructions)
        # - for showing videos (even more detailed instructions)




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




# if we want to separate tracking trajectories from visual stimuli,
# we want to use iohub
# which means we need to use the pyglet backend

class tabletTracker:

    def __init__(self, cfg):

        tracker = copy.deepcopy(cfg['settings']['devices']['tracker'])

        display_size_cm = copy.deepcopy(cfg['hw']['display'].size_cm)

        # for a tablet tracker, we can't get physical dimensions
        # so if it fails, set a mouse tracker instead, outside this object

        # this should really be determined based on available data!
        # for now it is hard-coded
        self.units = 'cm'

        if ('size_cm' in tracker.keys()):
            self.size_cm = tracker['size_cm']
        if ('size_px' in tracker.keys()):
            self.size_px = tracker['size_px']
        if ('offset_cm' in tracker.keys()):
            self.offset_cm = tracker['offset_cm']
        else:
            self.offset_cm = [0,0]

        # this SHOULD link the mouse/tablet to the window object
        # and use the units set for the window object
        self.psymouse = event.Mouse( visible = False,
                                     newPos = None,
                                     win = cfg['hw']['display'].win )


        self.xscale = 1
        self.yscale = 1

        if cfg['hw']['display'].units == 'cm':
            # maybe we should also check that the physical size of the tablet is available

            aspect_ratio_tablet = self.size_cm[0] / self.size_cm[1]
            aspect_ratio_screen = display_size_cm[0] / display_size_cm[1]

            if tracker['mapping'] == 'absolute':
                # a 1:1 ratio between horizontal and vertical distances
                # good for drawing, but part of the tablet is likely not used
                # let's determine the effective size:
                if aspect_ratio_screen > aspect_ratio_tablet:
                    self.size_cm = [self.size_cm[0], self.size_cm[0]/aspect_ratio_screen]
                if aspect_ratio_screen < aspect_ratio_tablet:
                    self.size_cm = [self.size_cm[1]*aspect_ratio_screen, self.size_cm[1]]
                # if the two aspect ratios are the same, we don't do anything

            # if the mapping is relative, the effective size IS the physical size

            # now we can scale the tablet coordinates
            # (that are projected to the screen)
            # such that they become real centimeters
            self.xscale = self.size_cm[0] / display_size_cm[0]
            self.yscale = self.size_cm[1] / display_size_cm[1]



        # for an actual MOUSE, the normalized position should be stored

    def getPos(self):
        [X,Y] = self.psymouse.getPos()
        tp = time()
        X = (X * self.xscale) - self.offset_cm[0]
        Y = (Y * self.yscale) - self.offset_cm[1]
        return( [X,Y, tp] )

# cfg['settings']['devices']['tracker'] = {
#       "type"       : "tablet",
#       "screen_idx" : 1,
#       "size_px"    : [1680, 1050],
#       "size_cm"    : [31.1, 21.6],   # Wacom Intuos Pro Large, specifications from website
#       "offset_cm"  : [0, 0]

def addSounds(cfg):

    # check if there are "wav" files in the resources folders
    wav_files = glob.glob('experiments/%s/resources/sounds/*.wav'%(cfg['run']['experiment']), recursive=False)

    if len(wav_files):
        # make a dictionary with named sound objects:
        cfg['hw']['sounds'] = {}
        for wav_file in wav_files:
            file_name = os.path.basename(wav_file)
            sound_name = os.path.splitext(file_name)[0]
            cfg['hw']['sounds'][sound_name] = sound.Sound(wav_file)
    #sound.Sound('short_tick.wav', sampleRate=44100)

    return(cfg)


class Arc:

    def __init__(self, 
                 win, 
                 units,
                 edges, 
                 fillColor,
                 radius,
                 width,
                 start,
                 end,
                 pos,
                 ori = 0,
                 lineWidth = 0,
                 lineColor = None):

        self.win = win
        self.units = units
        self.edges = edges
        self.fillColor = fillColor
        self.radius = radius
        self.width = width
        self.start = start
        self.end = end
        self.pos = pos
        self.ori = ori


        self.lineWidth = lineWidth
        self.lineColor = lineColor

        # determines the object's shape (and color, position, etc)
        self.setVertices()

    def setVertices(self):

        self.vertices = []

        self.vertices += [[np.cos(a)*(self.radius - (self.width/2)), np.sin(a)*(self.radius - (self.width/2))] for a in (np.linspace(self.start, self.end, num=int(np.floor(self.edges/2)))/180)*np.pi]
        self.vertices += [[np.cos(a)*(self.radius + (self.width/2)), np.sin(a)*(self.radius + (self.width/2))] for a in (np.linspace(self.end, self.start, num=int(np.ceil(self.edges/2)))/180)*np.pi]

        self.arcshape = visual.ShapeStim(win       = self.win,
                                         units     = self.units,
                                         fillColor = self.fillColor,
                                         lineColor = self.lineColor,
                                         lineWidth = self.lineWidth,
                                         vertices  = self.vertices,
                                         pos       = self.pos,
                                         ori       = self.ori)

    def draw(self):
        # draw the shapestim
        self.arcshape.pos = self.pos
        self.arcshape.draw()
