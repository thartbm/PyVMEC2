import PyVMEC2.hw as hw
import random, json, copy, math, os, sys, shutil, glob
import numpy as np
from scipy import optimize
from time import time
from psychopy import event

# from psychopy.hardware import keyboard
# from pyglet.window import key

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

        if el['type'] == 'aiming':

            cfg = addAimingTrials(cfg=cfg, el=el)


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

            cfg = addPauseTask(cfg=cfg, el=el)

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

def addAimingTrials(cfg, el):

    # print('placeholder function: addAimingTrials()\n no aiming trials added!')

    # print(el)

    task = el

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
    trial = copy.deepcopy(task)
    # strippedtask = copy.deepcopy(task)
    remove_entries = var_prop_names + ['order']
    for k in remove_entries:
        trial.pop(k, None)
    # trial.update(strippedtask)

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

        thistrial['type'] = 'aiming'

        # print(thistrial)

        cfg['run']['triallist'] += [thistrial]

    return(cfg)

def addSuperTaskTrials(cfg, el):

    # nsubtasks = len(el['subtasks'])
    # nproperties = len(el['properties'])
    # nrepeats = el['repeats']

    # prepare the subtask properties:
    # subtasks X properties


    # these are all the properties we need to assign:
    # pro_dic = {}
    prop_orders = {}

    for gr_no in range(len(el['linkedproperties'])):
        gr = el['linkedproperties'][gr_no]
        prop_orders[gr_no] = []


        # these are all the properties that we need to assign:
    pro_dic = {} 
    for k in el['properties'].keys():
        pro_dic[k] = []

    # and we need to assign them to each sub-task:
    subtask_properties = {} 
    for k in range(len(el['subtasks'])):
        subtask_properties[el['subtasks'][k]['name']] = copy.deepcopy(pro_dic)


    # list with property values to populate subtasks
    # this will be refilled when empty while
    # looping through repeats of subtasks
    prop_vals = copy.deepcopy(subtask_properties)

    # now we use:
    # - prop_vals, and
    # - prop_orders
    # to assign values of properties to each subtask on each repeat

    # add trials to triallist:
    for repeat in range(el['repeats']):

        # determine task order:
        taskorder = range(len(el['subtasks']))
        if el['taskorder'] == 'pseudorandom':
            random.shuffle(taskorder)

        # set property orders in all property groups:
        for property_group_no in range(len(el['linkedproperties'])):
            
            property_group = el['linkedproperties'][property_group_no]

            if len(prop_orders[property_group_no]) == 0:
                pk = list(property_group['values'].keys())[0]
                temp_order = list(range(len(property_group['values'][pk][0])))
                if property_group['order'] == 'pseudorandom':
                    random.shuffle(temp_order)
                prop_orders[property_group_no] = temp_order

        # 
        for task_idx in taskorder:
            task_name = el['subtasks'][task_idx]['name']

            # set up a sub-task instance:
            subtask = copy.deepcopy(el['subtasks'][task_idx])

            # populate it with the variable properties:
            for property in el['properties'].keys():
                if len(prop_vals[task_name][property]) == 0:
                    temp_vals = copy.deepcopy(el['properties'][property]['values'][task_idx])
                    if el['properties'][property]['order'] == 'pseudorandom':
                        random.shuffle(temp_vals)
                    prop_vals[task_name][property] = temp_vals

                app_val = prop_vals[task_name][property].pop(0)
                subtask_properties[task_name][property] += [app_val]

                subtask[property] = subtask_properties[task_name][property].pop(0)


            # now get the subtask its linked properties:
            for property_group_no in range(len(el['linkedproperties'])):
                property_group = el['linkedproperties'][property_group_no]
                for prop in property_group['values'].keys():
                    prop_val = property_group['values'][prop][task_idx][prop_orders[property_group_no][0]]
                    subtask[prop] = prop_val




            # now the subtask could be handed to addTaskTrials?
            if subtask['type'] == 'task':
                cfg = addTaskTrials( el = subtask,
                                    cfg = cfg )

            if subtask['type'] == 'aiming':
                cfg = addAimingTrials( el = subtask,
                                    cfg = cfg )
            
            if subtask['type'] == 'pause':
                cfg = addPauseTask( cfg = cfg,
                                    el = subtask )


        # remove property value indices we just used:
        for property_group_no in range(len(el['linkedproperties'])):
            prop_orders[property_group_no].pop(0)


    return(cfg)

# def addSuperTaskTrials(cfg, el):

#     nsubtasks = len(el['subtasks'])
#     nproperties = len(el['properties'])
#     nrepeats = el['repeats']

#     # prepare the subtask properties:
#     # subtasks X properties

#     pro_dic = {} # an empty placeholder for all properties that are varied across subtasks
#     for k in el['properties'].keys():
#         pro_dic[k] = []

#     # print(pro_dic)

#     subtask_properties = {} # properties dictionary for each subtask: the empty one just made
#     for k in range(len(el['subtasks'])):
#         subtask_properties[el['subtasks'][k]['name']] = copy.deepcopy(pro_dic)

