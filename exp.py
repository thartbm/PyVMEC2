import PyVMEC2.hw as hw
import random, json, copy, math, os, sys, shutil, glob
import numpy as np
from scipy import optimize

# to make the scripts leaner, we should use numpy and homebrew for saving csvs, but:
#import pandas as pd

def runExperiment(experiment, participant):


# FROM: https://discourse.psychopy.org/t/keypress-using-event-watikeys-not-working-until-after-mouse-click/9288

# # Kill switch for Psychopy3 
# esc_key= 'escape'
# def quit():
#     """ quit programme"""
#     print ('User exited')
#     win.close()
#     core.quit()
# # call globalKeys so that whenever user presses escape, quit function called
# event.globalKeys.add(key=esc_key, func=quit)


    cfg = {}
    cfg['run'] = {}
    cfg['run']['experiment'] = experiment
    cfg['run']['participant'] = participant
    cfg['run']['jsonfile'] = 'experiments/%s/%s.json'%(experiment, experiment)

    cfg = setupRun(cfg)

    # active ESCAPE key

    cfg = runTrialSequence(cfg)

def setupRun(cfg):

    # setup folders and check if they are already there
    # (and filled with some data?)
    [cfg, doCrashRecovery] = setupFolder(cfg)

    if doCrashRecovery:
        cfg = crashRecovery(cfg)
    else:
        cfg = loadJSON(cfg)
        cfg = seedRNG(cfg)
        cfg = getTrialSequence(cfg)

    # these two will have to be done regardless
    # because they create non-hashable (binary) objects
    cfg = hw.setupHardware(cfg)
    cfg = loadScripts(cfg)

    saveState(cfg)
    return(cfg)

def setupFolder(cfg):

    cfg['run']['path'] = 'experiments/%s/data/%s/'%(cfg['run']['experiment'], cfg['run']['participant'])

    if (os.path.exists(cfg['run']['path'])):
        print('participant path already exists')
        doCrashRecovery = True
    else:
        os.makedirs(cfg['run']['path'])
        shutil.copy('experiments/%s/%s.json'%(cfg['run']['experiment'],cfg['run']['experiment']),cfg['run']['path'])
        doCrashRecovery = False

    return([cfg, doCrashRecovery])

def crashRecovery(cfg):

    print('crash recovery not implemented: exiting')
    sys.exit(1)

    # implement:
    # - get state from state.json on path
    # - log a crash recovery in the state
    # - and setup the hardware again (and potentially other non-hashables)

    return(cfg)

def loadJSON(cfg):

    with open(cfg['run']['jsonfile']) as fp:
        cfg.update(json.load(fp))

    return(cfg)

def getTrialSequence(cfg):

    cfg['run']['triallist'] = []

    # # simple start... shouldn't this be in the json?
    # cfg['run']['basictrial'] = {'target'   : 0,
    #                             'rotation' : 0,
    #                             'cursor'   : 'normal',
    #                             'name'     : '' }

    # we can add other functionality later on:
    # - aiming, cursor/target jumps, points... holding home/target

    for el in copy.deepcopy(cfg['experiment']):

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

        cfg['run']['triallist'] += [thistrial]

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
        seed_string = copy.deepcopy(cfg['run']['participant'])
    if cfg['settings']['randomization'] == 'standard':
        seed_string = copy.deepcopy(cfg['name'])

    #sum([ord(l) for l in list(seed_string)])
    random.seed(seed_string)

    # if we want 2 separate random number generator states, we could use:
    # random.getstate()
    # random.setstate()
    # we keep the two states, and can seed one for the experiment /group
    # and the other for the individual participant(s)
    # that means some subtasks or properties can be the same for all participants
    # but other things are randomized individually

    # if the RNG states are hashable, they can be stored in the state.json as well

    # for this, we return the cfg dict

    return(cfg)

