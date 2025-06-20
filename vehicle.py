from PIL import ImageTk
import matplotlib.pyplot as plt
import PIL.Image
from tkinter import *
from tkinter import ttk
import math

def move_direction(x, y, direction_deg, distance):
    """
    Move from an initial position (x, y) by a certain distance in a specified direction.
    
    :param x: Initial x-coordinate.
    :param y: Initial y-coordinate.
    :param direction_deg: Direction in degrees (0° is along the positive x-axis, increasing clockwise).
    :param distance: Distance to move.
    :return: Tuple (new_x, new_y) representing the new position.
    """
    # Convert direction from degrees to radians
    direction_rad = math.radians(direction_deg)
    
    # Calculate new coordinates
    new_x = x + distance * math.cos(direction_rad)
    new_y = y + distance * math.sin(direction_rad)
    
    return new_x, new_y

class vehicle:
    def __init__(self, posx, posy, width, height, sprite, debug=True):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = 0
        self.brakeforce = 0
        self.direction = 0
        self.steer = 0
        
        self.monitorres = [1920, 1080]

        self.maxsteer = 2
        self.maxspeed = 6.3
        self.maxbrake = 0.045

        self.source = PIL.Image.open(sprite)
        self.sprite = self.source.resize((self.width, self.height))
        self.keyspressed = []

        self.root = Tk()
        self.root.overrideredirect(True)
        self.place(self.posx, self.posy)

        self.debug = debug
        if self.debug:
            self.initdebug()

        self.canvas = Canvas(self.root, bg="#696969", highlightthickness=0) # set it to this color, so that its transparent
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.wm_attributes('-transparentcolor','#696969')
        self.root.wm_attributes('-topmost', True)

        self.root.bind('<KeyPress>', self.keydown)
        self.root.bind('<KeyRelease>', self.keyup)
    
    def initdebug(self):
        self.debugwin = Toplevel(self.root)
        self.debugwin.geometry("300x300")
        self.inputsteer = IntVar()
        steerbar = ttk.Progressbar(self.debugwin, variable=self.inputsteer, maximum=self.maxsteer*2)
        steerbar.place(anchor=CENTER, relx=0.5, rely=0.1)
        self.outputsteer = IntVar()
        steerbar = ttk.Progressbar(self.debugwin, variable=self.outputsteer, maximum=self.maxsteer*2)
        steerbar.place(anchor=CENTER, relx=0.5, rely=0.2)
        
        # speedometer
        self.brakevalue = IntVar()
        self.brakeinput = ttk.Progressbar(self.debugwin, variable=self.brakevalue, maximum=self.maxbrake)
        self.brakeinput.place(anchor=CENTER, relx=0.5, rely=0.3)

        # speedometer
        self.speedvalue = IntVar()
        self.speedometer = ttk.Progressbar(self.debugwin, variable=self.speedvalue, maximum=self.maxspeed)
        self.speedometer.place(anchor=CENTER, relx=0.5, rely=0.4)
        self.speedlabel = Label(self.debugwin, text="0")
        self.speedlabel.place(anchor=CENTER, relx=0.5, rely=0.5)

    def keydown(self, e):
        if not e.keycode in self.keyspressed:
            self.keyspressed.append(e.keycode)

    def keyup(self, e):
        if e.keycode in self.keyspressed:
            del self.keyspressed[self.keyspressed.index(e.keycode)]

    def move(self, posx, posy):
        self.place(self.posx + posx, self.posy + posy)

    def place(self, posx, posy):
        self.posx = posx
        self.posy = posy
        self.root.geometry(str(self.width)+"x"+str(self.height)+"+"+str(int(posx))+"+"+str(int(posy)))

    def steerleft(self):
        if -self.maxsteer*0.2 > self.steer > -self.maxsteer*0.5:
            self.steer += 0.2
        self.steer += 0.2
        if self.steer > self.maxsteer:
            self.steer = self.maxsteer

    def steerright(self):
        if self.maxsteer*0.2 < self.steer < self.maxsteer*0.5:
            self.steer -= 0.2
        self.steer -= 0.2
        if self.steer < -self.maxsteer:
            self.steer = -self.maxsteer

    def steercenter(self):
        if self.steer > 0:
            self.steer -= 0.25
            if self.steer < 0:
                self.steer = 0
        if self.steer < 0:
            self.steer += 0.25
            if self.steer > 0:
                self.steer = 0
    
    def limitsteer(self):
        if not self.speed > 0:
            return self.steer
        steer = self.steer / ( self.speed * 0.7 )
        # dont steer too slow
        if self.speed * 0.7 > self.maxspeed * 0.5:
            steer = self.steer / ( self.maxspeed * 0.5 )

        # dont steer too fast (aka. fidget spinner when going very slow)
        if self.steer > 0 and steer > self.steer*0.8:
            steer = self.steer*0.8
        elif -self.steer < 0 and steer < -self.steer*0.8:
            steer = self.steer*0.8
        
        # low steering on low speed
        if self.speed < self.maxspeed * 0.4:
            steer = self.steer*0.6
        if self.speed < self.maxspeed * 0.1:
            steer = self.steer*0.35
        
        # dont turn when too slow
        if self.speed < self.maxspeed * 0.03:
            steer = 0
        return steer

    def accelerate(self):
        if self.steer > 0 and self.steer > self.maxsteer*0.4 or self.steer < 0 and self.steer < -self.maxsteer*0.4:
            if self.speed < self.maxspeed * 0.35:
                self.speed += 0.02
            if self.speed > self.maxspeed * 0.75:
                self.speed += 0.035
            else:
                self.speed += 0.03
        else:
            self.speed += 0.04
        
        if self.speed > self.maxspeed:
            self.speed = self.maxspeed
    
    def decelerate(self):
        if self.speed > 0:
            self.speed -= 0.01
        if self.speed < 0:
            self.speed = 0
    
    def brake(self):
        self.brakeforce += self.maxbrake*0.1
        if self.brakeforce > self.maxbrake:
            self.brakeforce = self.maxbrake
            
        if self.speed > 0:
            if self.steer > 0 and self.steer > self.maxsteer*0.2 or self.steer < 0 and self.steer < -self.maxsteer*0.2:
                if self.speed > self.maxspeed*0.7:
                    self.brakeforce *= 0.85
                else:
                    self.brakeforce *= 0.9
            self.speed -= self.brakeforce
        if self.speed < 0:
            self.speed = 0
    
    def brakerelease(self):
        self.brakeforce -= 0.008
        if self.brakeforce < 0:
            self.brakeforce = 0

    def updateposition(self):
        if self.speed > 0:
            self.direction += self.limitsteer()
            x, y = move_direction(self.posx, self.posy, 360-self.direction, self.speed)
            # print(str(x)+" "+str(y))
            if x > self.monitorres[0]:
                x = -self.width
            if x < -10-self.width:
                x = self.monitorres[0]
            if y > self.monitorres[1]:
                y = 0-self.height
            if y < -10-self.height:
                y = self.monitorres[1]
            self.place(x, y)

    def update(self):
        # print keys pressed:
        # print(self.keyspressed)
        photoimage = ImageTk.PhotoImage(self.sprite.rotate(self.direction-90))
        self.canvas.delete('all')
        self.canvas.create_image(self.width/2, self.height/2, image=photoimage, anchor=CENTER)
        if self.debug:
            self.inputsteer.set((self.steer*-1)+self.maxsteer)
            self.outputsteer.set((self.limitsteer()*-1)+self.maxsteer)
            self.speedvalue.set(self.speed)
            self.speedlabel["text"] = int(self.speed*20)
            self.brakevalue.set(self.brakeforce)
            self.debugwin.update()
        self.root.update()