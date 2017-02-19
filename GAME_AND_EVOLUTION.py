# @Author: Varoon Pazhyanur <varoon>
# @Date:   18-02-2017
# @Filename: GAME_AND_EVOLUTION.py
# @Last modified by:   varoon
# @Last modified time: 19-02-2017

from random import Random
import inspyred
import itertools
import pygame
from pygame.locals import *
from sys import exit
from sprites import *
import random as rand
from values import *
from levels import *
from splash_screens import *
import math
from assets import *
from game_init import *
from game_ui import *
from multiprocessing import Process, Pipe
import time

#-----------------------------------------
#EVOLUTIONARY LEARNING SECTION
gen = -1
def evolution(conn):
    gen = -1
    def generate_enemy(random,args):
        SUM_OF_TRAITS = 100
        enemy_feature_vector = []
        for i in range(1,7):
            enemy_feature_vector.append(random.randint(1,30))
        speed = SUM_OF_TRAITS - sum(enemy_feature_vector)
        enemy_feature_vector.append(speed)
        enemy_feature_vector = bound_enemy(enemy_feature_vector, [])
       # print(enemy_feature_vector)
       # print(sum(enemy_feature_vector))
        return enemy_feature_vector


    #gives segments, calculates area of polygon
    def survival(enemy):
        ## TODO: FIX THIS TO BE OBJECTIVE FUNCTION
        print("SENDING")
        conn.send(enemy)
        print("SENT")
        x = conn.recv()

        return x

    #evaluator function. returns list of survival scores of entire generation.
    def evaluate_enemy(candidates, args):
        global gen
        gen = gen+1
        
        fitness=[]
        #print("eval")
        print(len(candidates))
        for i in range(0,len(candidates)):
            print("GENERATION; {} ; SPECIES: {}".format(gen,i))
            fit = survival(candidates[i])
            fitness.append(fit)
        return fitness
    def bound_enemy(mylist ,args):
        l = len(mylist)
        total = 0
        maxE = 100

        # 	Loop through the list and make sure that all values are between 0 and 100 inclusive
        for i in range(0,l):
            mylist[i] = max(min(mylist[i], 100), 0)
            total += mylist[i]

        # 	Scale all list element values to sum to a total of 100
        if (total != 0):
             for i in range(0,l):
                mylist[i] = mylist[i] / total * maxE

        # 	Edge Case: Equally distribute across all list elements
        else:
             for i in range(0, l):
                  mylist[i] = (maxE / l)
        #print(sum(mylist))
        return mylist


    #ACTUAL EVOLUTION

    #NOTE: Laplace crossover is used because of its success in the April 2014 Journal of Theoretical and Applied Information Technology Lim Suleiman, et. al
    #NOTE: Gaussian mutation is used for its simplicity.
    #ACTUAL SCRIPT:
    rand = Random()
    my_ec = inspyred.ec.EvolutionaryComputation(rand)
    my_ec.selector = inspyred.ec.selectors.fitness_proportionate_selection
    my_ec.variator = [inspyred.ec.variators.laplace_crossover,inspyred.ec.variators.gaussian_mutation]
    my_ec.replacer = inspyred.ec.replacers.truncation_replacement
    my_ec.terminator = [inspyred.ec.terminators.generation_termination]

    final_pop = my_ec.evolve(generator=generate_enemy,
                             evaluator=evaluate_enemy,
                             pop_size=8,
                             num_selected = 6,
                             bounder=bound_enemy,
                             max_evaluations=500,
                             mutation_rate=0.25,
                             max_generations=10,
                             lx_scale=10,    #analog of \sigma for the laplace distrubtion . used for laplace crossover)
                             gaussian_stdev=9)   #used for gaussian mutator, mu=0)

    # Sort and print the best individual, who will be at index 0.
    final_pop.sort(reverse=True)
    print('Terminated due to {0}.'.format(my_ec.termination_cause))
    print(final_pop[0])
    print(my_ec.num_generations)