def runTrialSequence(cfg):

    cfg['run']['trialidx'] = 0

    performance = {}
    performance['targetangle_deg']    = []
    performance['rotation']           = []
    performance['errorgain']          = []
    performance['feedbacktype']       = []
    performance['reachdeviation_deg'] = []
    performance['reactiontime_s']     = []
    performance['movementtime_s']     = []
    performance['scoredpoints']       = []

    cfg['run']['performance'] = performance

    # points are in here:
    cfg = initializeTrialState(cfg)

    while cfg['run']['trialidx'] < len(cfg['run']['triallist']):

        trialdict = copy.deepcopy(cfg['run']['triallist'][cfg['run']['trialidx']])
        trialtype = copy.deepcopy(trialdict['type'])

        # IFF the pretrialscript key exists in the trial dictionary
        if ('pretrialscript' in trialdict.keys()):
            pretrialscript = trialdict['pretrialscript']
            # AND it is not None (and actually a string: a filename)
            if (isinstance(pretrialscript, str)):

                # the script should be here:
                if pretrialscript in cfg['bin']['scripts'].keys():

                    code = cfg['bin']['scripts'][pretrialscript]

                    performance = copy.deepcopy(cfg['run']['performance'])
                    # and the list of UPCOMING trials only
                    triallist   = copy.deepcopy(cfg['run']['triallist'][cfg['run']['trialidx']:])
                    # which are put in a 'globals' dictionary
                    g = globals()
                    g['performance'] = performance
                    g['triallist']   = triallist
                    # accompanied by an empty 'locals' dictionary
                    l = {}
                    # and it is executed
                    exec(code, g, l)

                    # the updated triallist should now be in the 'locals' dictionary
                    # so we copy it to the the running trial list
                    cfg['run']['triallist'][cfg['run']['trialidx']:] = copy.deepcopy(l['triallist'])



                # filename = 'experiments/%s/resources/scripts/%s.py'%(cfg['run']['experiment'],pretrialscript)
                # if (os.path.exists(filename)):
                #
                #     # we use that filename:
                #     with open(filename) as fh:
                #         # to compile whatever is in ther:
                #         code = compile( source = fh.read(),
                #                         filename = filename,
                #                         mode = 'exec' )
                #         # the compile step is not strictly necessary,
                #         # but SO says it gives line numbers in the file if there are errors/crashes
                #
                #         # it gets as input the previous performance (not used in my example)
                #         performance = copy.deepcopy(cfg['run']['performance'])
                #         # and the list of UPCOMING trials only
                #         triallist   = copy.deepcopy(cfg['run']['triallist'][cfg['run']['trialidx']:])
                #         # which are put in a 'globals' dictionary
                #         g = globals()
                #         g['performance'] = performance
                #         g['triallist']   = triallist
                #         # accompanied by an empty 'locals' dictionary
                #         l = {}
                #         # and it is executed
                #         exec(code, g, l)
                #
                #         # the updated triallist should now be in the 'locals' dictionary
                #         # so we copy it to the the running trial list
                #         cfg['run']['triallist'][cfg['run']['trialidx']:] = copy.deepcopy(l['triallist'])


        print('EVENT:',cfg['run']['trialidx']+1,' / ', len(cfg['run']['triallist']))
        trialdict = copy.deepcopy(cfg['run']['triallist'][cfg['run']['trialidx']])
        trialtype = copy.deepcopy(trialdict['type'])

        if trialtype == 'trial':

            print('type:',   trialtype,
                  'cursor:', trialdict['cursor'],
                  'rot:',    trialdict['rotation'],
                  'target:', trialdict['target'])

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

        saveState(cfg) # should this be called "saveState()" ?

    cfg['hw']['display'].shutDown()

    return(cfg)


