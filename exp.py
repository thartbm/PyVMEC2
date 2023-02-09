import hw
import random, json, copy, math
import numpy as np

def runExperiment(jsonfile, participant):

    cfg = {}

    cfg['participant'] = participant
    cfg['jsonfile'] = jsonfile

    cfg = loadJSON(cfg)

    cfg = getTrialSequence(cfg)

    cfg = hw.setupHardware(cfg)

    cfg = runTrialSequence(cfg)

def loadJSON(cfg):

    with open(cfg['jsonfile']) as fp:
        cfg.update(json.load(fp))

    return(cfg)

def getTrialSequence(cfg):

    seedRNG(cfg)

    cfg['triallist'] = []

    # simple start:
    cfg['basictrial'] = {'target'   : 0,
                         'rotation' : 0,
                         'cursor'   : 'normal',
                         'name'     : '' }

    # we can add other functionality later on:
    # - aiming, cursor/target jumps, points... holding home/target

    for el in cfg['experiment']:

        if el['type'] == 'task':

            cfg = addTaskTrials(cfg=cfg, el=el)




        if el['type'] == 'supertask':

            cfg = addSuperTaskTrials(cfg=cfg, el=el)

        if el['type'] == 'pause':

            # insert a specific pause:
            # - display (instruction) text
            # - force a wait time
            # - require key-press

            # not implemented:
            # show an image
            # play a video or audio recording (from the web?)

            pass

    return(cfg)

def addTaskTrials(cfg, el):

    task = copy.deepcopy(cfg['settings']['basictrial'])
    task.update(el)

    var_prop_names = []
    if 'order' in task.keys():
        for p in task.keys():
            if isinstance(task[p], list) & (p in task['order'].keys()):
                var_prop_names.append(p)

    variable_properties = {}
    for vpn in var_prop_names:
        variable_properties[vpn] = []
        nblocks = int(math.ceil(task['trials'] / len(task[vpn])))
        for block in range(nblocks):
            values = copy.deepcopy(task[vpn])
            if task['order'][vpn] == 'pseudorandom':
                random.shuffle(values)
            variable_properties[vpn] += values
        variable_properties[vpn] = variable_properties[vpn][:task['trials']]
        if task['order'][vpn] == 'random':
            random.shuffle(variable_properties[vpn])

    # make the basic trial template:
    trial = copy.deepcopy(cfg['settings']['basictrial'])
    strippedtask = copy.deepcopy(task)
    remove_entries = var_prop_names + ['order']
    for k in remove_entries:
        strippedtask.pop(k, None)
    trial.update(strippedtask)

    # psedurandomize in blocks:
    for trialno in range(task['trials']):

        # else: get a trial to add to the list:
        thistrial = copy.deepcopy(trial)
        for vpn in var_prop_names:
            thistrial[vpn] = variable_properties[vpn][trialno]

        unkeys = ['trials']
        for k in unkeys:
            if (k in thistrial.keys()):
                del thistrial[k]

        thistrial['type'] = 'trial'

        cfg['triallist'] += [thistrial]

    return(cfg)

def addSuperTaskTrials(cfg, el):

    nsubtasks = len(el['subtasks'])
    nproperties = len(el['properties'])
    nrepeats = el['repeats']

    # prepare the subtask properties:
    # subtasks X properties

    pro_dic = {} # an empty placeholder
    for k in el['properties'].keys():
        pro_dic[k] = []

    subtask_properties = {}
    for k in range(len(el['subtasks'])):
        subtask_properties[el['subtasks'][k]['name']] = copy.deepcopy(pro_dic)

    # list with property values to populate subtasks
    # this will be refilled when empty while
    # looping through repeats of subtasks
    prop_vals = copy.deepcopy(subtask_properties)

    # add trials to triallist:
    for repeat in range(el['repeats']):

        # determine task order:
        taskorder = range(len(el['subtasks']))
        if el['taskorder'] == 'pseudorandom':
            random.shuffle(taskorder)

        for task_idx in range(len(el['subtasks'])):
            task_name = el['subtasks'][task_idx]['name']

            # set up a sub-task instance:
            subtask = copy.deepcopy(el['subtasks'][task_idx])

            # populate it with the variable properties:
            for property in el['properties'].keys():
                #print(property)
                if len(prop_vals[task_name][property]) == 0:
                    temp_vals = copy.deepcopy(el['properties'][property]['values'][task_idx])
                    if el['properties'][property]['order'] == 'pseudorandom':
                        random.shuffle(temp_vals)
                    prop_vals[task_name][property] = temp_vals

                #print(task_name, property)
                app_val = prop_vals[task_name][property].pop()
                subtask_properties[task_name][property] += [app_val]

                subtask[property] = subtask_properties[task_name][property].pop()

            # now the subtask could be handed to addTaskTrials?
            cfg = addTaskTrials( el = subtask,
                                 cfg = cfg )


    #print(subtask_properties)

    return(cfg)

