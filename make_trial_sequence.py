import random, json, copy, math

def getTrialSequence(jsonfile, participant):

    with open(jsonfile) as fp:
        cfg = json.load(fp)

    cfg['triallist'] = []

    # simple start:
    cfg['basictrial'] = {'target'   : 0,
                         'rotation' : 0,
                         'cursor'   : 'normal',
                         'task'     : '' }

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

    tasktrial = copy.deepcopy(cfg['basictrial'])
    for k in tasktrial.keys():
        if k in el:
            tasktrial[k] = el[k]


    targets = copy.deepcopy(el['targets'])

    # set up a sequence of rotations:
    trial_rotations = [el['rotation']] * el['trials']

    # deal with task
    blocks = int(math.ceil(el['trials'] / len(el['targets'])))

    current_trial = 0

    # psedurandomize in blocks:
    for block in range(blocks):

        target_order = list(range(len(targets)))
        random.shuffle(target_order)

        # other stuff, apart from targets?

        for target_no in range(len(targets)):

            if (current_trial == el['trials']):
                pass # for tasks with fractioned blocks

            # else: get a trial to add to the list:
            thistrial = copy.deepcopy(tasktrial)



            thistrial['target'] = targets[target_order[target_no]]

            # rotation? other stuff?
            thistrial['rotation'] = trial_rotations[current_trial]


            cfg['triallist'] += [thistrial]

            current_trial += 1

    return(cfg)

def addSuperTaskTrials(cfg, el):

    nsubtasks = len(el['subtasks'])
    nproperties = len(el['properties'])
    nrepeats = el['repeats']

    # prepare the subtask properties:
    # subtasks X properties

    pro_dic = {}
    for k in el['properties'].keys():
        pro_dic[k] = []

    subtask_properties = {}
    for k in range(len(el['subtasks'])):
        subtask_properties[el['subtasks'][k]['name']] = copy.deepcopy(pro_dic)

    print(subtask_properties)

    # add trials to trial list:
    for repeat in range(el['repeats']):

        taskorder = range(len(el['subtasks']))
        if el['taskorder'] == 'pseudorandom':
            random.shuffle(taskorder)

        for task_idx in range(len(el['subtasks'])):
            task_name = el['subtasks'][task_idx]['name']

            for property in el['properties'].keys():
                print(task_name, property)
                subtask_properties[task_name][property] += [1]

        pass


    print(subtask_properties)

    return(cfg)



cfg = getTrialSequence( jsonfile = 'diagnostic triplets.json',
                        participant = 'marius' ) # participant ID seeds RNG