def runTrial(cfg):

    trialdict = copy.deepcopy(cfg['run']['triallist'][cfg['run']['trialidx']])




    # # show visual elements
    # if (cfg['run']['trialstate']['transient']['step'] in [-3, -2, -1, 0, 2, 3, 4]):
    #     cfg['hw']['display'].showHome(homePos)
    # if (cfg['run']['trialstate']['transient']['step'] in [0, 1, 2]):
    #     cfg['hw']['display'].showTarget(targetPos)


    # set step to -3, scoredpoints to 0, and all stimuli to not be shown
    cfg = resetTransientTrialState(cfg)

    targetPos = getTargetPos(cfg)
    #print(targetPos)
    targetangle_deg = trialdict['target']
    targetangle_rad = (targetangle_deg/180) * math.pi

    homePos = [0,0] # this could be changed at some point?

    # three kinds of perturbations of visual feedback:
    # 1: rotations:
    rotation_deg = trialdict['rotation']
    rotation_rad = (rotation_deg/180)*math.pi
    # 2: error gains:
    if 'errorgain' in trialdict.keys():
        errorgain = trialdict['errorgain']
    else:
        errorgain = 1
    # 3: distance gains:
    distancegain = 1 # NO USE FOR THIS YET: IMPLEMENT LATER

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
    trialdata['events'] = []
    # what else?

    trialdata['targetpos'] = targetPos
    trialdata['scoredpoints'] = 0

    # STEPS:
    # -3  =  get to home position before actual trial starts
    # -2  =  hold - without target (timehold)
    # -1  =  hold - with target (prephold)
    #  0  =  at home, start moving (go signal)
    #  1  =  left home, moving to target
    #  2  =  arrived at target or target distance or stopped at minimal distance... (include wait/hold at end point?)
    #  3  =  at target, home is there: start moving (or target-distance)
    #  4  =  moving back, not there yet
    #  5  =  at home... wait for some short period?
    #  6  =  post-trial period... ? maybe?



    home_target_distance = getDistance(homePos, targetPos)
    target_radius = cfg['hw']['display'].target.radius

    inprogress = True

    planned_events = []

    while inprogress:

        # visual feedback location depends on real location as well:
        [X,Y,time_s] = cfg['hw']['tracker'].getPos()
        trackerPos = [X,Y]

        frame_events = []

        cursorPos = trackerPos


        home_cursor_distance = getDistance(homePos, cursorPos)
        target_cursor_distance = getDistance(targetPos, cursorPos)


        if clamped:
            # cursorPos = [homePos[0] + (math.cos(targetangle_rad)*home_cursor_distance),
            #              homePos[1] + (math.sin(targetangle_rad)*home_cursor_distance)]
            relX, relY, unrot = cursorPos[0] - homePos[0], cursorPos[1] - homePos[1], -1 * targetangle_rad
            relX, relY = (relX * math.cos(unrot)) - (relY * math.sin(unrot)), 0
            #print([relX, relY])
            cursorPos = [(relX * math.cos(targetangle_rad)) - (relY * math.sin(targetangle_rad)),
                                 (relX * math.sin(targetangle_rad)) + (relY * math.cos(targetangle_rad))]

        if rotation_deg != 0:
            relX, relY = cursorPos[0] - homePos[0], cursorPos[1] - homePos[1]
            unrot = -1 * targetangle_rad
            relativeCursorPos = [(relX * math.cos(unrot)) - (relY * math.sin(unrot)),
                                 (relX * math.sin(unrot)) + (relY * math.cos(unrot))]
            relativeCursorRad = math.atan2(relativeCursorPos[1], relativeCursorPos[0])

            cursorPos = [(math.cos(targetangle_rad + relativeCursorRad + rotation_rad) * home_cursor_distance) + homePos[0],
                         (math.sin(targetangle_rad + relativeCursorRad + rotation_rad) * home_cursor_distance) + homePos[1]]

        if (errorgain != 1) and (not clamped):
            relX, relY = cursorPos[0] - homePos[0], cursorPos[1] - homePos[1]
            unrot = -1 * targetangle_rad
            relativeCursorPos = [(relX * math.cos(unrot)) - (relY * math.sin(unrot)),
                                 (relX * math.sin(unrot)) + (relY * math.cos(unrot))]
            relativeCursorRad = math.atan2(relativeCursorPos[1], relativeCursorPos[0]) * errorgain

            cursorPos = [(math.cos(targetangle_rad + relativeCursorRad) * home_cursor_distance) + homePos[0],
                         (math.sin(targetangle_rad + relativeCursorRad) * home_cursor_distance) + homePos[1]]

        # STEPS NEED TO BE TAKEN:
        if cfg['run']['trialstate']['transient']['step'] < 0:
            # PERIOD BEFORE CURSOR IS AT HOME
            # SPLIT FOR HOLD PERIODS... right now: only the go to home part
            if (home_cursor_distance <= home_radius):
                cfg['run']['trialstate']['transient']['step'] = 0

        if cfg['run']['trialstate']['transient']['step'] == 0:
            # AT HOME WITH TARGET PRESENTED... WAITING FOR REACTION
            if (home_cursor_distance > home_radius):
                # print('entering step 1')
                cfg['run']['trialstate']['transient']['step'] = 1

        if cfg['run']['trialstate']['transient']['step'] == 1:
            # IF criterion is DISTANCE:
            if trialdict['reachcompletioncriterion']['type'] == 'homecursordistance':
                if home_cursor_distance > (trialdict['reachcompletioncriterion']['hometargetdistance_prop'] * home_target_distance):
                    cfg['run']['trialstate']['transient']['step'] = 2

            if trialdict['reachcompletioncriterion']['type'] == 'acquire':
                if target_cursor_distance < (trialdict['reachcompletioncriterion']['targetradius_prop'] * target_radius):
                    cfg['run']['trialstate']['transient']['step'] = 2

        if cfg['run']['trialstate']['transient']['step'] == 2:
            if (home_cursor_distance < (home_target_distance - target_radius)):
                #print('entering step 4')
                cfg['run']['trialstate']['transient']['step'] = 4

        if cfg['run']['trialstate']['transient']['step'] == 3:
            # this would be a HOLD at the target (skipping for now)
            pass

        if cfg['run']['trialstate']['transient']['step'] == 4:
            if (home_cursor_distance < home_radius):
                cfg['run']['trialstate']['transient']['step'] = 5
                inprogress = False
                # back at home
                # for now: nothing else happens but we can have a 5th and 6th step later on


        # record trajectory:
        trialdata['handx'].append(trackerPos[0])
        trialdata['handy'].append(trackerPos[1])
        trialdata['time'].append(time_s)
        trialdata['step'].append(cfg['run']['trialstate']['transient']['step'])

        trialdata['events'].append('') # 

        # distances to check feedback rules:
        distances = {}
        distances['home_cursor_distance']  = home_cursor_distance
        distances['target_cursor_distance'] = target_cursor_distance
        distances['home_target_distance']   = home_target_distance

        # check feedback rules:
        trialdict['events'] += checkFeedbackRules( cfg        = cfg,
                                                   trialdict  = trialdict,
                                                   trialdata  = trialdata,
                                                   distances  = distances  )

        # see if anything needs to happen right now:
        [cfg, trialdict] = handleEvents( cfg            = cfg,
                                         trialdict      = trialdict,
                                         trialdata      = trialdata )  # not using trialdata so far...

        # # show visual elements
        # if (cfg['run']['trialstate']['transient']['step'] in [-3, -2, -1, 0, 2, 3, 4]):
        #     cfg['hw']['display'].showHome(homePos)

        # if (cfg['run']['trialstate']['transient']['step'] in [0, 1, 2]):
        #     cfg['hw']['display'].showTarget(targetPos)

        print(cfg['run']['trialstate']['transient']['showHome'])
        if (cfg['run']['trialstate']['transient']['showHome']):
            cfg['hw']['display'].showHome(homePos)
        if cfg['run']['trialstate']['transient']['showTarget']:
            cfg['hw']['display'].showTarget(targetPos)
        if cfg['run']['trialstate']['transient']['showCursor']:
            cfg['hw']['display'].showCursor(cursorPos)


        instr = 'step: %d'%cfg['run']['trialstate']['transient']['step']
        cfg['hw']['display'].showInstructions(txt = instr,
                                              pos = (-8,-4) )

        cfg['hw']['display'].doFrame()


    return([cfg, trialdata])

