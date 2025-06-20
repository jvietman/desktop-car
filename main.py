from tkinter import *
from tkinter import ttk

from vehicle import *

pos = [500, 500]
car = vehicle(pos[0], pos[1], 70, 70, "car.png", debug=True)

wait = 3
cur = 0
while True:
    car.update()
    # print(str(car.steer)+"   "+str(car.limitsteer()))
    # print(car.speed)
    if cur >= wait:
        # reset
        if 69 in car.keyspressed:
            car.place(pos[0], pos[1])
            car.speed = 0

        # accelerate
        if 87 in car.keyspressed:
            car.accelerate()
        else:
            car.decelerate()
        if 83 in car.keyspressed:
            car.brake()
        else:
            car.brakerelease()
        
        # steer
        if 65 in car.keyspressed: # left
            car.steerleft()
        elif 68 in car.keyspressed: # right
            car.steerright()
        else:
            car.steercenter()
        
        car.updateposition()
        cur = 0
    cur += 1