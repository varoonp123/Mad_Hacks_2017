# @Author: Varoon Pazhyanur <varoon>
# @Date:   18-02-2017
# @Filename: GAME_AND_EVOLUTION.py
# @Last modified by:   varoon
# @Last modified time: 18-02-2017

from random import Random
from time import time
from time import sleep
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

def evolution():
    #6 Traints: health, number of enemies, shot frequency, enemy speed, shot speed, amount of zig zag.
  #generator function. enemy attribues that add up to 100. Only for Generation 0.
  def generate_enemy(random,args):
      SUM_OF_TRAITS = 100
      enemy_feature_vector = []
      #fire rate
      for i in range(1,5):
          enemy_feature_vector.append(random.uniform(1,20))
      #health = random.uniform(1,20)
      #aggression=random.uniform(1,20)
      #dodge_likelihood = random.uniform(1,20)
      #shot_speed = random.uniform(1,20)
      speed = SUM_OF_TRAITS - sum(enemy_feature_vector)
      enemy_feature_vector.append(speed)
      print(enemy_feature_vector)
      #print(sum(enemy_feature_vector))
      return enemy_feature_vector


  #gives segments, calculates area of polygon
  def survival(enemy):
      conn.send(enemy)
      x = conn.recv()
      return max(enemy)

  #evaluator function. returns list of survival scores of entire generation.
  def evaluate_enemy(candidates, args):

      fitness=[]
      #print("eval")
      for cs in candidates:
          fit = survival(cs)
          fitness.append(fit)
      return fitness

  #need to bound each parameter. 0<=EACH_TRAIT<=100
  """
  def bound_enemy(enemy,args):
      #amount still left to be allocated/overallocated. Positive if can add more traits.
      while (sum(enemy) is not 100):
          unallocated = 100-sum(enemy)
          for i in range(0,size(enemy))
              if enemy[i] + unallocated/size(enemy) > 0:      #if adding portion of unallocated keeps trait positive
                  enemy[i] = enemy[i] + unallocated/size(enemy)
      return enemy

  def bound_enemy(candidate, args):
      for i in range(0,size(candidate)):
          candidate[i] = max(min(candidate[i], 100), 0)
      return candidate
  bound_polygon.lower_bound = itertools.repeat(-1)
  bound_polygon.upper_bound = itertools.repeat(1)

  #ACTUAL EVOLUTION
  """
  def mutate_enemy(random,candidates,args):
      #gaussian distrubtion for random mutation
      mut_rate = args.setdefault('mutation_rate', 0.1)
      #bounder = args['_ec'].bounder

      print("mutated")
      return candidates

  #ACTUAL SCRIPT:
  rand = Random()
  rand.seed(int(time()))
  my_ec = inspyred.ec.EvolutionaryComputation(rand)
  my_ec.selector = inspyred.ec.selectors.tournament_selection
  my_ec.variator = [inspyred.ec.variators.uniform_crossover,mutate_enemy]
  my_ec.replacer = inspyred.ec.replacers.steady_state_replacement
  my_ec.terminator = [inspyred.ec.terminators.generation_termination]

  final_pop = my_ec.evolve(generator=generate_enemy,
                           evaluator=evaluate_enemy,
                           pop_size=30,
                           #bounder=inspyred.ec.Bounder(0,100),
                           max_evaluations=500,
                           num_selected=2,
                           mutation_rate=0.25,
                           max_generations=10)
  # Sort and print the best individual, who will be at index 0.
  final_pop.sort(reverse=True)
  print('Terminated due to {0}.'.format(my_ec.termination_cause))
  print(final_pop[0])
  print(my_ec.num_generations)

#----------------------------------------------------------------
#PYGAME SECTION
def game():

    #setup frames per second
    clock = pygame.time.Clock()
    #set initial scene to 0
    scene = 0
    #start pygame
    pygame.init()
    #set up screen display and images
    screen = pygame.display.set_mode(SCREEN_SIZE,0,32)

    #initialize the player
    player = Player(player_img_name, 10, 10, 100, 100)
    #set paused status to false
    paused = False
    map_showing = False
    #initialize first room

    size = 5

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



    while True:

        enemy_attr = [rand.randint(1,10), rand.randint(3,10), rand.randint(1,10)]
        #set clock to save the time between frames
        dt = clock.tick(FPS)
        speed = float(dt)/64

        #print(str(level_1.current_room.enemy_count))
        #print(str(player.health))

        ##########SCENE-RENDERING#########
        #rendering for title scene


        if scene == 0:
            title_screen.display(screen,dt)

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
                        l.on_collision(e)

                for e in level_1.current_room.enemies:
                    e.behave(speed, dt)
                    player.on_collision(e)

                for p in level_1.current_room.portals:
                    p.on_collision(player,screen, enemy_attr)



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



if __name__ == '__main__':
  #conn1, conn2 = Pipe()
  #p1 = Process(target=evolution, args = (conn1,))
  p2 = Process(target=game)

  #p1.start()
  p2.start()

  #p1.join()
  #p2.join()
