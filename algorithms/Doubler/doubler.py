import numpy as np
from arms.bernoulli import *
from algorithms.ucb.ucb1 import *
import random


def time_interval(p):
    """ time_interval() - This function returns the time interval T_p. """
    return [value for value in range(int(2**(p-1)), int(2**p))]


def observe_b_t(left_reward, right_reward):
    """ observe_b_t() - This function returns b_t."""

    random_variable = random.random()

    if random_variable >= (left_reward - right_reward + 1.0)/2:
        return 1
    else:
        return 0


def calculate_f_p(f_p, t_interval, b, p):
    """ calculate_f_p() - This function returns the f_p factor according to b in the t_interval. """

    # The relevant b values of the t_interval
    b_p = [b[value] for value in t_interval]

    # The factor that will be added to last epoch f_p
    factor = float(sum(b_p))/((2**(p-1))+.0)

    return f_p + factor - 0.5


def choose_from_probability_vector(probability_vector):
    """ choose_from_probability_vector() - This function receives a probability vector and returns the chosen index."""
    r = random.random()
    index = 0

    while r >= 0 and index < len(probability_vector):

        r -= probability_vector[index]

        index += 1

    return index - 1


def construct_probability_vector(histogram):
    """ construct_probability_vector() - This function returns the normalized histogram."""

    return np.divide(histogram, sum(histogram)+.0)


def run_doubler_algorithm(means, log_horizon, improved):
    """ run_doubler_algorithm() - This function runs the doubler / improved doubler algorithm and returns the
        cumulative regret. """

    # The L set (initialized to [1,0,0,...,0])
    my_left_set = [False]*len(means)
    my_left_set[0] = 1

    # The number of arms
    n_arms = len(means)

    # Shuffling the means vector.
    random.shuffle(means)

    # Assigning Bernoulli arms
    arms = map(lambda (mu): BernoulliArm(mu), means)

    # Assigning the black-boxes with the UCB 1 algorithm
    left_black_box = UCB1([], [])
    right_black_box = UCB1([], [])

    # Initializing the black-boxes.
    left_black_box.initialize(n_arms)
    right_black_box.initialize(n_arms)

    # The b observation
    observed_b = [0]*(2**log_horizon)

    # Regret and reward tracking
    average_reward = [0]*(2**log_horizon)
    regret = [0]*(2**log_horizon)
    cumulative_average_reward = [0]*(2**log_horizon)
    cumulative_regret = [0]*(2**log_horizon)

    # The f factor
    f = [0]*(log_horizon+2)

    # The Doubler algorithm :
    for current_p in range(0, log_horizon+1):

        # The arms used in this current round
        arms_histogram = [0]*n_arms

        # This round time interval.
        current_time_interval = time_interval(current_p)

        # The Improved Doubler algorithm.
        if improved:

            for t in current_time_interval:

                # Choosing the left arm from the multi-set L.
                left_arm = choose_from_probability_vector(construct_probability_vector(my_left_set))

                # Choosing an arm using the right black box.
                right_arm = right_black_box.select_arm()

                # Updating the histogram for the next time interval
                arms_histogram[right_arm] += 1

                # Choosing the arms
                current_left_reward = arms[left_arm].draw()

                current_right_reward = arms[right_arm].draw()

                # Observing b_t
                observed_b[t] = observe_b_t(current_left_reward, current_right_reward)

                # Updating the right black-box with b_t and f_p
                right_black_box.update(right_arm, observed_b[t] + f[current_p])

                # Assigning the average reward.
                average_reward[t] = float(current_left_reward + current_right_reward) / 2

                # Assigning the regret
                regret[t] = max(means) - average_reward[t]

                # Assigning the cumulative regret and rewards
                if t == 1:
                    cumulative_average_reward[t] = average_reward[t]

                    cumulative_regret[t] = regret[t]
                else:
                    cumulative_average_reward[t] = average_reward[t] + cumulative_average_reward[t-1]

                    cumulative_regret[t] = regret[t] + cumulative_regret[t-1]

        # The standard Doubler algorithm
        else:

            # Initializing the right black-box (S).
            right_black_box.initialize(n_arms)

            for t in current_time_interval:

                # Choosing the left arm from the multi-set L.
                left_arm = choose_from_probability_vector(construct_probability_vector(my_left_set))

                # Choosing an arm using the right black box.
                right_arm = right_black_box.select_arm()

                # Updating the histogram for the next time interval
                arms_histogram[right_arm] += 1

                # Choosing the arms
                current_left_reward = arms[left_arm].draw()

                current_right_reward = arms[right_arm].draw()

                # Observing b_t
                observed_b[t] = observe_b_t(current_left_reward, current_right_reward)

                # Updating the right black-box with b_t and f_p
                right_black_box.update(right_arm, observed_b[t])

                # Assigning the average reward.
                average_reward[t] = float(current_left_reward + current_right_reward) / 2

                # Assigning the regret
                regret[t] = max(means) - average_reward[t]

                # Assigning the cumulative regret and rewards
                if t == 1:
                    cumulative_average_reward[t] = average_reward[t]

                    cumulative_regret[t] = regret[t]
                else:
                    cumulative_average_reward[t] = average_reward[t] + cumulative_average_reward[t-1]

                    cumulative_regret[t] = regret[t] + cumulative_regret[t-1]

        # Calculating the f_p
        f[current_p+1] = calculate_f_p(f[current_p], current_time_interval, observed_b, current_p)

        # Updating the left set of arms that can be used in the next round.
        my_left_set = arms_histogram

    return cumulative_regret


def run_several_iterations(iterations, means, horizon, improved):
    """ run_several_iterations() - This function runs several iterations of the Doubler/Improved Doubler algorithm. """

    # Initializing the  results vector
    results = [0]*horizon

    # log(horizon)
    log_horizon = int(np.log2(horizon))

    for iteration in range(iterations):

        # The current cumulative regret.
        results = np.add(results, run_doubler_algorithm(means, log_horizon=log_horizon, improved=improved))

    # Returning the average cumulative regret.
    return results/(iterations + .0)