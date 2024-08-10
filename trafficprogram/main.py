import pygame
import numpy as np
import pickle
import sys
from matplotlib import style
from drawlines import draw_lanes, draw_boundaries, intersection_hitbox1, intersection_hitbox2
from car import Car
from trafficdirect import traffic_director
from pygame.math import Vector2


start_array_q_table = 'arr_qtable_1.pickle'  # None or Filename
start_array_q_table_b = 'arr_qtable_b_1.pickle'
start_array_q_table_2 = 'arr_qtable_2.pickle'
start_array_q_table_b_2 = 'arr_qtable_b_2.pickle'
start_destination_q_table = 'des_qtable_1.pickle'
start_destination_q_table_b = 'des_qtable_2.pickle'
# can look up from Q-table with: print(q_table[((-9, -2), (3, 9))]) for example

action_choice1 = 0
action_choice2 = 0

traffic_director1 = traffic_director(240, 352, 496, 384, 352, 496, 0, 352, 496, 1024)
traffic_director2 = traffic_director(240, 1024, 1168, 384, 1024, 1168, 496, 1024, 1168, 1520)
number_of_cars = 12

def Action1(choice, cars):
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

def Action2(choice, cars):
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


with open(start_array_q_table, "rb") as f:
    arr_q_table = pickle.load(f)

with open(start_array_q_table_b, "rb") as f:
    arr_q_table_b = pickle.load(f)

with open(start_array_q_table_2, "rb") as f:
    arr_q_table_2 = pickle.load(f)

with open(start_array_q_table_b_2, "rb") as f:
    arr_q_table_b_2 = pickle.load(f)

with open(start_destination_q_table, "rb") as f:
    des_q_table = pickle.load(f)

with open(start_destination_q_table_b, "rb") as f:
    des_q_table_b = pickle.load(f)


def main():
    pygame.init()
    screen = pygame.display.set_mode((1520, 624))
    pygame.display.set_caption("Traffic Sim")

    clock = pygame.time.Clock()

    cars = []
    hitboxes = []
    front_hitboxes = []

    current_time = pygame.time.get_ticks()

    action_time_1 = 0
    action_time_2 = 0

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

            if car.velocity == Vector2(0,0):
                car.stopped_time += 1

            if car.stopped_time > 1000:
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
            elif car.intersection_collision and not car.turned:
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

        if current_time > 1000:
            if current_time - action_time_1 > 400:
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

                for i in range(0, 8):
                    if x1 < 0.5:
                        list1[i] += arr_q_table[array_obs1][i]
                    else:
                        list1[i] += arr_q_table_b[array_obs1][i]
                    if y1 < 0.5:
                        list1[i] += 0.5 * des_q_table[destination_obs1][i]
                    else:
                        list1[i] += 0.5 * des_q_table_b[destination_obs1][i]

                action1 = np.argmax([list1])
                Action1(action1, cars)

                action_time_1 = current_time

            if current_time - action_time_2 > 400:
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

                for i in range(0, 8):
                    if x2 < 0.5:
                        list2[i] += arr_q_table_2[array_obs2][i]
                    else:
                        list2[i] += arr_q_table_b_2[array_obs2][i]
                    if y2 < 0.5:
                        list2[i] += 0.5 * des_q_table[destination_obs2][i]
                    else:
                        list2[i] += 0.5 * des_q_table_b[destination_obs2][i]

                action2 = np.argmax([list2])
                Action2(action2, cars)

                action_time_2 = current_time

if __name__ == '__main__':
    main()