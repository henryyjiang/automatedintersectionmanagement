import pygame
import numpy as np
import pickle
import sys
from matplotlib import style
from drawlines import draw_lanes, draw_boundaries, intersection_hitbox1, intersection_hitbox2
from car import Car
from trafficdirect import traffic_director
from pygame.math import Vector2

style.use("ggplot")

HM_EPISODES = 10000
SHOW_EVERY = 100

TIME_PENALTY = 1
LENGTH_PENALTY = 20
STOPPED_PENALTY = 10
MOVED_REWARD = 5

epsilon = 1.0
EPS_DECAY = 0.9997

LEARNING_RATE = 0.1
DISCOUNT = 0.95

DESTINATION_WEIGHT = 0.5

sys.path.append("..")
start_arr_q_table_1 = None
start_arr_q_table_b_1 = None
start_arr_q_table_2 = None
start_arr_q_table_b_2 = None
start_des_q_table = 'qtables/des_qtable_1.pickle'
start_des_q_table_b = 'qtables/des_qtable_2.pickle'

action_choice = 0

traffic_director1 = traffic_director(240, 352, 496, 384, 352, 496, 0, 352, 496, 1024)
traffic_director2 = traffic_director(240, 1024, 1168, 384, 1024, 1168, 496, 1024, 1168, 1520)
number_of_cars = 16


def Action(choice, cars, traffic_director, intersection_hitbox):
    global action_choice
    if choice == action_choice:
        pass
    else:
        action_choice = choice
        y = False
        for car in cars:
            if pygame.Rect(car.hitbox).colliderect(intersection_hitbox) and car.velocity == Vector2(150, 0):
                y = True
        if not y:
            traffic_director.greenlight(choice)
            # i don't know why but cars stop inside of each other sometimes if this line isn't there
            traffic_director.yellow_light_state = False
        else:
            traffic_director.yellowlight(choice, cars)


if start_arr_q_table_1 is None:
    arr_q_table_1 = {}
    for i in range(0, 10):
        for ii in range(0, 10):
            for iii in range(0, 10):
                for iiii in range(0, 14):
                    arr_q_table_1[(i, ii, iii, iiii)] = [np.random.uniform(-5, 0) for i in range(8)]
else:
    with open(start_arr_q_table_1, "rb") as f:
        arr_q_table_1 = pickle.load(f)

if start_arr_q_table_b_1 is None:
    arr_q_table_b_1 = {}
    for i in range(0, 10):
        for ii in range(0, 10):
            for iii in range(0, 10):
                for iiii in range(0, 14):
                    arr_q_table_b_1[(i, ii, iii, iiii)] = [np.random.uniform(-5, 0) for i in range(8)]
else:
    with open(start_arr_q_table_b_1, "rb") as f:
        arr_q_table_b_1 = pickle.load(f)

if start_arr_q_table_2 is None:
    arr_q_table_2 = {}
    for i in range(0, 10):
        for ii in range(0, 10):
            for iii in range(0, 14):
                for iiii in range(0, 10):
                    arr_q_table_2[(i, ii, iii, iiii)] = [np.random.uniform(-5, 0) for i in range(8)]
else:
    with open(start_arr_q_table_2, "rb") as f:
        arr_q_table_2 = pickle.load(f)

if start_arr_q_table_b_2 is None:
    arr_q_table_b_2 = {}
    for i in range(0, 10):
        for ii in range(0, 10):
            for iii in range(0, 14):
                for iiii in range(0, 10):
                    arr_q_table_b_2[(i, ii, iii, iiii)] = [np.random.uniform(-5, 0) for i in range(8)]
else:
    with open(start_arr_q_table_b_2, "rb") as f:
        arr_q_table_b_2 = pickle.load(f)

if start_des_q_table is None:
    des_q_table = {}
    for i in range(0, 3):
        for ii in range(0, 3):
            for iii in range(0, 3):
                for iiii in range(0, 3):
                    des_q_table[(i, ii, iii, iiii)] = [np.random.uniform(-5, 0) for i in range(8)]