def game(conn):

    #setup frames per second
    clock = pygame.time.Clock()
    #set initial scene to 0
    scene = 0
    #start pygame
    pygame.init()
    #set up screen display and images
    screen = pygame.display.set_mode(SCREEN_SIZE,0,32)

    #initialize the player
    player = Player(player_img_name, PLAYER_SPEED, PLAYER_HEALTH, 100, 100)
    #set paused status to false
    paused = False
    map_showing = False
    #initialize first room

    size = 25

    level_1 = Level(size)
    #add the player to the allies sprite group
    #print(level_1.current_room)
    level_1.current_room.ally_sprite_group.add(player)

    #scene_0_images = [(title_img_name,(0,0))]
    scene_0_buttons = [(start_button_img_name,(220,200)),(quit_button_img_name,(220,300))]
    title_screen = Splash_Screen((0,0),0,[scene_0_background_img_name],[],scene_0_buttons)

    pause_menu_backgrounds = [pause_menu_img_name]
    pause_menu_images = []
    pause_menu_buttons = [(continue_button_img_name,(220,193)),(quit_button_img_name,(220,266))]
    pause_menu = Splash_Screen((160,120),0,pause_menu_backgrounds,pause_menu_images,pause_menu_buttons)

    map_overlay_backgrounds = [map_overlay_img]
    map_overlay = Splash_Screen((0,0),0,map_overlay_backgrounds,[(starting_room_img,(305,225))],[])

    health_enter = PLAYER_HEALTH
    health_exit = PLAYER_HEALTH

    #SEND THIS DATA TO EVOLUTION
    health_diff = 0
    enemy_attr = [rand.randint(1,10), rand.randint(3,10), rand.randint(200, 500), rand.randint(10, 50), rand.randint(1,10), rand.randint(1000,1500), rand.randint(0, 120)]


    while True:

        #REPLACE RANDOM NUMBERS WITH DATA FROM EVOLUTION
        #print("BEFORE RECV")

        #x= conn.recv()
        #print("rCVD: {}".format(x))
        #enemy_attr = [1+int(math.floor(x[0]/10)) , int(math.ceil(x[1]/10)+3) , int(math.ceil(x[2]))*3+200 , int(math.ceil(x[3]/2)+10) , 1+int(math.ceil(x[4]/10)) , int(math.ceil(x[5]*5+1000)) , int(math.ceil(x[6]*1.2))]
        #enemy_attr = [rand.randint(1,10), rand.randint(3,10), rand.randint(200, 500), rand.randint(10, 50), rand.randint(1,10), rand.randint(1000,1500), rand.randint(0, 120)]
        #set clock to save the time between frames
        dt = clock.tick(FPS)
        speed = float(dt)/64

        #print(str(level_1.current_room.enemy_count))
        #print(str(player.health))

        #print('health enter: ' + str(health_enter))
        #print('health exit' + str(health_exit))
        #print('health diff: ' + str(health_diff))

        ##########SCENE-RENDERING#########
        #rendering for title scene

        #print("scene rendering")
        if scene == 0:
            title_screen.display(screen,dt)
            #print('scene done rendering')

        #rendering for the firsl level scene
        elif scene == 1:
            level_1.current_room.draw_all(screen,dt)

            if paused:
                pause_menu.display(screen,dt)

            elif not paused:

                #print(level_1.current_room)

                for l in level_1.current_room.lasers:
                    l.behave(speed,dt)
                    for e in level_1.current_room.enemies:
                        e.on_collision(l)

                for e in level_1.current_room.enemies:
                    #print(str(e.health))
                    e.behave(speed, dt)
                    for l in level_1.current_room.lasers:
                        player.on_collision(level_1.current_room,e, l)

                for p in level_1.current_room.portals:
                    if p.on_collision(player,screen, enemy_attr):
                        health_exit = player.health
                        health_diff = health_enter - health_exit
                        health_enter = player.health
                        print("BEFORE RECV")

                        x= conn.recv()
                        print("rCVD: {}; {}".format(x, sum(x)))
                        enemy_attr = [1+int(math.floor(x[0]/10)) , int(math.ceil(x[1]/10)+3) , int(math.ceil(x[2]))*3+200 , int(math.ceil(x[3]/2)+10) , 1+int(math.ceil(x[4]/10)) , int(math.ceil(x[5]*5+1000)) , int(math.ceil(x[6]*1.2))]
 
                    
                        conn.send(health_diff)

                        print("HEALTH DIFF SENT: {}".format(health_diff))

                player.behave(speed, dt)

            display_health(screen, player.health)

            if map_showing:
                map_overlay.display(screen,dt)

        ##########EVENT-LISTENING##########
        for event in pygame.event.get():
            #print the events
            #print(event)
            if event.type == QUIT:
                exit()

            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if scene == 0:
                        if title_screen.button_disp[0].collidepoint(pygame.mouse.get_pos()):
                            scene = 1
                            level_1.current_room.generate(screen, [0, 0, 0])

                        if title_screen.button_disp[1].collidepoint(pygame.mouse.get_pos()):
                            exit()
                    if scene == 1:
                        if paused:
                            if pause_menu.button_disp[0].collidepoint(pygame.mouse.get_pos()):
                                paused = False
                            if pause_menu.button_disp[1].collidepoint(pygame.mouse.get_pos()):
                                exit()

            if event.type == KEYDOWN:
                if not paused:
                    if event.key == K_w:
                        player.accelerate(0)
                    elif event.key == K_s:
                        player.accelerate(1)
                    elif event.key == K_a:
                        player.accelerate(2)
                    elif event.key == K_d:
                        player.accelerate(3)
                    elif event.key == K_SPACE:
                        level_1.current_room.generate_player_laser(player)

            if event.type == KEYUP:
                if event.key == K_w:
                    player.deccelerate(0)
                elif event.key == K_s:
                    player.deccelerate(1)
                elif event.key == K_a:
                    player.deccelerate(2)
                elif event.key == K_d:
                    player.deccelerate(3)
                if event.key == K_ESCAPE:
                    if not paused:
                        paused = True
                    elif paused:
                        paused = False
                if event.key == K_m:
                    if not map_showing:
                        map_showing = True
                    elif map_showing:
                        map_showing = False

        pygame.display.update()
conn1, conn2 = Pipe()
p1 = Process(target = evolution, args=(conn1,))
p2 = Process(target = game, args=(conn2,))

p1.start()
p2.start()

p1.join()
p2.join()
