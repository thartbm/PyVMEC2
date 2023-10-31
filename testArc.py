import numpy as np
from psychopy import core, event, visual, monitors
from time import time


# create monitor object for window in CM

default_gamma = np.array([[0., 1., 1., np.nan, np.nan, np.nan],
                            [0., 1., 1., np.nan, np.nan, np.nan],
                            [0., 1., 1., np.nan, np.nan, np.nan],
                            [0., 1., 1., np.nan, np.nan, np.nan]], dtype=float)

resolution = [1920, 1080]
size = [34.4, 19.4]
distance = 30


mymonitor = monitors.Monitor(name='temp',
                             distance=distance,
                             width=size[0])
mymonitor.setGammaGrid(default_gamma)
mymonitor.setSizePix(resolution)




win = visual.Window( screen = 0,
                     winType = 'pyglet',
                     color = [-1,-1,-1],
                     units = 'cm',
                     fullscr = True,
                     monitor = mymonitor)


radius = 8
width = 0.25
start = 30
end = 150
edges = 128

vertices = []
vertices += [[np.cos(a)*(radius - (width/2)), np.sin(a)*(radius - (width/2))] for a in (np.linspace(start, end, num=int(np.floor(edges/2)))/180)*np.pi]
vertices += [[np.cos(a)*(radius + (width/2)), np.sin(a)*(radius + (width/2))] for a in (np.linspace(end, start, num=int(np.ceil(edges/2)))/180)*np.pi]

arcshape = visual.ShapeStim(win       = win,
                            units     = 'cm',
                            fillColor = [0,0,1],
                        #  lineColor = self.lineColor,
                        #  lineWidth = self.lineWidth,
                            interpolate = True,
                            lineColor = [0,0,0],
                            lineWidth = 0,
                            vertices  = vertices,
                            pos       = [0,0],
                            ori       = 0)

beginning = time()

while (time() < (beginning + 2)):

    # newpos = event.mouse.getPos()
    # arcshape.pos = newpos
    arcshape.draw()
    win.flip()

win.close()