#     # print(subtask_properties) # still empty?


#     # list with property values to populate subtasks
#     # this will be refilled when empty while
#     # looping through repeats of subtasks
#     prop_vals = copy.deepcopy(subtask_properties)

#     # add trials to triallist:
#     for repeat in range(el['repeats']):

#         # determine task order:
#         taskorder = range(len(el['subtasks']))
#         if el['taskorder'] == 'pseudorandom':
#             random.shuffle(taskorder)

#         for task_idx in range(len(el['subtasks'])):
#             task_name = el['subtasks'][task_idx]['name']

#             # set up a sub-task instance:
#             subtask = copy.deepcopy(el['subtasks'][task_idx])

#             # populate it with the variable properties:
#             for property in el['properties'].keys():
#                 #print(property)
#                 if len(prop_vals[task_name][property]) == 0:
#                     temp_vals = copy.deepcopy(el['properties'][property]['values'][task_idx])
#                     if el['properties'][property]['order'] == 'pseudorandom':
#                         random.shuffle(temp_vals)
#                     prop_vals[task_name][property] = temp_vals

#                 #print(task_name, property)
#                 app_val = prop_vals[task_name][property].pop(0)
#                 subtask_properties[task_name][property] += [app_val]

#                 subtask[property] = subtask_properties[task_name][property].pop(0)

#             # now the subtask could be handed to addTaskTrials?
#             if subtask['type'] == 'task':
#                 cfg = addTaskTrials( el = subtask,
#                                      cfg = cfg )
            
#             if subtask['type'] == 'pause':
#                 cfg = addPauseTask( cfg = cfg,
#                                     el = subtask )

#     #print(subtask_properties)

#     return(cfg)

def addPauseTask(cfg, el):

    # strip properties of regular tasks?

    # what now? just add it... I guess
    cfg['run']['triallist'] += [el]

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
    performance['label']              = []
    performance['targetangle_deg']    = []
    performance['rotation']           = []
    performance['handerrorgain']      = []
    performance['feedbacktype']       = []
    performance['reachdeviation_deg'] = []
    performance['reactiontime_s']     = []
    performance['movementtime_s']     = []
    performance['scoredpoints']       = []
    performance['cursorerrorgain']    = []
    performance['trialstarttime_s']   = []
    performance['W_hat']              = []
    performance['event_idx']          = []

    cfg['run']['new_W_hat'] = 0

    cfg['run']['performance'] = performance

    # print(cfg['run']['performance'])

    aiming = {}
    aiming['targetangle_deg']    = []
    aiming['arrowoffset_deg']    = []
    aiming['arrowdeviation_deg'] = []
    aiming['steps']              = []
    aiming['completiontime_s']   = []
    aiming['event_idx']          = []

    cfg['run']['aiming'] = aiming

    # points are in here:
    cfg = initializeTrialState(cfg)
    # and steps? could shortcut to step 6 or whatever immediately ends the trial later on...

    while cfg['run']['trialidx'] < len(cfg['run']['triallist']):

        trialdict = copy.copy(cfg['run']['triallist'][cfg['run']['trialidx']])
        trialtype = copy.copy(trialdict['type'])

        # IFF the pretrialscript key exists in the trial dictionary
        if ('pretrialscript' in trialdict.keys()):
            pretrialscript = trialdict['pretrialscript']
            
            # AND it is not None (and actually a string: a filename)
            if (isinstance(pretrialscript, str)):
            
                # the script should be here:
                if pretrialscript in cfg['bin']['scripts'].keys():

                    #print(pretrialscript)

                    # startPTSprep = time()

                    # fetch the binary version of the script:
                    code = cfg['bin']['scripts'][pretrialscript]

                    # get performance on previous trials:
                    performance = copy.deepcopy(cfg['run']['performance'])
                    # and the list of UPCOMING trials only
                    # triallist   = copy.deepcopy(cfg['run']['triallist'][cfg['run']['trialidx']:])
                    # deepcopy takes lots of time, especially on the biggest object:
                    triallist   = copy.copy(cfg['run']['triallist'][cfg['run']['trialidx']:])
                    # this is also the 1 object that we allow people to change, so we can just use 'copy' instead
                    # as well as the trialstate dictionary:
                    trialstate  = copy.deepcopy(cfg['run']['trialstate'])
                    # and the trialdict dictionary? this is actually in the triallist... for ALL upcoming trials
                    
                    # which are put in a 'globals' dictionary
                    g = globals()

                    g['performance'] = performance
                    g['triallist']   = triallist
                    g['trialstate']  = trialstate
                    g['new_W_hat']   = 0

                    # finishPTSprep = time()
                    # print('%0.3f s preparing pre-trial script'%(finishPTSprep-startPTSprep))

                    # accompanied by an empty 'locals' dictionary
                    l = {}
                    # and it is executed
                    exec(code, g, l)

                    for check_key in l.keys():
                        if check_key == 'triallist':
                            cfg['run']['triallist'][cfg['run']['trialidx']:] = copy.copy(l['triallist'])
                        if check_key == 'new_W_hat':
                            cfg['run']['new_W_hat'] = copy.deepcopy(l['new_W_hat'])
                        if check_key == 'trialstate':
                            cfg['run']['trialstate']['persistent']['customvariables']['variables'] = copy.deepcopy(l['trialstate']['persistent']['customvariables']['variables'])

                    # # the updated triallist should now be in the 'locals' dictionary
                    # # so we copy it to the the running trial list
                    # cfg['run']['triallist'][cfg['run']['trialidx']:] = copy.deepcopy(l['triallist'])
                    # cfg['run']['new_W_hat'] = copy.deepcopy(l['new_W_hat'])
                    # cfg['run']['trialstate']['persistent']['customvariables']['variables'] = copy.deepcopy(l['trialstate']['persistent']['customvariables']['variables'])
                    # # print(cfg['run']['new_W_hat'])

        if cfg['run']['trialidx'] >= len(cfg['run']['triallist']):
            # break out of the while loop:
            break

        print('EVENT:',cfg['run']['trialidx']+1,' / ', len(cfg['run']['triallist']))
        trialdict = copy.copy(cfg['run']['triallist'][cfg['run']['trialidx']])
        trialtype = copy.copy(trialdict['type'])

        if trialtype == 'trial':

            print('type:',   trialtype,
                  'cursor:', trialdict['cursor'],
                  'rot:',    trialdict['rotation'],
                  'target:', trialdict['target'])

            [cfg, trialdata] = runTrial(cfg=cfg)

            # startSaveTrial = time()

            # SAVE TRIAL DATA as file
            saveTrialdata(cfg=cfg, trialdata=trialdata)

            # finishSaveTrial = time()
            # print('%0.3f s spent saving trial data'%(finishSaveTrial-startSaveTrial))

            # store stuff in performance as well
            # startStorePerformance = time()
            cfg = storePerformance(cfg=cfg, trialdata=trialdata)
            # finishStorePerformance = time()
            # print('%0.3f s spent storing performance'%(finishStorePerformance-startStorePerformance))

        if trialtype == 'pause':

            cfg = runPause(cfg=cfg)

        if trialtype == 'aiming':

            cfg = runAiming(cfg=cfg)

        # this has to be at the very end!
        cfg['run']['trialidx'] +=1

        # well... before this anyway:
        saveState(cfg) # should this be called "saveState()" ?
    
    savePerformance(cfg) # shorthand data... might be sufficient for some analyses?

    saveAiming(cfg)

    cfg['hw']['display'].shutDown()

    return(cfg)


