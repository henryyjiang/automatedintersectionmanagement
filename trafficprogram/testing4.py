import pygame
import numpy as np
import pickle
import sys
from matplotlib import style
from drawlines import draw_lanes, draw_boundaries, intersection_hitbox1, intersection_hitbox2
from car import Car
from trafficdirect import traffic_director
from pygame.math import Vector2
#CONTROL
style.use("ggplot")

HM_EPISODES = 600
SHOW_EVERY = 100

TIME_PENALTY = 1
LENGTH_PENALTY = 20
STOPPED_PENALTY = 10
MOVED_REWARD = 5

epsilon = 0.0
EPS_DECAY = 0.9997

LEARNING_RATE = 0.1
DISCOUNT = 0.95

DESTINATION_WEIGHT = 0.5

action_choice1 = 0
action_choice2 = 0

traffic_director1 = traffic_director(240, 352, 496, 384, 352, 496, 0, 352, 496, 1024)
traffic_director2 = traffic_director(240, 1024, 1168, 384, 1024, 1168, 496, 1024, 1168, 1520)
number_of_cars = 16


def Action1(choice):
    global action_choice1
    if choice == action_choice1:
        pass
    else:
        action_choice1 = choice
        y = False
        for car in cars:
            if pygame.Rect(car.hitbox).colliderect(intersection_hitbox1) and car.velocity == Vector2(150, 0):
                y = True
        if not y:
            traffic_director1.greenlight(choice)
            traffic_director1.yellow_light_state = False
        else:
            traffic_director1.yellowlight(choice, cars)

def Action2(choice):
    global action_choice2
    if choice == action_choice2:
        pass
    else:
        action_choice2 = choice
        y = False
        for car in cars:
            if pygame.Rect(car.hitbox).colliderect(intersection_hitbox2) and car.velocity == Vector2(150, 0):
                y = True
        if not y:
            traffic_director2.greenlight(choice)
            traffic_director2.yellow_light_state = False
        else:
            traffic_director2.yellowlight(choice, cars)

