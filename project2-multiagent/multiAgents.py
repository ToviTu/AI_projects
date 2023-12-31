# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from contextlib import nullcontext
from unittest import result
from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        from util import PriorityQueueWithFunction, manhattanDistance
        import math
        dist2self = lambda x: manhattanDistance(x, newPos)
        squash = lambda x: 1 / (1 + math.e**(-0.1 * x))

        food_pq = PriorityQueueWithFunction(dist2self)
        for food in newFood.asList():
            food_pq.push(food)

        numFoodLeft = len(newFood.asList())
        nearestFoodDist = dist2self(food_pq.pop()) if numFoodLeft > 0 else 1e-10

        result = (
            successorGameState.getScore() 
            + 3*squash(dist2self(newGhostStates[0].getPosition())) 
            + math.e**(-nearestFoodDist) 
            + 1/squash(numFoodLeft)
        ) if newScaredTimes[0] == 0 else (
            successorGameState.getScore() 
            + 10 * math.e**(-nearestFoodDist) 
            + 1/squash(numFoodLeft)
            + 100
        )
        return result

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agent_index):
        Returns a list of legal actions for an agent
        agent_index=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agent_index, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        self.num_agents = gameState.getNumAgents()
        val, act = self.max_value(0, 0, gameState)
        return act
    
    def max_value(self, agent_index, this_depth, gameState):
        if this_depth == self.depth or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState), Directions.STOP
        best_value = -1e10
        best_action = None

        agent_index = 0
        for action in gameState.getLegalActions(agent_index):
            successorGameState = gameState.generateSuccessor(agent_index, action)

            nextagent_index = 0 if agent_index == self.num_agents - 1 else agent_index + 1
            nextDepth = this_depth + 1 if agent_index == self.num_agents - 1 else this_depth
            val, act = self.min_value(nextagent_index, nextDepth, successorGameState) if nextagent_index != 0 else self.max_value(nextagent_index, nextDepth, successorGameState)
            if val > best_value:
                best_action = action
                best_value = val
        return best_value, best_action
    
    def min_value(self, agent_index, this_depth, gameState):
        if self.depth == (this_depth-1) / self.num_agents or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState), Directions.STOP
        best_value = 1e10
        best_action = None

        for action in gameState.getLegalActions(agent_index):
            successorGameState = gameState.generateSuccessor(agent_index, action)

            nextagent_index = 0 if agent_index == self.num_agents - 1 else agent_index + 1
            nextDepth = this_depth + 1 if agent_index == self.num_agents - 1 else this_depth
            val, act = self.min_value(nextagent_index, nextDepth, successorGameState) if nextagent_index != 0 else self.max_value(nextagent_index, nextDepth, successorGameState)
            if val < best_value:
                best_action = action
                best_value = val
        return best_value, best_action


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        self.num_agents = gameState.getNumAgents()
        val, act = self.max_value(0, 0, gameState, float('-inf'), float('inf'))
        return act
    
    def max_value(self, agent_index, this_depth, gameState, alpha, beta):
        if this_depth == self.depth or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState), Directions.STOP
        best_value = -1e10
        best_action = None

        agent_index = 0
        for action in gameState.getLegalActions(agent_index):
            successorGameState = gameState.generateSuccessor(agent_index, action)

            nextagent_index = 0 if agent_index == self.num_agents - 1 else agent_index + 1
            nextDepth = this_depth + 1 if agent_index == self.num_agents - 1 else this_depth
            val, act = self.min_value(nextagent_index, nextDepth, successorGameState, alpha, beta) if nextagent_index != 0 else self.max_value(nextagent_index, nextDepth, successorGameState, alpha, beta)
            
            if val >  beta:
                return val, act
            
            if val > alpha:
                alpha = val
            
            if val > best_value:
                best_action = action
                best_value = val
        return best_value, best_action
    
    def min_value(self, agent_index, this_depth, gameState, alpha, beta):
        if self.depth == (this_depth-1) / self.num_agents or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState), Directions.STOP
        best_value = 1e10
        best_action = None

        for action in gameState.getLegalActions(agent_index):
            successorGameState = gameState.generateSuccessor(agent_index, action)

            nextagent_index = 0 if agent_index == self.num_agents - 1 else agent_index + 1
            nextDepth = this_depth + 1 if agent_index == self.num_agents - 1 else this_depth
            val, act = self.min_value(nextagent_index, nextDepth, successorGameState, alpha, beta) if nextagent_index != 0 else self.max_value(nextagent_index, nextDepth, successorGameState, alpha, beta)
            
            if val < alpha:
                return val, act

            if val < beta:
                beta = val
            
            if val < best_value:
                best_action = action
                best_value = val
        return best_value, best_action

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        self.num_agents = gameState.getNumAgents()
        val, act = self.max_value(0, 0, gameState)
        return act
    
    def max_value(self, agent_index, this_depth, gameState):
        if this_depth == self.depth or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState), Directions.STOP
        best_value = -1e10
        best_action = None

        agent_index = 0
        for action in gameState.getLegalActions(agent_index):
            successorGameState = gameState.generateSuccessor(agent_index, action)

            nextagent_index = 0 if agent_index == self.num_agents - 1 else agent_index + 1
            nextDepth = this_depth + 1 if agent_index == self.num_agents - 1 else this_depth
            val, act = self.min_value(nextagent_index, nextDepth, successorGameState) if nextagent_index != 0 else self.max_value(nextagent_index, nextDepth, successorGameState)
            if val > best_value:
                best_action = action
                best_value = val
        return best_value, best_action
    
    def min_value(self, agent_index, this_depth, gameState):
        if self.depth == (this_depth-1) / self.num_agents or gameState.isWin() or gameState.isLose():
            return self.evaluationFunction(gameState), Directions.STOP
        actions = gameState.getLegalActions(agent_index)
        exp_value = 0
        prob = 1 / len(actions)
        for action in actions:
            successorGameState = gameState.generateSuccessor(agent_index, action)
            nextagent_index = 0 if agent_index == self.num_agents - 1 else agent_index + 1
            nextDepth = this_depth + 1 if agent_index == self.num_agents - 1 else this_depth
            val, act = self.min_value(nextagent_index, nextDepth, successorGameState) if nextagent_index != 0 else self.max_value(nextagent_index, nextDepth, successorGameState)
            exp_value += prob * val
        return exp_value, None


def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    Pos = currentGameState.getPacmanPosition()
    Food = currentGameState.getFood()
    GhostStates = currentGameState.getGhostStates()
    ScaredTimes = [ghostState.scaredTimer for ghostState in GhostStates]
    from util import PriorityQueueWithFunction, manhattanDistance
    import math
    dist2self = lambda x: manhattanDistance(x, Pos)
    squash = lambda x: 1 / (1 + math.e**(-0.1 * x))

    food_pq = PriorityQueueWithFunction(dist2self)
    for food in Food.asList():
        food_pq.push(food)

    numFoodLeft = len(Food.asList())
    nearestFoodDist = dist2self(food_pq.pop()) if numFoodLeft > 0 else 1e-10

    result = (
        currentGameState.getScore() 
        + 3*squash(dist2self(GhostStates[0].getPosition())) 
        + math.e**(-nearestFoodDist) 
        + 1/squash(numFoodLeft)
    ) if ScaredTimes[0] == 0 else (
        currentGameState.getScore() 
        + 10 * math.e**(-nearestFoodDist) 
        + 1/squash(numFoodLeft)
        + 100
    )
    return result
# Abbreviation
better = betterEvaluationFunction
