import json
#import math, copy



# # # # # # # # # # # # # # # # # # # # # # # # #
#
# THIS IS NOT HOW THE FINAL SCRIPTS WILL WORK!
#
# # # # # # # # # # # # # # # # # # # # # # # # #

# the idea is to make a GUI that creates and manages these JSON files
# and will also run them, store data and do some basic pre-processing


cfg = {}
cfg['name'] = 'diagnostic triplets'
cfg['settings'] = {}     # window scaling / mirroring & flipping / other settings...
                         # workspace settings: home position... max target distance... allowed target angels & allowed rotations

cfg['settings']['basictrial'] = {
      "target"              : 0,
      "rotation"            : 0,
      "errorgain"           : 1,
      "cursor"              : "normal",
      "name"                : "default",
      "home"                : [0,0],
      "targetdistance_cm"   : 8,
      "targetdistance_norm" : 0.4,
      "returncursor"        : False,
    }

# units could be 'cm' or 'norm' (pixels or degrees are near useless)
# maybe also NSU, which is (norm / normalized target distance)
cfg['settings']['preferred_unit'] = 'cm'

cfg['settings']['devices'] = {}

# the size in pixels and cm could be read from screeninfo:
cfg['settings']['devices']['display'] = {
      "type"       : "monitor",
      "screen_idx" : 1,
      "size_px"    : [1680, 1050],
      "size_cm"    : [43.3, 27.1],
      "viewscale"  : [-1,-1],
      "gammafile"  : "DellE2009Wt.csv"

      # not sure if we want to allow fine-grained viewscaling again
      # this was done to map screen and tablet to the same cm distance
      # but we can now do this better, based on their physical sizes

      # however, it also allows flipping and mirroring, which is
      # necessary on the mirror-box setup

      # gammafile is completely optional, and more useful for well-calibrated
      # visual stimuli (e.g. linearizing the CLUT etc)
    }

cfg['settings']['devices']['tracker'] = {
      "type"       : "tablet",
      "screen_idx" : 1,
      "size_px"    : [1680, 1050],
      "size_cm"    : [31.1, 21.6],   # Wacom Intuos Pro Large, specifications from website
      "offset_cm"  : [0, 0]

      # typically a tablet is mapped to screen pixels
      # using a mouse device
      # we assume this has been set up correctly in the OS

      # while we can verify the screen's size in pixels
      # we'll just have to assume that the size in cm is correct
      # if not given, we fall back to normalized coordinates

      # when using a stencil, we might want to allow for small offsets?
}

# a mouse tracker device would behave almost the same way
# except that we don't know the physical size of the movements
# this would be the only setting (I can think of) where we
# have to record reaches in normalized units



# one day, all STIMULI will also be modifiable as trial properties
# (- different colored target to indicate instructions,
#  - HUGE target to reduce errors,
#  - gaussian blur cursors/targets to reduce certainty)
# and they can all be replaced with images or random shapes
cfg['settings']['stimuli'] = {}

cfg['settings']['stimuli']['home'] = {
    # shapestim / circle ?
    "edges"     : 32,
    "lineColor" : [0,0,0],  # gray
    "lineWidth" : 2,        # I think this is ALWAYS in pixels...
    "fillColor" : None,     # transparent
    "radius_cm" : 0.5
}

cfg['settings']['stimuli']['target'] = {
    # shapestim / circle ?
    "edges"     : 32,
    "lineColor" : [0,0,0],  # gray
    "lineWidth" : 2,        # I think this is ALWAYS in pixels...
    "fillColor" : None,     # thansparent
    "radius_cm" : 0.5
}

cfg['settings']['stimuli']['cursor'] = {
    # shapestim / circle ?
    "edges"     : 32,
    "lineColor" : None,     # transparent
    "lineWidth" : 0,        # I think this is ALWAYS in pixels...
    "fillColor" : [1,1,1],  # white
    "radius_cm" : 0.5
}


# randomization: 'standard' or 'individual'
# standard: everyone gets the same random sequence (based on experiment name)
# individual: participants get their own random sequence (based on participant ID)
cfg['settings']['randomization'] = 'individual'

cfg['experiment'] = []

cfg['experiment'].append( { 'type':'task',
                            'name':'baseline',
                            'cursor':'normal',
                            'targets':[90],
                            'rotation':0,
                            'trials':15 } )

cfg['experiment'].append( { 'type':'supertask',
                            'name':'triplets',
                            'taskorder':'fixed', # these task are always done in the same order
                            'repeats':9,
                            'properties':{ 'rotation': {'order':'pseudorandom', # the values are randomized across repeat of all subtasks
                                                        'values': [[0],[5,10,15],[0],[0]] }, # four values: one for each of the subtasks
                                           'trials' : {'order':'pseudorandom',
                                                       'values': [[1],[1],[1],[2,3,4]] } },
                            'subtasks': [{ 'name':'pre-clamped',
                                           'cursor':'clamped' },
                                           # ,
                                           # 'targets':[90],
                                           # 'rotation':0,
                                           # 'trials':1 },
                                         { 'name':'perturbed',
                                           'cursor':'normal'},
                                           # ,
                                           # 'targets':[90],
                                           # 'rotation':0,
                                           # 'trials':1 },
                                         { 'name':'post-clamped',
                                           'cursor':'clamped'},
                                           # ,
                                           # 'targets':[90],
                                           # 'rotation':0,
                                           # 'trials':1 },
                                         { 'name':'washout',
                                           'cursor':'normal'},
                                           # ,
                                           # 'targets':[90],
                                           # 'rotation':0,
                                           # 'trials':1 },
                                         ] } )

with open( file='%s.json'%(cfg['name']),
                mode='w') as fp:
    json.dump(cfg, fp, indent=2)