def runTrial(cfg):

    # startTrialSetup = time()

    trialdict = copy.deepcopy(cfg['run']['triallist'][cfg['run']['trialidx']])

    # set step to -3, scoredpoints to 0, and all stimuli to not be shown
    cfg = resetTransientTrialState(cfg)
    # record trial start time:
    cfg['run']['trialstate']['transient']['trialstarttime'] = time()

    targetPos = getTargetPos(cfg)
    targetangle_deg = trialdict['target']
    targetangle_rad = (targetangle_deg/180) * math.pi

    homePos = [0,0] # this could be changed at some point?

    # three kinds of perturbations of visual feedback:
    # 1: rotations:
    rotation_deg = trialdict['rotation']
    rotation_rad = (rotation_deg/180)*math.pi
    # 2: cursor error gains:
    if 'cursorerrorgain' in trialdict.keys():
        cursorerrorgain = trialdict['cursorerrorgain']
    else:
        trialdict['cursorerrorgain'] = 1
        cursorerrorgain = 1
    
    # 2: hand error gains:
    if 'handerrorgain' in trialdict.keys():
        handerrorgain = trialdict['handerrorgain']
    else:
        trialdict['handerrorgain'] = 1
        handerrorgain = 1
    
    # 3: distance gains:
    distancegain = 1 # NO USE FOR THIS YET: IMPLEMENT LATER

    if trialdict['cursor'] == 'clamped':
        clamped = True
    else:
        clamped = False

    if 'holddurations' in trialdict.keys():
        holddurations = trialdict['holddurations']
        if 'start' not in holddurations.keys():
            holddurations['start'] = 0.000
        if 'target' not in holddurations.keys():
            holddurations['target'] = 0.000
        if 'finish' not in holddurations.keys():
            holddurations['finish'] = 0.000
    else:
        holddurations = { 'start'  : 0.000,
                          'target' : 0.000,
                          'finish' : 0.000 }


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

    # 

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

    # finishTrialSetup = time()
    # print('time spent setting up trial: %0.1f s'%(finishTrialSetup-startTrialSetup))

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

        if (handerrorgain != 1) and (not clamped):
            relX, relY = cursorPos[0] - homePos[0], cursorPos[1] - homePos[1]
            unrot = -1 * targetangle_rad
            relativeCursorPos = [(relX * math.cos(unrot)) - (relY * math.sin(unrot)),
                                 (relX * math.sin(unrot)) + (relY * math.cos(unrot))]
            relativeCursorRad = math.atan2(relativeCursorPos[1], relativeCursorPos[0]) * handerrorgain

            cursorPos = [(math.cos(targetangle_rad + relativeCursorRad) * home_cursor_distance) + homePos[0],
                         (math.sin(targetangle_rad + relativeCursorRad) * home_cursor_distance) + homePos[1]]

        if rotation_deg != 0:
            relX, relY = cursorPos[0] - homePos[0], cursorPos[1] - homePos[1]
            unrot = -1 * targetangle_rad
            relativeCursorPos = [(relX * math.cos(unrot)) - (relY * math.sin(unrot)),
                                 (relX * math.sin(unrot)) + (relY * math.cos(unrot))]
            relativeCursorRad = math.atan2(relativeCursorPos[1], relativeCursorPos[0])

            cursorPos = [(math.cos(targetangle_rad + relativeCursorRad + rotation_rad) * home_cursor_distance) + homePos[0],
                         (math.sin(targetangle_rad + relativeCursorRad + rotation_rad) * home_cursor_distance) + homePos[1]]

        if (cursorerrorgain != 1) and (not clamped):
            relX, relY = cursorPos[0] - homePos[0], cursorPos[1] - homePos[1]
            unrot = -1 * targetangle_rad
            relativeCursorPos = [(relX * math.cos(unrot)) - (relY * math.sin(unrot)),
                                 (relX * math.sin(unrot)) + (relY * math.cos(unrot))]
            relativeCursorRad = math.atan2(relativeCursorPos[1], relativeCursorPos[0]) * cursorerrorgain

            cursorPos = [(math.cos(targetangle_rad + relativeCursorRad) * home_cursor_distance) + homePos[0],
                         (math.sin(targetangle_rad + relativeCursorRad) * home_cursor_distance) + homePos[1]]

        
        # recalculate distances with updated positions:
        home_cursor_distance = getDistance(homePos, cursorPos)
        target_cursor_distance = getDistance(targetPos, cursorPos)

        # STEPS NEED TO BE TAKEN:
        if cfg['run']['trialstate']['transient']['step'] < -1:
            if (home_cursor_distance <= home_radius):
                # start hold:
                cfg['run']['trialstate']['transient']['step'] = -1
                cfg['run']['trialstate']['transient']['StartHoldStartTime']  =  copy.deepcopy(time_s)

        if cfg['run']['trialstate']['transient']['step'] == -1:
            if (home_cursor_distance > home_radius):
                cfg['run']['trialstate']['transient']['step'] = -2
            elif time_s >= (cfg['run']['trialstate']['transient']['StartHoldStartTime'] + holddurations['start']):
                # hold is completed, we move on to step 0, and that is "go time"
                cfg['run']['trialstate']['transient']['step'] = 0
                cfg['run']['trialstate']['transient']['gotime'] = time_s


        # if cfg['run']['trialstate']['transient']['step'] == 0:
        #     # PERIOD BEFORE CURSOR IS AT HOME
        #     # SPLIT FOR HOLD PERIODS... right now: only the go to home part
        #     if (home_cursor_distance <= home_radius):
        #         cfg['run']['trialstate']['transient']['step'] = 0
                

        if cfg['run']['trialstate']['transient']['step'] == 0:
            # AT HOME WITH TARGET PRESENTED... WAITING FOR REACTION
            if (home_cursor_distance > home_radius):
                # print('entering step 1')

                cfg['run']['trialstate']['transient']['step'] = 1
                cfg['run']['trialstate']['transient']['reactiontime'] = time_s - cfg['run']['trialstate']['transient']['gotime']

        if cfg['run']['trialstate']['transient']['step'] == 1:
            # IF criterion is DISTANCE:
            if trialdict['reachcompletioncriterion']['type'] == 'homecursordistance':
                if home_cursor_distance > (trialdict['reachcompletioncriterion']['hometargetdistance_prop'] * home_target_distance):
                    cfg['run']['trialstate']['transient']['step'] = 2
            # IF criterion is ACQUIRE:
            if trialdict['reachcompletioncriterion']['type'] == 'acquire':
                if target_cursor_distance < (trialdict['reachcompletioncriterion']['targetradius_prop'] * target_radius):
                    cfg['run']['trialstate']['transient']['step'] = 2
            
            # update times in transient trial state upon reach completion:
            if cfg['run']['trialstate']['transient']['step'] == 2:
                cfg['run']['trialstate']['transient']['movementtime'] = time_s - cfg['run']['trialstate']['transient']['gotime'] - cfg['run']['trialstate']['transient']['reactiontime']
                cfg['run']['trialstate']['transient']['completiontime'] = cfg['run']['trialstate']['transient']['reactiontime'] + cfg['run']['trialstate']['transient']['movementtime']



        if cfg['run']['trialstate']['transient']['step'] == 2:
            if (home_cursor_distance < (home_target_distance - target_radius)):
                #print('entering step 4')
                cfg['run']['trialstate']['transient']['step'] = 4


        if cfg['run']['trialstate']['transient']['step'] == 3:
            # this would be a HOLD at the target (skipping for now)
            # the criteria should come from the trial-event sequence,
            # and depend on the outward reach completion criterion (acquire target? home-cursor distance?)
            # so not doing this right now... :(
            pass

        if cfg['run']['trialstate']['transient']['step'] == 4:
            # print('in step 4')
            if (home_cursor_distance < home_radius):
                # print('switching to step 5')
                cfg['run']['trialstate']['transient']['step'] = 5
                cfg['run']['trialstate']['transient']['FinishHoldStartTime']  =  copy.deepcopy(time_s)
                # back at home

        if cfg['run']['trialstate']['transient']['step'] == 5:
            # print('in step 5')
            # print('hold duration: %0.3f s'%(time_s - cfg['run']['trialstate']['transient']['FinishHoldStartTime']))
            if (home_cursor_distance > home_radius):
                # print('back to step 4...')
                cfg['run']['trialstate']['transient']['step'] = 4
                #cfg['run']['trialstate']['transient']['FinishHoldStartTime']  =  time_s
            elif time_s >= (cfg['run']['trialstate']['transient']['FinishHoldStartTime'] + holddurations['finish']):
                cfg['run']['trialstate']['transient']['step'] = 6 # not sure what this would do, maybe a blank screen, but for now we say:
                inprogress = False


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

        # positions to implement certain feedback:
        positions = {}
        positions['home_pos'] = homePos
        positions['cursor_pos'] = cursorPos
        positions['target_pos'] = targetPos

        # startCFB = time()
        # check feedback rules:
        trialdict = checkFeedbackRules( cfg        = cfg,
                                        trialdict  = trialdict,
                                        trialdata  = trialdata,
                                        distances  = distances,
                                        positions  = positions  )
        # finishCFB = time()
        # print('time spent checking feedback-rules: %0.f s'%(finishCFB - startCFB))


        # see if anything needs to happen right now:
        [cfg, trialdict] = handleEvents( cfg            = cfg,
                                         trialdict      = trialdict,
                                         trialdata      = trialdata )  # not using trialdata so far...

        # show visual elements
        # THIS SHOULD BE OUTSOURCED to a function:
        if (cfg['run']['trialstate']['transient']['showImprintTarget']):
            cfg['hw']['display'].showTargetImprint(cfg['run']['trialstate']['transient']['imprintTargetPos'])
        if (cfg['run']['trialstate']['transient']['showImprintCursor']):
            cfg['hw']['display'].showCursorImprint(cfg['run']['trialstate']['transient']['imprintCursorPos'])
        if (cfg['run']['trialstate']['transient']['showHome']):
            cfg['hw']['display'].showHome(homePos)
        if cfg['run']['trialstate']['transient']['showTargetArc']:
            cfg['hw']['display'].showTargetArc(homePos)
        if cfg['run']['trialstate']['transient']['showTarget']:
            cfg['hw']['display'].showTarget(targetPos)
        if cfg['run']['trialstate']['transient']['showCursor']:
            cfg['hw']['display'].showCursor(cursorPos)


        # instr = 'step: %d'%cfg['run']['trialstate']['transient']['step']
        # cfg['hw']['display'].showInstructions(txt = instr,
        #                                       pos = (-8,-4) )

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

    # get the config for THIS pause:
    pausedict = copy.deepcopy(cfg['run']['triallist'][cfg['run']['trialidx']])

    pausestart = time()

    pause_ongoing = True
    waiting = True

    while pause_ongoing:

        elapsed = time() - pausestart

        if elapsed > pausedict['wait']:
            waiting = False

        if pausedict['display-type'] == 'text':
            # set the instructions.text to the value of 'display-value'

            cfg['hw']['display'].showInstructions(txt=pausedict['display-value'])

        if (waiting and pausedict['showcountdown']):

            countdown = ''

            timer_s = np.int64(np.ceil(pausedict['wait'] - elapsed))
            timer_m = timer_s // 60
            timer_h = timer_m // 60 # REALLY ??? ah well... why not
            if pausedict['wait'] > 3600:
                countdown = countdown + '%d'%(timer_h)
            if pausedict['wait'] > 60:
                if len(countdown):
                    countdown = countdown + '%02d'%(timer_m)
                else:
                    countdown = countdown + '%d'%(timer_m)
            if len(countdown):
                countdown = countdown + '%02d'%(timer_s)
            else:
                countdown = countdown + '%d'%(timer_s)

            cfg['hw']['display'].showPauseCountdown(txt=countdown)

        # test for the end of the pause "task":

        if not waiting:

            if pausedict['endpause'] == 'timeout':

                pause_ongoing = False

            if pausedict['endpause'] == 'button':
                
                keys = event.getKeys(keyList=['space'])
                if len(keys):
                    if 'space' in keys:
                        pause_ongoing = False

                cfg['hw']['display'].showPauseCountdown(txt='(press SPACE to continue)')

        cfg['hw']['display'].doFrame()

    # I don't think there's anything else to do?

    return(cfg)

