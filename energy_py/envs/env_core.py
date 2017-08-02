import collections
import os

import numpy as np
import pandas as pd


class Base_Env(object):
    """
    the energy_py base environment class
    inspired by the gym.Env class

    The methods of this class are:
        step
        reset

    To implement an environment:
    1 - override the following methods in your child:
        _step
        _reset

    2 - set the following attributes
        action_space
        observation_space
        reward_range (defaults to -inf, +inf)
    """

    def __init__(self):
        self.info    = collections.defaultdict(list)
        self.outputs = collections.defaultdict(list)
        self.done    = False
        return None

    # Override in ALL subclasses
    def _step(self, action): raise NotImplementedError
    def _reset(self): raise NotImplementedError

    # Set these in ALL subclasses
    action_space = None
    observation_space = None
    reward_range = (-np.inf, np.inf)

    def load_state(self, csv_path, lag):
        """
        loads state infomation from a csv
        """
        #  loading time series data
        ts = pd.read_csv(csv_path,
                         index_col=0,
                         parse_dates=True)

        #  now dealing with the lag
        #  if no lag then state = observation
        if lag == 0:
            observation_ts = ts.iloc[:, :]
            state_ts = ts.iloc[:, :]

        #  a negative lag means the agent can only see the past
        elif lag < 0:
            #  we shift & cut the observation
            observation_ts = ts.shift(lag).iloc[:-lag, :]
            #  we cut the state
            state_ts = ts.iloc[:-lag, :]

        #  a positive lag means the agent can see the future
        elif lag > 0:
            #  we shift & cut the observation
            observation_ts = ts.shift(lag).iloc[lag:, :]
            #  we cut the state
            state_ts = ts.iloc[lag:, :]
        observation_ts = observation_ts.iloc[:, :]
        state_ts = state_ts.iloc[:, :]
        #  checking our two ts are the same shape
        assert observation_ts.shape == state_ts.shape

        return observation_ts, state_ts

    def step(self, action):
        """
        Run one timestep of the environment's dynamics.
        When end of episode is reached, you are responsible for calling reset().

        Accepts an action and returns a tuple (observation, reward, done, info).

        The step function should progress in the following order:
        - action = a[1]
        - reward = r[1]
        - next_state = next_state[1]
        - update_info()
        - step += 1
        - self.state = next_state[1]

        step() returns the observation - not the state!
        This is to allow the state to remain hidden (if desired by the modeller).

        Args:
            action (object): an action provided by the environment

        Returns:
            observation (np array): agent's observation of the current environment
            reward (np float) : amount of reward returned after previous action
            done (boolean): whether the episode has ended, in which case further step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
        """
        return self._step(action)

    def reset(self):
        """
        Resets the state of the environment and returns an initial observation.

        Returns: observation (np array): the initial observation
        """
        print('Reset environment.')
        return self._reset()


class Space(object):
    """
    The base class for observation & action spaces

    Analagous to the 'Space' object used in gym
    """

    def sample(self):
        """
        Uniformly randomly sample a random element of this space.
        """
        return self._sample()

    def contains(self, x):
        """
        Return boolean specifying if x is a valid
        member of this space.
        """
        return self._contains(x)

    def discretize(self, step):
        """
        Method to discretize the action space.
        """
        return self._discretize(step)

class Discrete_Space(Space):
    """
    A single dimension discrete space.

    Args:
        low  (float) : an array with the minimum bound for each
        high (float) : an array with the maximum bound for each
        step (float) : an array with step size
    """

    def __init__(self, low, high, step):
        self.low  = low
        self.high = high
        self.step = step
        self.discrete_space = self.discretize(self.step)

    def _sample(self):
        return np.random.choice(self.discrete_space)

    def _contains(self, x):
        return np.in1d(x, self.discrete_space)

    def _discretize(self, step):
        return np.arange(self.low, self.high + self.step, self.step).reshape(-1)

class Continuous_Space(Space):
    """
    A single dimension continuous space.

    Args:
        low  (float) : an array with the minimum bound for each
        high (float) : an array with the maximum bound for each
    """

    def __init__(self, low, high, step):
        self.low  = low
        self.high = high
        self.step = step
        self.discrete_space = self.discretize(self.step)

    def _sample(self):
        return np.random.uniform(low=self.low, high=self.high)

    def _contains(self, x):
        return (x >= self.low) and (x <= self.high)

    def _discretize(self, step):
        self.step = step
        return np.arange(self.low, self.high + step, step).reshape(-1)