else:
    with open(start_des_q_table, "rb") as f:
        des_q_table = pickle.load(f)

if start_des_q_table_b is None:
    des_q_table_b = {}
    for i in range(0, 3):
        for ii in range(0, 3):
            for iii in range(0, 3):
                for iiii in range(0, 3):
                    des_q_table_b[(i, ii, iii, iiii)] = [np.random.uniform(-5, 0) for i in range(8)]
else:
    with open(start_des_q_table_b, "rb") as f:
        des_q_table_b = pickle.load(f)

for i in range(0, 8):
    arr_q_table_1[(i, 0, 0, 0)] = [-5, -5, -5, -5, -5, 0, -5, -5]
    arr_q_table_1[(0, i, 0, 0)] = [-5, -5, -5, -5, 0, -5, -5, -5]
    arr_q_table_1[(0, 0, i, 0)] = [-5, -5, -5, -5, -5, -5, 0, -5]
    arr_q_table_1[(0, 0, 0, i)] = [-5, -5, -5, -5, -5, -5, -5, 0]
    arr_q_table_b_1[(i, 0, 0, 0)] = [-5, -5, -5, -5, -5, 0, -5, -5]
    arr_q_table_b_1[(0, i, 0, 0)] = [-5, -5, -5, -5, 0, -5, -5, -5]
    arr_q_table_b_1[(0, 0, i, 0)] = [-5, -5, -5, -5, -5, -5, 0, -5]
    arr_q_table_b_1[(0, 0, 0, i)] = [-5, -5, -5, -5, -5, -5, -5, 0]
    arr_q_table_2[(i, 0, 0, 0)] = [-5, -5, -5, -5, -5, 0, -5, -5]
    arr_q_table_2[(0, i, 0, 0)] = [-5, -5, -5, -5, 0, -5, -5, -5]
    arr_q_table_2[(0, 0, i, 0)] = [-5, -5, -5, -5, -5, -5, 0, -5]
    arr_q_table_2[(0, 0, 0, i)] = [-5, -5, -5, -5, -5, -5, -5, 0]
    arr_q_table_b_2[(i, 0, 0, 0)] = [-5, -5, -5, -5, -5, 0, -5, -5]
    arr_q_table_b_2[(0, i, 0, 0)] = [-5, -5, -5, -5, 0, -5, -5, -5]
    arr_q_table_b_2[(0, 0, i, 0)] = [-5, -5, -5, -5, -5, -5, 0, -5]
    arr_q_table_b_2[(0, 0, 0, i)] = [-5, -5, -5, -5, -5, -5, -5, 0]