def runAiming(cfg):

    trialdict = copy.deepcopy(cfg['run']['triallist'][cfg['run']['trialidx']])

    # print(trialdict)

    pyglet_kb = cfg['hw']['pyglet']['keyboard']
    key       = cfg['hw']['pyglet']['key']


    targetangle_deg = trialdict['target']
    arrowoffset_deg = trialdict['offset']

    targetPos = getTargetPos(cfg)

    # ori = targetangle_deg + arrowoffset_deg
    pos = cfg['settings']['basictrial']['home'] # should this be an option to set in aiming trials as well? YES!!!

    starttime = time()
    steps = 0

    inprogress = True

    while inprogress:

        # show target
        cfg['hw']['display'].showTarget(targetPos)
        cfg['hw']['display'].showAimingarrow(aimingArrowPos=pos, aimingArrowOri=-1*((targetangle_deg + arrowoffset_deg)))
        cfg['hw']['display'].doFrame()

        k = event.getKeys(['up', 'left', 'right', 'w', 'a', 'd', 'space'])
        if k:
            if k[0] in ['up', 'w', 'space']:
                # CHECK CRITERIA ! ! ! ! ! !
                inprogress = False
                if 'required' in trialdict.keys():
                    if 'steps' in trialdict['required']:
                        if steps < trialdict['required']['steps']:
                            inprogress = True
                    if 'time' in trialdict['required']:
                        if (time()-starttime) < trialdict['required']['time']:
                            inprogress = True
        
        if any([pyglet_kb[key.LEFT], pyglet_kb[key.A]]):
            arrowoffset_deg += trialdict['stepsize']
            steps += 1
        if any([pyglet_kb[key.RIGHT], pyglet_kb[key.D]]):
            arrowoffset_deg -= trialdict['stepsize']
            steps += 1
        

    cfg['run']['aiming']['targetangle_deg'].append(targetangle_deg)
    cfg['run']['aiming']['arrowoffset_deg'].append(trialdict['offset'])
    cfg['run']['aiming']['arrowdeviation_deg'].append(arrowoffset_deg)
    cfg['run']['aiming']['steps'].append(steps)
    cfg['run']['aiming']['completiontime_s'].append(time() - starttime)
    cfg['run']['aiming']['event_idx'].append(cfg['run']['trialidx'])

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

    if 'label' in trialdata.keys():
        cfg['run']['performance']['label'].append(trialdata['label'])
        # print(trialdata['label'])
    else:
        cfg['run']['performance']['label'].append('__nolabel__')

    # does this work?
    cfg['run']['performance']['event_idx'].append(cfg['run']['trialidx'])

    cfg['run']['performance']['trialstarttime_s'].append(cfg['run']['trialstate']['transient']['trialstarttime'])

    cfg['run']['performance']['targetangle_deg'].append(trialdata['target'])
    cfg['run']['performance']['rotation'].append(trialdata['rotation'])
    cfg['run']['performance']['handerrorgain'].append(trialdata['handerrorgain'])
    cfg['run']['performance']['cursorerrorgain'].append(trialdata['cursorerrorgain'])
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

    cfg['run']['performance']['scoredpoints'].append(trialdata['scoredpoints'])

    cfg['run']['performance']['W_hat'].append(copy.deepcopy(cfg['run']['new_W_hat']))

    return(cfg)