def seedRNG(cfg):

    if cfg['settings']['randomization'] == 'individual':
        seed_string = copy.deepcopy(cfg['participant'])
    if cfg['settings']['randomization'] == 'standard':
        seed_string = copy.deepcopy(cfg['name'])

    #sum([ord(l) for l in list(seed_string)])
    random.seed(seed_string)

    return

def runTrialSequence(cfg):

    cfg['run'] = {}

    cfg['run']['trialidx'] = 0

    performance = {}
    performance['targetangle_deg']    = []
    performance['feedbacktype']       = []
    performance['aimdeviation_deg']   = []
    performance['reachdeviation_deg'] = []
    performance['reactiontime_s']     = []
    performance['movementtime_s']     = []

    cfg['run']['performance'] = performance

    while cfg['run']['trialidx'] < len(cfg['triallist']):

        print('EVENT:',cfg['run']['trialidx']+1,' / ', len(cfg['triallist']))

        trialtype = copy.deepcopy(cfg['triallist'][cfg['run']['trialidx']]['type'])

        print('type:',   trialtype,
              'cursor:', cfg['triallist'][cfg['run']['trialidx']]['cursor'],
              'rot:',    cfg['triallist'][cfg['run']['trialidx']]['rotation'],
              'target:', cfg['triallist'][cfg['run']['trialidx']]['target'])

        # THIS IS WHERE CODE COULD BE RUN?
        # if ...
        #

        if trialtype == 'trial':

            [cfg, trialdata] = runTrial(cfg=cfg)

            # SAVE TRIAL DATA as file
            saveTrialdata(cfg=cfg, trialdata=trialdata)

            # store stuff in performance as well
            cfg = storePerformance(cfg=cfg, trialdata=trialdata)

        if trialtype == 'pause':
            cfg = runPause(cfg) # NOT WRITTEN YET!

        # this has to be at the very end!
        cfg['run']['trialidx'] +=1

        # well... before this:
        # STORE JSON!

        storeJSON(cfg)

    cfg['hw']['display'].shutDown()

    return(cfg)


