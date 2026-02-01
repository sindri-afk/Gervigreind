import math
import random
import time

from environment import *
from search import *

#############

"""Agent acting in some environment"""
class Agent(object):

  def __init__(self):
    return

  # this method is called on the start of the new environment
  # override it to initialise the agent
  def start(self, percepts):
    print("start called")
    return

  # this method is called on each time step of the environment
  # it needs to return the action the agent wants to execute as as string
  def next_action(self, percepts):
    print("next_action called")
    return "NOOP"

  # this method is called when the environment has reached a terminal state
  # override it to reset the agent
  def cleanup(self, percepts):
    print("cleanup called")
    return

#############

"""A random Agent for the VacuumCleaner world

 RandomAgent sends actions uniformly at random. In particular, it does not check
 whether an action is actually useful or legal in the current state.
 """
class RandomAgent(Agent):

  def next_action(self, percepts):
    print("perceiving: " + str(percepts))
    actions = ["TURN_ON", "TURN_OFF", "TURN_RIGHT", "TURN_LEFT", "GO", "SUCK"]
    action = random.choice(actions)
    print("selected action: " + action)
    return action

#############

class VacuumCleanerAgent(Agent):

  search_algorithm = None
  plan = []

  def __init__(self, search_algorithm):
    self.search_algorithm = search_algorithm

  def start(self, percepts):
    self.env = Environment(percepts)
    start_time = time.process_time()

    # do the planning and remember the plan
    self.search_algorithm.do_search(self.env)
    self.plan = self.search_algorithm.get_plan()

    end_time = time.process_time()

    print("planning took %.2fs" % (end_time-start_time))
    print("number of node expansions: %d" % self.search_algorithm.get_nb_node_expansions())
    print("node expansions per second: %.1f" % (self.search_algorithm.get_nb_node_expansions()/(end_time-start_time)))
    print("maximal frontier size: %d nodes" % self.search_algorithm.get_max_frontier_size())

    if not self.plan:
      raise Exception("no plan found")
    
    print("plan length: %d" % len(self.plan))
    print("effective branching factor: %.2f" % (math.log(self.search_algorithm.get_nb_node_expansions()) / math.log(len(self.plan))))
    print("plan cost: %d" % self.search_algorithm.get_plan_cost())
    return

  def next_action(self, percepts):
    # execute actions from the plan one after the other
    a = self.plan.pop(0)
    print("executing " + a)
    return a

