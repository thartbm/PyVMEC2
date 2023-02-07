import hw
import random, json, copy, math

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

    cfg['trialidx'] = 0

    while cfg['trialidx'] < len(cfg['triallist']):

        print('trial: ',cfg['trialidx'],' / ', len(cfg['triallist']))

        print(cfg['triallist'][cfg['trialidx']])

        cfg = runTrial(cfg)

        # this has to be at the very end!
        cfg['trialidx'] +=1

        # well... before this:

        # SAVE TRIAL DATA!
        # &
        # STORE JSON!


# cfg = getTrialSequence( {'jsonfile' : 'diagnostic triplets.json',
#                          'participant' : 'marius' } ) # participant ID seeds RNG