def getTargetPos(cfg):

    # get target angle:
    trialdict = copy.deepcopy(cfg['run']['triallist'][cfg['run']['trialidx']])

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

    # maybe this should be dimensionality agnostic
    # so it could work in VR too?

    if pos_b == None:
        pos_b = [0,0]

    return( math.sqrt( (pos_a[0]-pos_b[0])**2 + (pos_a[1]-pos_b[1])**2 ) )

def runPause(cfg):

    return(cfg)

def saveTrialdata(cfg, trialdata):

    # get path from cfg
    # convert trialdata to csv file
    # store in separate trial file

    #print(trialdata)

    samples = len(trialdata['handx'])
    display_unit = copy.deepcopy(cfg['hw']['display'].units)
    tracker_unit = copy.deepcopy(cfg['hw']['tracker'].units)

    data = {}
    data['trial'] = [cfg['run']['trialidx']] * samples
    data['task'] = [trialdata['name']] * samples
    data['targetangle_deg'] = [trialdata['target']] * samples
    data['targetx_%s'%(display_unit)] = [trialdata['targetpos'][0]] * samples
    data['targety_%s'%(display_unit)] = [trialdata['targetpos'][1]] * samples
    data['cursor'] = [trialdata['cursor']] * samples
    data['rotation'] = [trialdata['rotation']] * samples
    data['handx_%s'%(tracker_unit)] = trialdata['handx']
    data['handy_%s'%(tracker_unit)] = trialdata['handy']
    data['time_s'] = trialdata['time']
    data['step'] = trialdata['step']

    data_array = np.array(tuple(data.values())).T

    filename = '%strial_%04d.csv'%(cfg['run']['path'],cfg['run']['trialidx'])

    header = ','.join(data.keys())

    np.savetxt(filename, data_array, delimiter=',', header=header, fmt='%s', comments="")

    return