def runTrial(cfg):

    trialdict = copy.deepcopy(cfg['triallist'][cfg['run']['trialidx']])

    targetPos = getTargetPos(cfg)
    targetangle_deg = trialdict['target']
    targetangle_rad = (targetangle_deg/180) * math.pi

    homePos = [0,0] # this could be changed at some point?


    # three kinds of perturbations of visual feedback:
    rotation_deg = trialdict['rotation']
    rotation_rad = (rotation_deg/180)*math.pi
    errorgain = 1
    # distancegain = 1 # NO USE FOR THIS YET: IMPLEMENT LATER

    if trialdict['cursor'] == 'clamped':
        clamped = True
    else:
        clamped = False


    # we need the radius of things:
    [home_radius, target_radius, cursor_radius] = getRadii(cfg)


    # feedbacktypes:
    # - cursor (regular / default)
    # - no-cursor (for reach aftereffects)
    # - clamped (this can have a rotation or distancegain perturbation, but not the errorgain)

    # we collect data about the trial here:
    trialdata = copy.deepcopy(trialdict)
    # we add lists to collect the trajectory:
    trialdata['handx'] = []
    trialdata['handy'] = []
    trialdata['time'] = []
    trialdata['step'] = []
    # what else?


    # STEPS:
    # -3 = get to home position before actual trial starts
    # -2 = hold - without target (timehold)
    # -1 = hold - with target (prephold)
    # 0 = at home, start moving
    # 1 = left home, moving to target
    # 2 = arrived at target (wait/hold at target?) (or target-distance)
    # 3 = at target, home is there: start moving (or target-distance)
    # 4 = moving back, not there yet
    # 5 = at home... wait for some short period?
    # 6 = post-trial period... ? maybe?

    home_target_distance = getDistance(homePos, targetPos)

    inprogress = True
    step = -3
    while inprogress:

        # visual feedback location depends on real location as well:
        [X,Y,time_s] = cfg['hw']['tracker'].getPos()
        trackerPos = [X,Y]

        cursorPos = trackerPos


        home_cursor_distance = getDistance(homePos, cursorPos)
        target_cursor_distance = getDistance(targetPos, cursorPos)


        if clamped:
            cursorPos = [homePos[0] + (math.cos(targetangle_rad)*home_cursor_distance),
                         homePos[1] + (math.sin(targetangle_rad)*home_cursor_distance)]

        if rotation_deg != 0:
            relX, relY = cursorPos[0] - homePos[0], cursorPos[1] - homePos[1]
            unrot = -1 * targetangle_rad
            relativeCursorPos = [(relX * math.cos(unrot)) - (relY * math.sin(unrot)),
                                 (relX * math.sin(unrot)) + (relY * math.cos(unrot))]
            relativeCursorRad = math.atan2(relativeCursorPos[1], relativeCursorPos[0])

            cursorPos = [math.cos(targetangle_rad + relativeCursorRad + rotation_rad) * home_cursor_distance,
                         math.sin(targetangle_rad + relativeCursorRad + rotation_rad) * home_cursor_distance]



        # STEPS NEED TO BE TAKEN:
        if step < 0:
            # SPLIT FOR HOLD PERIODS... right now: only the go to home part
            if (home_cursor_distance <= home_radius):
                #print('entering step 0')
                step = 0

        if step == 0:
            if (home_cursor_distance > home_radius):
                #print('entering step 1')
                step = 1

        if step == 1:
            # IF criterion is DISTANCE:
            if (home_cursor_distance > (home_target_distance - target_radius)):
                #print('entering step 2')
                step = 2

            # acquire:
            # if (target_cursor_distance < target_radius):
            #     step == 2

        if step == 2:
            if (home_cursor_distance < (home_target_distance - target_radius)):
                #print('entering step 4')
                step = 4

            # acquire:
            # if (target_cursor_distance > target_radius):
            #     step == 4

        if step == 3:
            # this would be a HOLD at the target (skipping for now)
            pass

        if step == 4:
            if (home_cursor_distance < home_radius):
                #print('entering current final step')
                step = 5
                inprogress = False
                # back at home
                # for now: nothing else happens but we can have a 5th and 6th step later on


        if (step in [-3, -2, -1, 0, 2, 3, 4]):
            cfg['hw']['display'].showHome(homePos)

        if (step in [0, 1, 2]):
            cfg['hw']['display'].showTarget(targetPos)

        cfg['hw']['display'].showCursor(cursorPos)

        cfg['hw']['display'].doFrame()

        trialdata['handx'].append(trackerPos[0])
        trialdata['handy'].append(trackerPos[1])
        trialdata['time'].append(time_s)
        trialdata['step'].append(step)

    return([cfg, trialdata])

def getTargetPos(cfg):

    # get target angle:
    trialdict = copy.deepcopy(cfg['triallist'][cfg['run']['trialidx']])

    # we need angle and distance:
    angle = trialdict['target']
    rad = (angle/180) * math.pi

    # do we use norm or cm distance? depends on display-unit:
    if (cfg['hw']['display'].units == 'cm'):
        dist = trialdict['targetdistance_cm']
    if (cfg['hw']['display'].units == 'norm'):
        dist = trialdict['targetdistance_norm']

    X = math.cos(rad) * dist
    Y = math.sin(rad) * dist

    return([X,Y])

def getRadii(cfg):

    stimuli = copy.deepcopy(cfg['settings']['stimuli'])

    home_radius = stimuli['home']['radius_cm']
    target_radius = stimuli['target']['radius_cm']
    cursor_radius = stimuli['cursor']['radius_cm']

    # convert to norm units, if display uses those:
    if (cfg['hw']['display'].units == 'norm'):
        # for now: NO CONVERSION!
        [home_radius, target_radius, cursor_radius] = cfg['hw']['display'].cm2norm([home_radius, target_radius, cursor_radius])

    return([home_radius, target_radius, cursor_radius])

def getDistance(pos_a, pos_b=None):

    if pos_b == None:
        pos_b = [0,0]

    return( math.sqrt( (pos_a[0]-pos_b[0])**2 + (pos_a[1]-pos_b[1])**2 ) )

def runPause(cfg):

    return(cfg)

def saveTrialdata(cfg, trialdata):

    # get path from cfg
    # convert trialdata to csv file
    # store in separate trial file

    return

def storePerformance(cfg, trialdata):

    # extract target angle
    # extract feedback type
    # extract aim-deviation (or set to None?)
    # extract reach deviation at X percent, or some given distance
    # extract reaction time (time between GO and leaving HOME)
    # extract movement time (time between leaving HOME and reaching TARGET)

    # other stuff:
    # see if hold was correct? (0/1)
    # see if time/accuracy criteria were met? (0/1)

    return(cfg)

def storeJSON(cfg):

    return