def savePerformance(cfg):

    performance = cfg['run']['performance']

    performance_array = np.array(tuple(performance.values())).T

    filename = '%s%s_performance.csv'%(cfg['run']['path'], cfg['run']['participant'])

    header = ','.join(performance.keys())

    np.savetxt(filename, performance_array, delimiter=',', header=header, fmt='%s', comments="")

    return

def saveAiming(cfg):

    aiming = cfg['run']['aiming']

    if len(aiming['targetangle_deg']) == 0:
        return # do not save empty array
    
    aiming_array = np.array(tuple(aiming.values())).T

    filename = '%s%s_aiming.csv'%(cfg['run']['path'], cfg['run']['participant'])

    header = ','.join(aiming.keys())

    np.savetxt(filename, aiming_array, delimiter=',', header=header, fmt='%s', comments="")
    
    return


def saveState(cfg):

    # main keys:
    # - name
    # - settings
    # - experiment
    # - run

    # EXCEPT:
    # - run['triallist']

    #print(cfg.keys())

    state = {}
    state_keys = ['name', 'settings', 'experiment', 'run']
    # we exclude 'hw' (monitor object) and 'bin' (sounds, compiled scripts) 
    for k in state_keys:
        if k in cfg.keys():
            if k == 'run':
                # exclude 'triallist' from run
                runkeys = list(cfg['run'].keys())
                runkeys.remove('triallist')
                run = {}
                for runkey in runkeys:
                    run[runkey] = copy.deepcopy(cfg['run'][runkey])
                state[k] = run
            else:
                # all other parts we keep
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

    print(script_files)

    if len(script_files):

        for script_path in script_files:
            if (os.path.exists(script_path)):
                file_name = os.path.basename(script_path)
                script_name = os.path.splitext(file_name)[0]
                # we use that filename:
                with open(script_path) as fh:
                    # to compile whatever is in ther:
                    code = compile( source = fh.read(),
                                    filename = script_path,
                                    mode = 'exec' )
                    cfg['bin']['scripts'][script_name] = code
                    # the compile step is not strictly necessary,
                    # but SO says it gives line numbers in the file if there are errors/crashes
                    # might also run faster?

    #print(cfg['bin']['scripts'].keys())


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


    if 'points' not in cfg['run']['trialstate']['persistent'].keys():
        # actually: this should come from the config json:
        cfg['run']['trialstate']['persistent']['points'] = 0
    if 'run_onset' not in cfg['run']['trialstate']['persistent'].keys():
        cfg['run']['trialstate']['persistent']['run_onset'] = time()

    if 'customvariables' not in cfg['run']['trialstate']['persistent'].keys():
        cfg['run']['trialstate']['persistent']['customvariables'] = { 'rules' : {},
                                                                      'variables' : {} }

    # no other ones here yet...

    return(cfg)

