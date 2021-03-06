from collections import defaultdict
import logging

import tensorflow as tf

import energypy

logger = logging.getLogger(__name__)


class BaseAgent(object):
    """ The energypy base agent class """

    def __init__(
            self,
            env,
            sess=None,
            total_steps=0,

            memory_type='deque',
            memory_length=10000,
            load_memory_path=None,

            min_reward=-10,
            max_reward=10,
            act_path='./act_path',
            learn_path='./learn_path'
    ):

        self.sess = sess
        self.env = env

        self.observation_space = env.observation_space
        self.action_space = env.action_space

        self.memory = energypy.make_memory(
            memory_id=memory_type,
            env=env,
            size=memory_length,
            load_path=load_memory_path
        )

        #  reward clipping
        self.min_reward = min_reward
        self.max_reward = max_reward

        self.act_step = 0
        self.learn_step = 0

        #  TODO replace the lists with defaultdict(list)
        # self.act_summaries = []
        # self.act_writer = tf.summary.FileWriter(act_path)

        # self.learn_summaries = []
        # self.learn_writer = tf.summary.FileWriter(learn_path)

        self.summaries = {
            'acting': [],
            'learning': []
        }
        self.writers = {
            'acting': tf.summary.FileWriter(act_path),
            'learning': tf.summary.FileWriter(learn_path)
        }

        #  TODO
        self.filters = None
        self.kernels = None
        self.strides = None

    def reset(self):
        """
        Resets the agent internals
        """
        logger.debug('Resetting the agent internals')
        self.memory.reset()
        self.act_step = 0
        self.learn_step = 0

        return self._reset()

    def act(self, observation, explore=1.0):
        """
        Action selection by agent

        args
            observation (np array) shape=(1, observation_dim)
            explore (float) 0.0 = 100% greedy, 1.0 = 100% explore

        return
            action (np array) shape=(1, num_actions)
        """
        logger.debug('Agent is acting')
        self.act_step += 1

        return self._act(
            observation.reshape(1, *self.observation_space.shape),
            explore=explore
        )

    def learn(self, **kwargs):
        """
        Agent learns from experience

        args
            batch (dict) batch of experience
            sess (tf.Session)

        return
            training_history (object) info about learning (i.e. loss)
        """
        logger.debug('Agent is learning')
        self.learn_step += 1

        return self._learn(**kwargs)

    def remember(self, observation, action, reward, next_observation, done):
        """
        Store experience in the agent's memory

        args
            observation (np.array)
            action (np.array)
            reward (np.array)
            next_observation (np.array)
            done (np.array)
        """
        logger.debug('Agent is remembering')

        if self.min_reward and self.max_reward:
            reward = max(self.min_reward, min(reward, self.max_reward))

        return self.memory.remember(
            observation, action, reward, next_observation, done
        )
