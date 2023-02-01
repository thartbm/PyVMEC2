


def runExperiment(jsonfile, partcipant):

    cfg = {}

    cfg['participant'] = participant
    cfg['jsonfile'] = jsonfile

    cfg = loadJSON(cfg)

    cfg = getTrialSequence(cfg)

    cfg = setupHardware(cfg)

    cfg = runTrialSequence(cfg)




def loadJSON(cfg):

    with open(cfg['jsonfile']) as fp:
        cfg.update(json.load(fp))

    return(cfg)
