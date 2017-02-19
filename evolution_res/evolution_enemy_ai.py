# @Author: Varoon Pazhyanur <varoon>
# @Date:   18-02-2017
# @Filename: evolution_enemy_ai.py
# @Last modified by:   varoon
# @Last modified time: 19-02-2017

from random import Random
from time import time
from time import sleep
import inspyred
import itertools

##Goal: create enemy attributes that adapy

#generator function. enemy attribues that add up to 100. Only for Generation 0.
def generate_enemy(random,args):
    SUM_OF_TRAITS = 100
    enemy_feature_vector = []
    for i in range(1,6):
        enemy_feature_vector.append(random.uniform(1,20))
    speed = SUM_OF_TRAITS - sum(enemy_feature_vector)
    enemy_feature_vector.append(speed)
    enemy_feature_vector = bound_enemy(enemy_feature_vector, [])
    print(enemy_feature_vector)
    print(sum(enemy_feature_vector))
    return enemy_feature_vector


#gives segments, calculates area of polygon
def survival(enemy):
    ## TODO: FIX THIS TO BE OBJECTIVE FUNCTION
    #conn.send(enemy)
    #x = conn.recv()

    return max(enemy)

#evaluator function. returns list of survival scores of entire generation.
def evaluate_enemy(candidates, args):

    fitness=[]
    #print("eval")
    for cs in candidates:
        fit = survival(cs)
        fitness.append(fit)
    return fitness
def bound_enemy(mylist ,args):
    l = len(mylist)
    total = 0.0
    maxE = 100.0

    # 	Loop through the list and make sure that all values are between 0 and 100 inclusive
    for i in range(0,l):
        mylist[i] = max(min(mylist[i], 100.0), 0.0)
        total += mylist[i]

    # 	Scale all list element values to sum to a total of 100
    if (total != 0):
         for i in range(0,l):
            mylist[i] = mylist[i] / total * maxE

    # 	Edge Case: Equally distribute across all list elements
    else:
         for i in range(0, l):
              mylist[i] = (maxE / l)
    print(sum(mylist))
    return mylist


#ACTUAL EVOLUTION

#NOTE: Laplace crossover is used because of its success in the April 2014 Journal of Theoretical and Applied Information Technology Lim Suleiman, et. al
#NOTE: Gaussian mutation is used for its simplicity.
#ACTUAL SCRIPT:
rand = Random()
rand.seed(int(time()))
my_ec = inspyred.ec.EvolutionaryComputation(rand)
my_ec.selector = inspyred.ec.selectors.tournament_selection
my_ec.variator = [inspyred.ec.variators.laplace_crossover,inspyred.ec.variators.gaussian_mutation]
my_ec.replacer = inspyred.ec.replacers.steady_state_replacement
my_ec.terminator = [inspyred.ec.terminators.generation_termination]

final_pop = my_ec.evolve(generator=generate_enemy,
                         evaluator=evaluate_enemy,
                         pop_size=30,
                         bounder=bound_enemy,
                         max_evaluations=500,
                         num_selected=2,
                         mutation_rate=0.25,
                         max_generations=10,
                         lx_scale=10,    #analog of \sigma for the laplace distrubtion . used for laplace crossover)
                         gaussian_stdev=9)   #used for gaussian mutator, mu=0)

# Sort and print the best individual, who will be at index 0.
final_pop.sort(reverse=True)
print('Terminated due to {0}.'.format(my_ec.termination_cause))
print(final_pop[0])
print(my_ec.num_generations)