episode_rewards_1 = []
episode_rewards_2 = []
for episode in range(HM_EPISODES):
    pygame.init()
    screen = pygame.display.set_mode((1520, 624))
    pygame.display.set_caption("Traffic Sim 4")

    clock = pygame.time.Clock()

    if episode % SHOW_EVERY == 0:
        print(f"on #{episode}, epsilon is {epsilon}")
        print(f"{SHOW_EVERY} ep mean: {np.mean(episode_rewards_1[-SHOW_EVERY:])}")
        print(f"{SHOW_EVERY} ep mean: {np.mean(episode_rewards_2[-SHOW_EVERY:])}")

    episode_reward_1 = 0
    episode_reward_2 = 0

    cars = []
    hitboxes = []
    front_hitboxes = []

    current_time = pygame.time.get_ticks()

    action_time_1 = 0
    action_time_2 = 0
    action_state1 = 3
    action_state2 = 3
    action_change_time1 = 0
    action_change_time2 = 0
    obs_time_1 = 0
    obs_time_2 = 0

    for car in range(number_of_cars):
        cars.append(Car(screen, pygame.time.get_ticks()))
    for car in cars:
        hitboxes.append(car.hitbox)
        front_hitboxes.append(car.front_hitbox)

    running = True
    while running:
        screen.fill((255, 255, 255))
        draw_lanes(screen)
        draw_boundaries(screen)
        dt = clock.get_time() / 1000

        i = 0
        for car in cars:
            car.current_time = current_time
            hitboxes[i] = car.hitbox
            if not car.arrived_at_destination:
                front_hitboxes[i] = car.front_hitbox
            else:
                front_hitboxes[i] = (0,0,0,0)

            for hitbox in hitboxes:
                if hitbox == car.hitbox:
                    pass
                elif pygame.Rect(car.front_hitbox).colliderect(hitbox):
                    car.collision = True
                    break
                else:
                    car.collision = False

            for front_hitbox in front_hitboxes:
                if front_hitbox == car.front_hitbox:
                    pass
                elif pygame.Rect(car.front_hitbox).colliderect(front_hitbox) and not car.intersection_collision:
                    car.respawn()

            if pygame.Rect(car.hitbox).colliderect(pygame.Rect(intersection_hitbox1)):
                car.intersection_collision = True
            elif pygame.Rect(car.hitbox).colliderect(pygame.Rect(intersection_hitbox2)):
                car.intersection_collision = True
            else:
                car.intersection_collision = False

            if current_time - car.respawn_timer < 300 and car.collision:
                car.respawn()

            if car.velocity == Vector2(0, 0):
                car.stopped_time += 1

            if car.stopped_time > 2000:
                car.respawn()

            # draw destination
            # pygame.draw.circle(screen, (20, 20, 255), car.destination, 10)

            i = i + 1


        def lane_move(traffic_director):
            for x in traffic_director.array_state:
                if traffic_director.array_state[x] == 0:
                    for car in traffic_director.arrays[x]:
                        car.turned = False
                elif traffic_director.array_state[x] == 1:
                    for car in traffic_director.arrays[x]:
                        car.turned = True


        lane_move(traffic_director1)
        lane_move(traffic_director2)

        for car in cars:
            if not car.intersection_collision:
                car.turned = False
            elif car.turned:
                car.collision = False
            elif pygame.Rect(car.front_hitbox).colliderect(pygame.Rect(intersection_hitbox1)) or pygame.Rect(
                    car.front_hitbox).colliderect(pygame.Rect(intersection_hitbox2)):
                if not car.turned:
                    car.collision = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for car in cars:
            car.update(dt)

        traffic_director1.update(cars)
        traffic_director2.update(cars)

        current_time = pygame.time.get_ticks()
        clock.tick(60)
        pygame.display.update()

        if current_time > 3000:
            if current_time - action_time_1 > 1200:
                top_car_val1 = 3
                bottom_car_val1 = 3
                right_car_val1 = 3
                left_car_val1 = 3

                for car in traffic_director1.front_cars['top']:
                    top_car_val1 = car.turn_direction
                for car in traffic_director1.front_cars['bottom']:
                    bottom_car_val1 = car.turn_direction
                for car in traffic_director1.front_cars['left']:
                    left_car_val1 = car.turn_direction
                for car in traffic_director1.front_cars['right']:
                    right_car_val1 = car.turn_direction

                array_obs1 = (len(traffic_director1.arrays['top']), len(traffic_director1.arrays['bottom']),
                              len(traffic_director1.arrays['left']), len(traffic_director1.arrays['right']))
                destination_obs1 = (top_car_val1, bottom_car_val1, left_car_val1, right_car_val1)

                x1 = np.random.rand()
                y1 = np.random.rand()
                list1 = [0, 0, 0, 0, 0, 0, 0, 0]


                if current_time - action_change_time1 > 1200:
                    if action_state1 == 0:
                        action_state1 = 3
                    else:
                        action_state1 -= 1
                    action1 = action_state1
                    action_change_time1 = current_time

                Action1(action1)

                action_time_1 = current_time
                obs_time_1 = current_time
                loop1 = 0
            else:
                pass

            if current_time - action_time_2 > 1200:
                top_car_val2 = 3
                bottom_car_val2 = 3
                right_car_val2 = 3
                left_car_val2 = 3

                for car in traffic_director2.front_cars['top']:
                    top_car_val2 = car.turn_direction
                for car in traffic_director2.front_cars['bottom']:
                    bottom_car_val2 = car.turn_direction
                for car in traffic_director2.front_cars['left']:
                    left_car_val2 = car.turn_direction
                for car in traffic_director2.front_cars['right']:
                    right_car_val2 = car.turn_direction

                array_obs2 = (len(traffic_director2.arrays['top']), len(traffic_director2.arrays['bottom']),
                              len(traffic_director2.arrays['left']), len(traffic_director2.arrays['right']))
                destination_obs2 = (top_car_val2, bottom_car_val2, left_car_val2, right_car_val2)

                x2 = np.random.rand()
                y2 = np.random.rand()
                list2 = [0, 0, 0, 0, 0, 0, 0, 0]

                if current_time - action_change_time2 > 1200:
                    if action_state2 == 0:
                        action_state2 = 3
                    else:
                        action_state2 -= 1
                    action2 = action_state2
                    action_change_time2 = current_time

                    Action2(action2)

                action_time_2 = current_time
                obs_time_2 = current_time
                loop2 = 0
            else:
                pass

            if current_time - obs_time_1 > 1150:
                if loop1 == 0:
                    loop1 += 1
                    reward1 = -1
                    cars_moved1 = False

                    new_array_obs1 = (len(traffic_director1.arrays['top']), len(traffic_director1.arrays['bottom']),
                                      len(traffic_director1.arrays['left']), len(traffic_director1.arrays['right']))

                    if array_obs1 == (0,0,0,0):
                        reward1 = 0
                    else:
                        for array in traffic_director1.arrays:
                            if len(traffic_director1.arrays[array]) > 4:
                                reward1 += -LENGTH_PENALTY
                                break
                        if array_obs1 == new_array_obs1:
                            reward1 += -STOPPED_PENALTY
                        for i in range(0,4):
                            if list(array_obs1)[i] > list(new_array_obs1)[i]:
                                cars_moved1 = True
                        if cars_moved1:
                            reward1 += MOVED_REWARD

                    episode_reward_1 += reward1
            else:
                pass

            if current_time - obs_time_2 > 1150:
                if loop2 == 0:
                    loop2 += 1
                    reward2 = -1
                    cars_moved2 = False

                    new_array_obs2 = (len(traffic_director2.arrays['top']), len(traffic_director2.arrays['bottom']),
                                      len(traffic_director2.arrays['left']), len(traffic_director2.arrays['right']))


                    if array_obs2 == (0,0,0,0):
                        reward2 = 0
                    else:
                        for array in traffic_director2.arrays:
                            if len(traffic_director2.arrays[array]) > 4:
                                reward2 += -LENGTH_PENALTY
                                break
                        if array_obs2 == new_array_obs2:
                            reward2 += -STOPPED_PENALTY
                        for i in range(0,4):
                            if list(array_obs2)[i] > list(new_array_obs2)[i]:
                                cars_moved2 = True
                        if cars_moved2:
                            reward2 += MOVED_REWARD

                    episode_reward_2 += reward2

            else:
                pass

            all_stopped = True
            for car in cars:
                if not car.arrived_at_destination:
                    all_stopped = False
            if all_stopped:
                break

            if len(traffic_director1.arrays['top']) >= 5:
                break
            if len(traffic_director1.arrays['bottom']) >= 5:
                break
            if len(traffic_director1.arrays['left']) >= 6:
                break
            if len(traffic_director1.arrays['right']) >= 9:
                break
            if len(traffic_director2.arrays['top']) >= 5:
                break
            if len(traffic_director2.arrays['bottom']) >= 5:
                break
            if len(traffic_director2.arrays['left']) >= 9:
                break
            if len(traffic_director2.arrays['right']) >= 6:
                break

    episode_rewards_1.append(episode_reward_1)
    episode_rewards_2.append(episode_reward_2)
    epsilon *= EPS_DECAY