def storePerformance(cfg, trialdata):

    cfg['run']['performance']['targetangle_deg'].append(trialdata['target'])
    cfg['run']['performance']['rotation'].append(trialdata['rotation'])
    cfg['run']['performance']['errorgain'].append(trialdata['errorgain'])
    cfg['run']['performance']['feedbacktype'].append(trialdata['cursor'])

    display_unit = cfg['hw']['display'].units
    tracker_unit = cfg['hw']['tracker'].units

    data = {}
    data['step'] = trialdata['step']
    data['handx_%s'%(tracker_unit)] = trialdata['handx']
    data['handy_%s'%(tracker_unit)] = trialdata['handy']
    data['time_s'] = trialdata['time']


    # CALCULATE REACH DEVIATION AT FIRST SAMPLE BEYOND 25% HOME-TARGET DISTANCE
    arr = np.array(tuple(data.values())).T
    # use steps 0,1,2 (maybe only step 1?)
    arr = arr[arr[:,0] >= 0]
    arr = arr[arr[:,0] <= 2]
    home = trialdata['home']
    target = trialdata['targetpos']
    XY = arr[:,np.array([1,2])]
    XY = XY - np.array(home)
    distance = np.sqrt(XY[:,0]**2 + XY[:,1]**2)
    distcrit = 0.25 * math.sqrt((target[0] - home[0])**2 + (target[1] - home[1])**2)
    q_idx = np.where(distance >= distcrit)[0][0]
    #print(threshold_idx)
    xd, yd = XY[q_idx,0], XY[q_idx,1]
    unrot = -1 * ((trialdata['target']/180)*np.pi)
    reachdev = (math.atan2((xd * math.sin(unrot)) + (yd * math.cos(unrot)), (xd * math.cos(unrot)) - (yd * math.sin(unrot)))/np.pi)*180
    cfg['run']['performance']['reachdeviation_deg'].append(reachdev)

    start_s = min(arr[:,3])
    arr0 = arr[arr[:,0] == 0]
    reactiontime = max(arr0[:,3]) - start_s
    cfg['run']['performance']['reactiontime_s'].append(reactiontime)
    movementtime = max(arr[:,3]) - start_s - reactiontime
    cfg['run']['performance']['movementtime_s'].append(movementtime)

    return(cfg)

def saveState(cfg):

    # main keys:
    # - name
    # - settings
    # - experiment
    # - run

    #print(cfg.keys())

    state = {}
    state_keys = ['name', 'settings', 'experiment', 'run']
    for k in state_keys:
        if k in cfg.keys():
            state[k] = copy.deepcopy(cfg[k])

    filename = '%s/state.json'%(cfg['run']['path'])

    with open( file=filename,
               mode='w') as fp:
        json.dump(state, fp, indent=2)

    return

def loadScripts(cfg):

    cfg['bin'] = {}
    cfg['bin']['scripts'] = {}

    script_files = glob.glob('experiments/%s/resources/scripts/*.py'%(cfg['run']['experiment']), recursive=False)

    if len(script_files):

        for script_file in script_files:
            # the script should be here:
            filename = 'experiments/%s/resources/scripts/%s.py'%(cfg['run']['experiment'],script_file)
            if (os.path.exists(filename)):
                # we use that filename:
                with open(filename) as fh:
                    # to compile whatever is in ther:
                    code = compile( source = fh.read(),
                                    filename = filename,
                                    mode = 'exec' )
                    cfg['bin']['scripts'][script_file] = code
                    # the compile step is not strictly necessary,
                    # but SO says it gives line numbers in the file if there are errors/crashes
                    # might also run faster?


    return( cfg )

def initializeTrialState(cfg):

    cfg['run']['trialstate'] = {}

    # this is done only at the start of the experiment:
    cfg['run']['trialstate']['persistent'] = {}
    cfg = resetPersistentTrialState(cfg)

    # this is done before (or after?) each trial:
    cfg['run']['trialstate']['transient']  = {}
    cfg = resetTransientTrialState(cfg)

    return(cfg)

