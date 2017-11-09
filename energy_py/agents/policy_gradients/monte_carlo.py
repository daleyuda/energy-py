import numpy as np
import tensorflow as tf

from energy_py.agents import Base_Agent


class MC_Reinforce(Base_Agent):
    """
    Monte Carlo implementation of REINFORCE

    args
        env             : energy_py environment
        discount        : float
        policy          : energy_py policy approximator
        baseline        : usually an energy_py value function
        learning rate   : float
        verbose         : boolean

    REINFORCE is high variance - due to the nature of Monte Carlo sampling.

    REINFORCE is a low bias algorithm - no bootstrapping.

    This algorithm requires lots of episodes to run:
    - policy gradient only makes small updates
    - Monte Carlo is high variance (takes a while for expectation to converge)
    - we only update once per episode
    - only learn from samples once

    Reference = Williams (1992)
    """
    def __init__(self, **kwargs):
        #  passing the environment to the Base_Agent class
        super().__init__(**kwargs)
        self.lr = kwargs.pop('lr')
        #  pull out the policy object
        policy = kwargs.pop('policy')
        self.policy = policy(action_space=self.action_space,
                             observation_space=self.observation_space,
                             lr=self.lr)


    def _act(self, **kwargs):
        """
        Act according to the policy network

        args
            observation : np array (1, observation_dim)
            session     : a TensorFlow Session object

        return
            action      : np array (1, num_actions)
        """
        observation = kwargs.pop('observation')
        session = kwargs.pop('session')

        #  scaling the observation for use in the policy network
        scaled_observation = self.memory.scale_array(observation, self.observation_space)

        scaled_observation = scaled_observation.reshape(-1, self.observation_dim)
        assert scaled_observation.shape[0] == 1

        #  generating an action from the policy network
        action, output = self.policy.get_action(session, scaled_observation)

        #print('observation {}'.format(observation))
        #print('scaled observation {}'.format(scaled_observation))
        #print('action {}'.format(action))

        #self.memory.agent_stats['means'].extend(output['means'])
        #self.verbose_print('means are {}'.format(output['means']), level=1)
        #self.verbose_print('stdevs are {}'.format(output['stdevs']), level=1)

        return action.reshape(-1, self.num_actions)

    def _learn(self, **kwargs):
        """
        Update the policy network using the episode experience

        args
            observations        : np array (episode_length, observation_dim)
            actions             : np array (episode_length, num_actions)
            discounted_returns  : np array (episode_length, 1)
            session             : a TensorFlow Session object

        return
            loss                : np float
        """
        observations = kwargs.pop('observations')
        actions = kwargs.pop('actions')
        discounted_returns = kwargs.pop('discounted_returns')
        session = kwargs.pop('session')

        self.verbose_print('observations {}'.format(observations))
        self.verbose_print('actions {}'.format(actions))
        self.verbose_print('discounted_returns {}'.format(discounted_returns))

        loss = self.policy.improve(session,
                                   observations,
                                   actions,
                                   discounted_returns)

        self.memory.agent_stats['losses'].append(loss)
        self.verbose_print('loss is {:.8f}'.format(loss))

        return loss