def resetTransientTrialState(cfg):

    cfg['run']['trialstate']['transient']['showCursor']             = False
    cfg['run']['trialstate']['transient']['showHome']               = False
    cfg['run']['trialstate']['transient']['showTarget']             = False
    cfg['run']['trialstate']['transient']['showImprintCursor']      = False
    cfg['run']['trialstate']['transient']['imprintCursorPos']       = (0,0)
    cfg['run']['trialstate']['transient']['showImprintTarget']      = False
    cfg['run']['trialstate']['transient']['imprintTargetPos']       = (0,0)
    cfg['run']['trialstate']['transient']['showTargetArc']          = False
    cfg['run']['trialstate']['transient']['showCursorArc']          = False
    # cfg['run']['trialstate']['transient']['showHand']               = False
    
    cfg['run']['trialstate']['transient']['home'] = False
    cfg['run']['trialstate']['transient']['out']  = False
    cfg['run']['trialstate']['transient']['back'] = False

    cfg['run']['trialstate']['transient']['StartHoldStartTime']      =  0
    # cfg['run']['trialstate']['transient']['StartHoldFinished']       =  0
    cfg['run']['trialstate']['transient']['FinishHoldStartTime']     =  0
    # cfg['run']['trialstate']['transient']['FinishHoldFinished']      =  0
    cfg['run']['trialstate']['transient']['targetHoldStartTime']     =  0
    # cfg['run']['trialstate']['transient']['targetHoldFinished']      =  0
    cfg['run']['trialstate']['transient']['step']                    = -3

    # cfg['run']['trialstate']['transient']
    # timing information:
    cfg['run']['trialstate']['transient']['trialstarttime']         =  0
    cfg['run']['trialstate']['transient']['gotime']                 =  0
    cfg['run']['trialstate']['transient']['reactiontime']           =  0
    cfg['run']['trialstate']['transient']['movementtime']           =  0
    cfg['run']['trialstate']['transient']['completiontime']         =  0

    return(cfg)

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
            do_event = checkTimeTrigger(trigger = event['trigger'])
            # if do_event:
            #     print(event)
            #     print(cfg['run']['trialstate']['transient']['imprintCursorPos'])

        if do_event:
            # implement the effect
            trialdict = implementEventEffect(event=event, cfg=cfg, trialdict=trialdict)
            # remove the event, since we only have to do it once!
            remove_events += [event_idx]

    remove_events.sort(reverse=True)
    for del_event in remove_events:
        # print({'del_event':del_event, 'len_events':len(trialdict["events"])})
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

    for effect in event['effects']:

        if effect['type'] == 'transient-state':
            if effect['delay'] == 0:
                # we implement the effect right away
                for param in effect['parameters'].keys():
                    cfg['run']['trialstate']['transient'][param] = effect['parameters'][param]
            else:
                # we add the effect as a timed effect to the event list
                new_event = copy.deepcopy(event)
                # print(event['effects'])
                new_event['property']        = 'time'
                new_event['value']           = time() + effect['delay']
                new_event['effects']['delay'] = 0
                trialdict['events'] += [new_event]

        if effect['type'] == 'sound':
            cfg['hw']['sounds'][effect['file']].play()

        if effect['type'] == 'stimulus-properties':
            for propdict in effect['changes']:
                # print(propdict)
                cfg['hw']['display'].setProperties(propdict)

        if effect['type'] == 'stimulus-objects':
            # only cursor for now?
            for objdict in effect['changes']:
                print('switching objects?')
                cfg['hw']['display'].switchObjects(cfg, objdict)
                

    return(trialdict)

