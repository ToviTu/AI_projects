"""RL Policy classes.

We have provided you with a base policy class, some example
implementations and some unimplemented classes that should be useful
in your code.
"""

import numpy as np
import attr


class Policy:
    """Base class representing an MDP policy.

    Policies are used by the agent to choose actions.

    Policies are designed to be stacked to get interesting behaviors
    of choices. For instances in a discrete action space the lowest
    level policy may take in Q-Values and select the action index
    corresponding to the largest value. If this policy is wrapped in
    an epsilon greedy policy then with some probability epsilon, a
    random action will be chosen.
    """

    def select_action(self, **kwargs):
        """Used by agents to select actions.

        Returns
        -------
        Any:
          An object representing the chosen action. Type depends on
          the hierarchy of policy instances.
        """
        raise NotImplementedError("This method should be overriden.")


class UniformRandomPolicy(Policy):
    """Chooses a discrete action with uniform random probability.

    This is provided as a reference on how to use the policy class.

    Parameters
    ----------
    num_actions: int
      Number of actions to choose from. Must be > 0.

    Raises
    ------
    ValueError:
      If num_actions <= 0
    """

    def __init__(self, num_actions):
        assert num_actions >= 1
        self.num_actions = num_actions

    def select_action(self, **kwargs):
        """Return a random action index.

        This policy cannot contain others (as they would just be ignored).

        Returns
        -------
        int:
          Action index in range [0, num_actions)
        """
        return np.random.randint(0, self.num_actions)

    def get_config(self):  # noqa: D102
        return {"num_actions": self.num_actions}


class GreedyPolicy(Policy):
    """Always returns best action according to Q-values.

    This is a pure exploitation policy.
    """

    def select_action(self, q_values, **kwargs):  # noqa: D102
        return np.argmax(q_values)


class GreedyEpsilonPolicy(Policy):
    """Selects greedy action or with some probability a random action.

    Standard greedy-epsilon implementation. With probability epsilon
    choose a random action. Otherwise choose the greedy action.

    Parameters
    ----------
    epsilon: float
     Initial probability of choosing a random action. Can be changed
     over time.
    """

    def __init__(self, epsilon):
        self.epsilon = epsilon

    def select_action(self, q_values, **kwargs):
        """Run Greedy-Epsilon for the given Q-values.

        Parameters
        ----------
        q_values: array-like
          Array-like structure of floats representing the Q-values for
          each action.

        Returns
        -------
        int:
          The action index chosen.
        """
        if np.random.random() < self.epsilon:
            return np.random.randint(0, len(q_values))
        else:
            return np.argmax(q_values)


class LinearDecayGreedyEpsilonPolicy(Policy):
    """Policy with a parameter that decays linearly.

    Like GreedyEpsilonPolicy but the epsilon decays from a start value
    to an end value over k steps.

    Parameters
    ----------
    start_value: int, float
      The initial value of the parameter
    end_value: int, float
      The value of the policy at the end of the decay.
    num_steps: int
      The number of steps over which to decay the value.

    """

    def __init__(
        self, policy, attr_name, start_value, end_value, num_steps
    ):  # noqa: D102
        self.policy = policy
        self.attr_name = attr_name
        self.start_value = start_value
        self.end_value = end_value
        self.num_steps = num_steps
        self.current_step = 0
        setattr(self.policy, self.attr_name, start_value)

    def select_action(self, q_values, is_training=True, agent_step=None, **kwargs):
        """Decay parameter and select action.

        Parameters
        ----------
        q_values: np.array
          The Q-values for each action.
        is_training: bool, optional
          If true then parameter will be decayed. Defaults to true.

        Returns
        -------
        Any:
          Selected action.
        """

        if agent_step is not None:
            self.current_step = agent_step

        if is_training and self.current_step < self.num_steps:
            new_epsilon = (
                self.start_value
                - self.current_step
                * (self.start_value - self.end_value)
                / self.num_steps
            )
            new_epsilon = max(new_epsilon, self.end_value)
            setattr(
                self.policy,
                self.attr_name,
                new_epsilon,
            )
            self.current_step += 1
        else:
            # Reduce to GreedyPolicy
            setattr(self.policy, self.attr_name, 0)
        return self.policy.select_action(self.policy, q_values, **kwargs)

    def reset(self):
        """Start the decay over at the start value."""
        self.current_step = 0
        setattr(self.policy, self.attr_name, self.start_value)
