import json, math, copy

cfg = {}
cfg['name'] = 'diagnostic triplets'
cfg['settings'] = {}     # window scaling / mirroring & flipping / other settings...
                         # workspace settings: home position... max target distance... allowed target angels & allowed rotations

cfg['settings']['preferred_unit'] = 'cm'

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
                                           'cursor':'clamped',
                                           'targets':[90],
                                           'rotation':0,
                                           'trials':1 },
                                         { 'name':'perturbed',
                                           'cursor':'normal',
                                           'targets':[90],
                                           'rotation':0,
                                           'trials':1 },
                                         { 'name':'post-clamped',
                                           'cursor':'clamped',
                                           'targets':[90],
                                           'rotation':0,
                                           'trials':1 },
                                         { 'name':'washout',
                                           'cursor':'normal',
                                           'targets':[90],
                                           'rotation':0,
                                           'trials':1 },
                                         ] } )

with open( file='%s.json'%(cfg['name']),
                mode='w') as fp:
    json.dump(cfg, fp, indent=2)