episode_rewards_1 = []
episode_rewards_2 = []
for episode in range(HM_EPISODES):
    pygame.init()
    screen = pygame.display.set_mode((1520, 624))
    pygame.display.set_caption("Traffic Sim 2")

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
            if current_time - action_time_1 > 700:
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

                if np.random.random() > epsilon:
                    for i in range(0, 8):
                        if x1 < 0.5:
                            list1[i] += arr_q_table_1[array_obs1][i]
                        else:
                            list1[i] += arr_q_table_b_1[array_obs1][i]
                        if y1 < 0.5:
                            list1[i] += DESTINATION_WEIGHT * des_q_table[destination_obs1][i]
                        else:
                            list1[i] += DESTINATION_WEIGHT * des_q_table_b[destination_obs1][i]

                    action1 = np.argmax([list1])
                else:
                    action1 = np.random.randint(0, 8)

                Action(action1, cars, traffic_director1, intersection_hitbox1)

                action_time_1 = current_time
                obs_time_1 = current_time
                loop1 = 0
            else:
                pass

            if current_time - action_time_2 > 700:
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

                if np.random.random() > epsilon:
                    for i in range(0, 8):
                        if x2 < 0.5:
                            list2[i] += arr_q_table_2[array_obs2][i]
                        else:
                            list2[i] += arr_q_table_b_2[array_obs2][i]
                        if y2 < 0.5:
                            list2[i] += DESTINATION_WEIGHT * des_q_table[destination_obs2][i]
                        else:
                            list2[i] += DESTINATION_WEIGHT * des_q_table_b[destination_obs2][i]

                    action2 = np.argmax([list2])
                else:
                    action2 = np.random.randint(0, 8)

                Action(action2, cars, traffic_director2, intersection_hitbox2)

                action_time_2 = current_time
                obs_time_2 = current_time
                loop2 = 0
            else:
                pass

            if current_time - obs_time_1 > 650:
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


                    if x1 < 0.5:
                        max_future_q_1 = arr_q_table_b_1[new_array_obs1][np.argmax(arr_q_table_1[new_array_obs1])]
                        current_q_1 = arr_q_table_1[array_obs1][action1]
                    else:
                        max_future_q_1 = arr_q_table_1[new_array_obs1][np.argmax(arr_q_table_b_1[new_array_obs1])]
                        current_q_1 = arr_q_table_b_1[array_obs1][action1]

                    if x1 < 0.5:
                        arr_q_table_1[array_obs1][action1] += LEARNING_RATE * (
                                reward1 + DISCOUNT * max_future_q_1 - current_q_1)
                    else:
                        arr_q_table_b_1[array_obs1][action1] += LEARNING_RATE * (
                                reward1 + DISCOUNT * max_future_q_1 - current_q_1)

                    # if y1 < 0.5:
                    #     des_q_table[destination_obs1][action1] += LEARNING_RATE * (
                    #                 reward1 + DISCOUNT * max_future_q_1 - current_q_1)
                    # else:
                    #     des_q_table_b[destination_obs1][action1] += LEARNING_RATE * (
                    #                 reward1 + DISCOUNT * max_future_q_1 - current_q_1)

                    episode_reward_1 += reward1
            else:
                pass

            if current_time - obs_time_2 > 650:
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


                    if x2 < 0.5:
                        max_future_q_2 = arr_q_table_b_2[new_array_obs2][np.argmax(arr_q_table_2[new_array_obs2])]
                        current_q_2 = arr_q_table_2[array_obs2][action2]
                    else:
                        max_future_q_2 = arr_q_table_2[new_array_obs2][np.argmax(arr_q_table_b_2[new_array_obs2])]
                        current_q_2 = arr_q_table_b_2[array_obs2][action2]

                    if x2 < 0.5:
                        arr_q_table_2[array_obs2][action2] += LEARNING_RATE * (
                                reward2 + DISCOUNT * max_future_q_2 - current_q_2)
                    else:
                        arr_q_table_b_2[array_obs2][action2] += LEARNING_RATE * (
                                reward2 + DISCOUNT * max_future_q_2 - current_q_2)

                    # if y2 < 0.5:
                    #     des_q_table[destination_obs2][action2] += LEARNING_RATE * (
                    #                 reward2 + DISCOUNT * max_future_q_2 - current_q_2)
                    # else:
                    #     des_q_table_b[destination_obs2][action2] += LEARNING_RATE * (
                    #                 reward2 + DISCOUNT * max_future_q_2 - current_q_2)

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

with open(f"arr_qtable_1_v3.pickle", "wb") as f:
    pickle.dump(arr_q_table_1, f)

with open(f"arr_qtable_2_v3.pickle", "wb") as f:
    pickle.dump(arr_q_table_2, f)

with open(f"arr_qtable_b_1_v3.pickle", "wb") as f:
    pickle.dump(arr_q_table_b_1, f)

with open(f"arr_qtable_b_2_v3.pickle", "wb") as f:
    pickle.dump(arr_q_table_b_2, f)

# with open(f"des_qtable_1.pickle", "wb") as f:
#     pickle.dump(des_q_table, f)
#
# with open(f"des_qtable_2.pickle", "wb") as f:
#     pickle.dump(des_q_table_b, f)