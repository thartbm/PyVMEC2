import copy

# if we want to separate tracking trajectories from visual stimuli,
# we want to use iohub
# which means we need to use the pyglet backend

class tabletTracker:

    def __init__(self, cfg):

        self.size_cm = copy.deepcopy(['settings']['devices']['tracker']['size_cm'])
        self.size_px = copy.deepcopy(['settings']['devices']['tracker']['size_px'])
        self.offset_cm = copy.deepcopy(['settings']['devices']['tracker']['offset_cm'])



# cfg['settings']['devices']['tracker'] = {
#       "type"       : "tablet",
#       "screen_idx" : 1,
#       "size_px"    : [1680, 1050],
#       "size_cm"    : [31.1, 21.6],   # Wacom Intuos Pro Large, specifications from website
#       "offset_cm"  : [0, 0]
