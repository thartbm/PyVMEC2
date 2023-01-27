import json, math, copy

cfg = {}
cfg['name'] = 'diagnostic triplets'
cfg['settings'] = {}     # window scaling / mirroring & flipping / other settings...
                         # workspace settings: home position... max target distance... allowed target angels & allowed rotations

cfg['settings']['basictrial'] = {
      "target"         : 0,
      "rotation"       : 0,
      "errorgain"      : 1,
      "cursor"         : "normal",
      "name"           : "default",
      "home"           : [0,0],
      "targetdistance" : 8
    }

# units could be 'cm' or 'norm' (pixels or degrees are near useless)
cfg['settings']['preferred_unit'] = 'cm'

# the size in pixels and cm could be read from screeninfo:
cfg['settings']['display'] = {
      "type"       : "monitor",
      "screen_idx" : 1,
      "size_px"    : [1680, 1050],
      "size_cm"    : [43.3, 27.1],
      "viewscale"  : [1,1]

      # not sure if we want to allow viewscaling again
      # this was done to map screen and tablet to the same cm distance
      # but we can now do this better, based on their physical sizes
    }

cfg['settings']['tracker'] = {
      "type" : "tablet",
      "screen_idx": 1,
      "size_px" : [1680, 1050],
      "size_cm":  []

      # typically a tablet is mapped to screen pixels
      # using a mouse device
      # we assume this has been set up correctly in the OS

      # while we can verify the screen's size in pixels
      # we'll just have to assume that the size in cm is correct
      # if not given, we fall back to normalized coordinates
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
