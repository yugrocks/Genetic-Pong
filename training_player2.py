from kivy.app import App
from main_auto import PongPaddle, PongBall, PongGame
from kivy.clock import Clock
from functools import partial
from mover import model
import numpy as np
from time import sleep
import time
from random import *
import threading
import operator
from numpy import copy
import pickle

# hyperparameters
nb_hdn_neurons_layer1 = 4
nb_hdn_neurons_layer2 = 4
nb_output_neurons = 1 #one class classification
input_size = 4 #including bias
W1_shape = (4, 4)
W2_shape = (4, 5)
W3_shape = (1, 5)
initial_population_size = 20
# total parameters = 4*4 + 4*5 + 1*5 = 51


final_best_individual = None
previous_score = 0 # will be used for early stopping


def initialize_population():
    population = []
    #convention: each chromosome will have dimensions 1x33
    for i in range(initial_population_size):
        W1 = np.random.randn(W1_shape[0], W1_shape[1])
        W2 = np.random.randn(W2_shape[0], W2_shape[1])
        W3 = np.random.randn(W3_shape[0], W3_shape[1])
        population.append(np.concatenate((W1.flatten().reshape(1,W1_shape[0]*W1_shape[1] ),
                                W2.flatten().reshape(1,W2_shape[0]*W2_shape[1] ),
                          W3.flatten().reshape(1,W3_shape[0]*W3_shape[1] )),axis = 1)
                          )
    return population

def get_weights_from_encoded(individual):
    W1 = individual[:, 0:W1_shape[0]*W1_shape[1]]
    W2 = individual[:, W1_shape[0]*W1_shape[1]:W1_shape[0]*W1_shape[1]+W2_shape[0]*W2_shape[1]]
    W3 = individual[:, W1_shape[0]*W1_shape[1]+W2_shape[0]*W2_shape[1]:]
    return (W1.reshape(W1_shape[0], W1_shape[1]), W2.reshape(W2_shape[0], W2_shape[1]), W3.reshape(W3_shape[0], W3_shape[1]))

def generate_random_chromosome():
    W1 = np.random.randn(W1_shape[0], W1_shape[1])
    W2 = np.random.randn(W2_shape[0], W2_shape[1])
    W3 = np.random.randn(W3_shape[0], W3_shape[1])
    return np.concatenate((W1.flatten().reshape(1,W1_shape[0]*W1_shape[1] ),
                                W2.flatten().reshape(1,W2_shape[0]*W2_shape[1] ),
                          W3.flatten().reshape(1,W3_shape[0]*W3_shape[1] )),axis = 1)
    


def mutate(chromosome, prob):
    if random() >= prob:
        return chromosome, False # No mutation done
    else:
        #mutate each element with a probability of 'prob'
        mutated = False
        chromosome0 = copy(chromosome)
        operators = ['add', 'subtract']
        for i in range(len(chromosome0)):
            if random() < prob:
                if choice(operators) == 'add':
                    chromosome0[i] += random()
                    mutated = True
                else:
                    chromosome0[i] -= random()
                    mutated = True
        return chromosome0, mutated # mutated
    

def crossover(chromosomes, prob):
    # here the argument chromosomes is a list containing two parent chromosomes
    if random() >= prob:
        return chromosomes, False # No crossover done
    else:
        #select a random position from the index, around which the values will be swapped
        indx = randint(1, chromosomes[0].shape[1]-1)
        p0 = copy(chromosomes[0]); p1 = copy(chromosomes[1])
        med = copy(p0)
        p0[:, 0:indx] = p1[:, 0:indx]
        p1[:, 0:indx] = med[:, 0:indx]
        return [p0, p1], True
    

def crossover2(chromosomes, prob):
    # here the argument chromosomes is a list containing two parent chromosomes
    #for every index along the length of both chromosomes, randomly select if it has to be swapped
    p0 = copy(chromosomes[0]); p1 = copy(chromosomes[1])
    crossovered = False
    for i in range(chromosomes[0].shape[1]):
        if random() < prob:
            #swap the numbers at index i
            p0[0, i] = chromosomes[1][0][i]
            p1[0, i] = chromosomes[0][0][i]
            crossovered = True
    return [p0, p1], crossovered


def selectindex():
    return randint(0, 5) #including the 6th element