def checkFeedbackRules(cfg, trialdict, trialdata, distances, positions):

    new_events = []

    # trialdict['feedback'] will have the feedback rules
    # trialdata will have all data necessary to check the rules

    feedbackrules = copy.deepcopy(trialdict['feedbackrules'])

    remove_feedbackrules = []

    for fbr_idx in range(len(feedbackrules)):

        fbr = feedbackrules[fbr_idx]
        #satisfied = False ?? not even sure if the rule needs to be applied at all...
        
        # do we test the rule?
        if testEvent(event = fbr['event'],
                     cfg = cfg,
                     trialdict = trialdict,
                     trialdata = trialdata,
                     distances = distances,
                     positions = positions):
            rule_passed = True # will fail on missing any single specified criterion
        else:
            continue # check next rule

        # whether or not the tests are passed: the rule is removed
        remove_feedbackrules += [fbr_idx]

        for cr in fbr['criteria']:   # loop through list of criteria, each is a dict
            
            crit_type = list(cr.keys())[0]

            if crit_type == 'speed':
                if testSpeed(test = cr['speed'],
                             cfg = cfg):
                    #print('rule passed')
                    pass
                else:
                    #print('rule failed')
                    rule_passed = False

            if crit_type == 'accuracy':
                if testAccuracy(test = cr['accuracy'],
                                positions = positions,
                                distances = distances):
                    #print('rule passed')
                    pass
                else:
                    #print('rule failed')
                    rule_passed = False
        
        for fb in fbr['feedback']:
            fb_type = list(fb.keys())[0]

            if rule_passed:
                value = fb[fb_type]['value'][0]
            else:
                value = fb[fb_type]['value'][1]

            if fb_type == 'imprint':
                now    = time()
                onset  = now + fb['imprint']['event']['duration'][0]
                offset = now + fb['imprint']['event']['duration'][1]
                # technically, the below thing is only for cursors... will make more flexible later:

                if value == 'cursor':
                    cfg['run']['trialstate']['transient']['imprintCursorPos'] = positions['cursor_pos']
                    new_events += [ {'trigger' : {'type'      : 'time',
                                                'value'     :  onset},
                                    'effects' : [{ 'type'       : 'transient-state',
                                                'delay'      : 0,
                                                'parameters' : {'showImprintCursor' : True}}]},
                                    {'trigger' : {'type'      : 'time',
                                                'value'     :  offset},
                                    'effects' : [{ 'type'       : 'transient-state',
                                                'delay'      : 0,
                                                'parameters' : {'showImprintCursor' : False}}]} ]             
                if value == 'target':
                    cfg['run']['trialstate']['transient']['imprintTargetPos'] = positions['target_pos']
                    cfg['run']['trialstate']['transient']['imprintCursorPos'] = positions['cursor_pos']
                    new_events += [ {'trigger' : {'type'      : 'time',
                                                'value'     :  onset},
                                    'effects' : [{ 'type'       : 'transient-state',
                                                'delay'      : 0,
                                                'parameters' : {'showImprintTarget' : True}}]},
                                    {'trigger' : {'type'      : 'time',
                                                'value'     :  offset},
                                    'effects' : [{ 'type'       : 'transient-state',
                                                'delay'      : 0,
                                                'parameters' : {'showImprintTarget' : False}}]} ] 
                    
            if fb_type == 'sound':
                
                if fb[fb_type]['event']['type'] == 'time':
                    onset = time() + fb[fb_type]['event']['delay']
                    
                    new_events += [ {'trigger' : {'type' : 'time', 'value': onset},
                                     'effects'  : [{'type' : 'sound', 'file' : value}]} ]
                #print(new_events[-1])

                
    trialdict['events'] += new_events

    remove_feedbackrules.sort(reverse=True)
    for del_fbr in remove_feedbackrules:
        del trialdict['feedbackrules'][del_fbr]

    return(trialdict)