def resetPersistentTrialState(cfg):

    # actually: this should come from the config json:
    cfg['run']['trialstate']['persistent']['points'] = 0

    # no other ones here yet...

    return(cfg)

def resetTransientTrialState(cfg):

    cfg['run']['trialstate']['transient']['showCursor']             = False
    cfg['run']['trialstate']['transient']['showHome']               = False
    cfg['run']['trialstate']['transient']['showTarget']             = False
    cfg['run']['trialstate']['transient']['showImprintCursor']      = False
    cfg['run']['trialstate']['transient']['showImprintTarget']      = False
    cfg['run']['trialstate']['transient']['showTargetArc']          = False
    cfg['run']['trialstate']['transient']['showCursorArc']          = False
    # cfg['run']['trialstate']['transient']['showHand']               = False
    
    cfg['run']['trialstate']['transient']['home'] = False
    cfg['run']['trialstate']['transient']['out']  = False
    cfg['run']['trialstate']['transient']['back'] = False

    cfg['run']['trialstate']['transient']['homeStartHoldFinished']  =  0
    cfg['run']['trialstate']['transient']['homeFinishHoldFinished'] =  0
    cfg['run']['trialstate']['transient']['targetHoldFinished']     =  0
    cfg['run']['trialstate']['transient']['step']                   = -3

    # cfg['run']['trialstate']['transient']
    # timing information:
    cfg['run']['trialstate']['transient']['trialstarttime']         =  0
    cfg['run']['trialstate']['transient']['gotime']                 =  0
    cfg['run']['trialstate']['transient']['reactiontime']           =  0
    cfg['run']['trialstate']['transient']['movementtime']           =  0
    cfg['run']['trialstate']['transient']['completiontime']         =  0

    return(cfg)


def checkFeedbackRules(cfg, trialdict, trialdata, distances):

    new_events = []

    # trialdict['feedback'] will have the feedback rules
    # trialdata will have all data necessary to check the rules

    feedbackrules = copy.deepcopy(trialdict['feedbackrules'])

    for fbr in feedbackrules:
        #satisfied = False ?? not even sure if the rule needs to be applied at all...
        # print(fbr.keys())
        rule_passed = True # set to False on a single failed criterion
        for cr in fbr['criteria']:   # loop through list of criteria, each is a dict
            
            crit_type = list(cr.keys())[0]

            if crit_type == 'event':
                # stuff that just happens
                print( cr )
                print( cfg['hw']['display'].target_radius )
                if cr['event']['type'] == 'location':
                    if cr['event']['at'] == 'target':
                        # check if people are at the target:
                        pass

                pass

            if crit_type == 'speed':
                pass

            if crit_type == 'accuracy':
                pass

    return(new_events)

def handleEvents( cfg, trialdict, trialdata):

    events = trialdict["events"]
    remove_events = []

    for event_idx in range(len(events)):
        # print(event_idx)
        # print(len(events))

        event = events[event_idx]
        do_event = False
        if event['trigger']['type'] == 'transient-state-change':
            do_event = checkTransientStateChangeTrigger(cfg=cfg, trigger=event['trigger'])
        if event['trigger']['type'] == 'time':
            do_event = checkTimeTrigger(trigger = trigger)

        if do_event:
            # implement the effect
            trialdict = implementEventEffect(event=event, cfg=cfg, trialdict=trialdict)
            # remove the event, since we only have to do it once!
            remove_events += [event_idx]

    for del_event in remove_events:
        del trialdict["events"][del_event]

    return(cfg, trialdict)

def checkTransientStateChangeTrigger(cfg, trigger):
    check = False
    if cfg['run']['trialstate']['transient'][trigger['property']] == trigger['value']:
        check = True
    return(check)

def checkTimeTrigger(trigger):
    check = False
    now = time()
    if now > trigger['value']:
        check = True
    return(check)

def implementEventEffect(event, cfg, trialdict):

    effect = event['effect']

    if effect['type'] == 'transient-state':
        if effect['delay'] == 0:
            # we implement the effect right away
            for param in effect['parameters'].keys():
                cfg['run']['trialstate']['transient'][param] = effect['parameters'][param]
        else:
            # we add the effect as a timed effect to the event list
            new_event = copy.deepcopy(event)
            new_event['property']        = 'time'
            new_event['value']           = time() + effect['delay']
            new_event['effect']['delay'] = 0
            trialdict['events'] += [new_event]

    return(trialdict)