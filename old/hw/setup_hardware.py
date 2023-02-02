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

def setupHardware():

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
        # and it should be a monitor anyway

        # once we have non-psychopy displays (VR?) any psychopy tracker
        # should still be related to a window object (a psychopy display)
        # that's where a dummyDisplay comes in, but we don't need it now




    # winType='pyglet'

    cfg['hw']['io'] = launchHubServer()