def testEvent(event, cfg, trialdict, trialdata, distances, positions):

    if event['type'] == 'transient-state-change':
        if cfg['run']['trialstate']['transient'][event['property']] != event['value']:
            return(False)
        else:
            return(True)

    print('event rule untested, considered failed')
    return(False)

def testSpeed(test, cfg):

    if test['testvariable'] in ['reactiontime', 'movementtime', 'completiontime']:
        value = cfg['run']['trialstate']['transient'][test['testvariable']]
    
    if value >= test['testrange'][0] and value <= test['testrange'][1]:
        #print('speed test passed')
        return(True)
    #print('speed test failed')

    return(False)

def testAccuracy(test, positions, distances):

    if test['testvariable'] in ['home_cursor_distance', 'target_cursor_distance', 'home_target_distance']:
        value = distances[test['testvariable']]
    if test['testvariable'] in ['target_home_cursor_angle']:
        hp = np.array(positions['home_pos'])
        cp = np.array(positions['cursor_pos']) - hp
        tp = np.array(positions['target_pos']) - hp
        ta = -1 * np.arctan2(tp[1], tp[0])
        R = np.array([[np.cos(ta), -1*np.sin(ta)],[np.sin(ta),np.cos(ta)]])
        [x,y] = R @ cp.T
        reachdev = ((np.arctan2(y,x)/np.pi)*180)
        value = abs(reachdev)

    if value >= test['testrange'][0] and value <= test['testrange'][1]:
        return(True)

    return(False)