def tournament(population, pong): #rank function
    fitnesses = []
    for individual in population:
        #generate a model from an individual
        model1 = model(get_weights_from_encoded(individual))
        pong.game_over = False
        pong.player1.score = 0
        pong.player2.score = 0
        pong.player2.pseudo_score = 0
        pong.player1.center_y = pong.height/2
        pong.player2.center_y = pong.height/2
        t1 = time.time()
        while not pong.game_over:
            pong.update("", model1)
        t2 = time.time()
        total_time = t2 - t1
        fitnesses.append(pong.player2.pseudo_score)
    zip1 = zip(fitnesses,population)
    sorted_results = sorted(zip1, key=operator.itemgetter(0), reverse = True)
    sorted_pop = [x for _,x in sorted_results]
    sorted_fitnesses = [_ for _,x in sorted_results]
    print(sorted_fitnesses)
    return sorted_pop, sorted_fitnesses
        

def main_function(dt, pong):
    global final_best_individual, previous_score
    max_gen = 150
    crossover2_prob = 0.3
    crossover_prob = 0.7
    mutation_prob = 0.2
    population = initialize_population() # the very first population
    for i in range(max_gen):
        print("Generation ", i)
        sorted_pop, sorted_fitnesses = tournament(population, pong)
        if sorted_fitnesses[0] > previous_score:
            final_best_individual = sorted_pop[0] # save the model if score is better than previous
            previous_score = sorted_fitnesses[0] # the best score from previous generation
        print(sorted_fitnesses[0])
        #The first two always make it
        newpop = []
        newpop.append(sorted_pop[0]);newpop.append(sorted_pop[1])
        while len(newpop) < initial_population_size:
                # select any from the top 6 of the population and randomly breed and mutate them
                # First crossover:
                idx1 = selectindex();idx2 = selectindex() # two parents
                if idx1 != idx2:
                    children, crossovered = crossover([population[idx1],population[idx2]], prob = crossover_prob)
                    if crossovered and len(newpop) < initial_population_size-1:
                        newpop.extend(children)
                # Mutation:
                idx1 = selectindex()
                child, mutated = mutate(population[idx1], prob = mutation_prob)
                if mutated and len(newpop) < initial_population_size:
                    newpop.append(child)
                # Crossover 2:
                idx1 = selectindex();idx2 = selectindex()
                if idx1 != idx2:
                    children, crossovered = crossover2([population[idx1],population[idx2]], prob = crossover2_prob)
                    if crossovered and len(newpop) < initial_population_size-1:
                        newpop.extend(children)
                #add a random new chromosome by the probability of none of the above hapening
                prob_none =1- ((crossover_prob*(1-mutation_prob)*(1-crossover2_prob) + (1-crossover_prob)*(mutation_prob)*(1-crossover2_prob)+(1-crossover_prob)*(1-mutation_prob)*(crossover2_prob))
                           +(crossover_prob*mutation_prob*(1-crossover2_prob) + (1-crossover_prob)*mutation_prob*crossover2_prob + crossover_prob*(1-mutation_prob)*crossover2_prob)
                           +crossover_prob*mutation_prob*crossover2_prob )
                if random() < prob_none and len(newpop) < initial_population_size:
                    newpop.append(generate_random_chromosome())
        population = list(np.copy(newpop))
    sorted_pop, sorted_losses = tournament(population, pong)
    if sorted_fitnesses[0] > previous_score:
        final_best_individual = sorted_pop[0]
    return sorted_losses[0], sorted_pop[0]
        
def pickle_weights(weights):
    W1, W2, W3 = get_weights_from_encoded(weights)
    weights0 = {'W1':copy(W1), "W2":copy(W2), "W3":copy(W3)}
    with open("weights2.pkl", 'wb') as file:
        pickle.dump(weights0, file)


def load_pickled_weights():
    with open("weights2.pkl", 'rb') as file:
        weights = pickle.load(file)
    return weights["W1"], weights['W2'], weights["W3"]


class PongApp(App):
    event = None
    def build(self):
        game = PongGame()
        game.serve_ball()
        threading.Thread(target = partial(main_function, "", game)).start()
        #self.event = Clock.schedule_interval(partial(main_function, pong = game), 1.0 / 60.0)
        return game


training_phase = False
if __name__ == "__main__" and training_phase:
  app = PongApp()
  app.run()

  pickle_weights(final_best_individual) #save the best evolved weights


W1, W2, W3 = load_pickled_weights()
trained_individual = np.concatenate((W1.flatten().reshape(1,W1_shape[0]*W1_shape[1] ),
                                W2.flatten().reshape(1,W2_shape[0]*W2_shape[1] ),
                          W3.flatten().reshape(1,W3_shape[0]*W3_shape[1] )),axis = 1)

class PongApp(App):
    event = None
    def build(self):
        game = PongGame()
        game.serve_ball()
        
        #target = partial(game.update,model = model(get_weights_from_encoded(final_best_individual)))).start()
        self.event = Clock.schedule_interval(partial(game.update, model = model(get_weights_from_encoded(trained_individual))), 1.0 / 60.0)
        return game

app = PongApp()
app.run()

