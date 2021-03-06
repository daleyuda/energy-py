import argparse
import os
from shutil import copyfile


from energypy.common import ensure_dir


def make_config_parser():
    """
    Parses arguments from the command line for running config experiments

    returns
        args (argparse NameSpace)
    """
    parser = argparse.ArgumentParser(
        description='energypy config expt argparser'
    )

    #  required
    parser.add_argument('expt_name', default=None, type=str)
    parser.add_argument('run_name', default=None, type=str)

    args = parser.parse_args()

    return args


def make_paths(
        experiments_dir,
        expt_name,
        run_name,
        load_configs=True
):
    """
    Creates a dictionary of paths for use with experiments

    args
        experiments_dir (str) usually energypy/energypy/experiments
        expt_name (str)
        run_name (str)

    returns
        paths (dict) {name: path}

    Folder structure
        experiments/configs/expt_name/expt.ini
                                      runs.ini

        experiments/results/expt_name/run_name/tensorboard/run_name/rl
                                                                   /act
                                                                   /learn
                                               env_histories/ep_1/info.csv
                                                             ep_2/info.csv
                                                             e..
                                               expt.ini
                                               runs.ini
                                               agent_args.txt
                                               env_args.txt
                                               info.log
                                               debug.log
    """
    #  rename the join function to make code below eaiser to read
    join = os.path.join

    results_dir = join(experiments_dir, 'results', expt_name)

    if load_configs:
        config_dir = join(experiments_dir, 'configs', expt_name)

        config_paths = {
            'expt_config': join(config_dir, 'expt.ini'),
            'run_configs': join(config_dir, 'runs.ini')
        }

        ensure_dir(join(results_dir, run_name))

        #  copy config files into results directory
        copyfile(
            config_paths['expt_config'], join(results_dir, 'expt.ini')
        )

        copyfile(
            config_paths['run_configs'], join(results_dir, 'runs.ini')
        )
    else:
        config_paths = {}

    results_paths = {

        #  tensorboard runs are all in the tensoboard folder
        #  this is for easy comparision of runs
        'tb_rl': join(results_dir, 'tensorboard', run_name, 'rl'),
        'tb_act': join(results_dir, 'tensorboard', run_name, 'act'),
        'tb_learn': join(results_dir, 'tensorboard', run_name,  'learn'),

        #  run specific
        'env_histories': join(results_dir, run_name, 'env_histories'),
        'debug_log': join(results_dir, run_name, 'debug.log'),
        'info_log': join(results_dir, run_name, 'info.log'),
        'env_args': join(results_dir, run_name, 'env_args.txt'),
        'agent_args': join(results_dir, run_name, 'agent_args.txt'),
        'ep_rewards': join(results_dir, run_name, 'episode_rewards.csv'),
        'memory': join(results_dir, '{}_memory.pkl'.format(run_name))
    }

    paths = {**config_paths, **results_paths}

    #  check that all our paths exist
    for key, path in paths.items():
        ensure_dir(path)


    return paths
