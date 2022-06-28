from asyncio.windows_events import NULL
import math, pygame, time, threading
import tkinter as tk

def pauseGame():
    global paused
    if paused == True:
        paused = False
        pauseBtn.config(text='Pause')
    else:
        paused = True
        pauseBtn.config(text='Unpause')

def popBody():
    global bodies
    body = bodies.pop(len(bodies)-1)
    del body

def clearBodies():
    global bodies
    bodies = []

def updateG(self):
    global gravConstant
    gravConstant = (int(GSlider.get()))*(10**-4)


def windowFunction():
    global massInp
    global radiusInp
    global pauseBtn
    global GSlider

    window = tk.Tk()
    windowWidth, windowHeight = 200,210
    window.geometry(str(windowWidth)+'x'+str(windowHeight))

    pauseBtn = tk.Button(text="Pause",height=1, command = pauseGame)
    pauseBtn.place(x=65,y=10)

    massLabel = tk.Label(text="Mass:")
    massLabel.place(x=10,y=40)
    massInp = tk.Entry(fg="black", bg="white", width=10)
    massInp.place(x=55,y=42)

    radiusLabel = tk.Label(text="Radius:")
    radiusLabel.place(x=10,y=65)
    radiusInp = tk.Entry(fg="black", bg="white", width=10)
    radiusInp.place(x=55,y=65)

    GLabel = tk.Label(text="Gravitational\nConstant")
    GLabel.place(x=10,y=93)
    GSlider = tk.Scale(window, from_=0, to=500, orient=tk.HORIZONTAL, command=updateG)
    GSlider.set(6.67)
    GSlider.place(x=80,y=85)

    clearBtn = tk.Button(text="Undo",height=1,command = popBody)
    clearBtn.place(x=65,y=135)

    undoBtn = tk.Button(text="Clear",height=1,command = clearBodies)
    undoBtn.place(x=66,y=167)

    window.mainloop()

def moveCamera(key): #shift position of bodies to simulate camera moving
    global bodies
    if key == 'left':
        for body in bodies:
            curPos = body.pos
            body.pos = [curPos[0]+cameraSpeed,curPos[1]]
    elif key == 'right':
        for body in bodies:
            curPos = body.pos
            body.pos = [curPos[0]-cameraSpeed,curPos[1]]
    elif key == 'up':
        for body in bodies:
            curPos = body.pos
            body.pos = [curPos[0],curPos[1]+cameraSpeed]
    elif key == 'down':
        for body in bodies:
            curPos = body.pos
            body.pos = [curPos[0],curPos[1]-cameraSpeed]

def getNewSpeed():
    global creatingBody
    global bodyIndex
    global bodies
    startPos = pygame.mouse.get_pos()
    while True:
        pygame.draw.line(screen, (255,0,0), startPos, pygame.mouse.get_pos(),3)
        if creatingBody == False:
            bodyIndex += 1
            endPos = pygame.mouse.get_pos()
            xVel = (endPos[0]-startPos[0])/speedReduction*-1
            yVel = (endPos[1]-startPos[1])/speedReduction*-1
            bodies.append(bodyClass([startPos[0]-(width/2),startPos[1]-(height/2)], bodyIndex, xVel, yVel))
            return
    

def calcVelocity(sep,mass):
    return math.sqrt((gravConstant*mass)/sep)

class bodyClass():
    def __init__(self,pos,id,xVel,yVel):
        try:
            newMass = int(massInp.get())
            if massInp != '':
                self.mass = int(newMass)
            else:
                self.mass = defaultMass
        except:
            self.mass = defaultMass

        try:
            newRadius = int(radiusInp.get())
            if massInp != '':
                self.radius = int(newRadius)
            else:
                self.radius = defaultRadius
        except:
            self.radius = defaultRadius

        self.xVel = xVel
        self.yVel = yVel
        self.pos = pos
        self.id = id
    
    def updateVelocities(self):
        for body in bodies:
            if body.id != self.id:
                xDiff = body.pos[0]-self.pos[0]
                yDiff = body.pos[1]-self.pos[1]
                
                xPol = 1
                yPol = 1
                if xDiff < 0:
                    xPol = -1
                if yDiff < 0:
                    yPol = -1 

                newVel = calcVelocity(abs(xDiff)+abs(yDiff),body.mass)
                self.xVel += (newVel*(abs(xDiff)/(abs(xDiff)+abs(yDiff))))*xPol
                self.yVel += (newVel*(abs(yDiff)/(abs(xDiff)+abs(yDiff))))*yPol

    def updatePositions(self):
        self.pos = [self.pos[0]+self.xVel, self.pos[1]+self.yVel]
    

threading.Thread(target=windowFunction).start()

bodies = []
gravConstant = 6.67*(10**-4)
speedReduction = 5 #used to reduce the velocity when creating a planet
size = width, height = 1000, 800
countsMeasured = 10 #number of frames mouse is measured when determining new velocity
defaultMass = 20
defaultRadius = 7

#bodies.append(bodyClass(500,[-50,0],0,0,0))
bodyIndex = len(bodies) #used to give new bodies individual indexes

cameraSpeed = 10 #number of pixels moved per camera shift frame
screen = pygame.display.set_mode(size)

creatingBody = False
done = False
paused = False
collisions = True #check for collisions, combine the bodies
while not done:
    keys = pygame.key.get_pressed()  #checking pressed keys
    if keys[pygame.K_UP]:
        moveCamera('up')
    if keys[pygame.K_DOWN]:
        moveCamera('down')
    if keys[pygame.K_LEFT]:
        moveCamera('left')
    if keys[pygame.K_RIGHT]:
        moveCamera('right')
    if keys[pygame.K_SPACE]:
        pauseGame()
        
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    screen.fill((255,255,255))

    mouse = pygame.mouse.get_pressed()
    if mouse[0] and creatingBody == False:
        creatingBody = True
        threading.Thread(target=getNewSpeed).start()

    if not mouse[0] and creatingBody == True:
        creatingBody = False

    if not paused:
        for body in bodies:
            body.updateVelocities()
            body.updatePositions()
            
    for body in bodies:
        pygame.draw.circle(screen, (0,0,0), (body.pos[0]+width/2,body.pos[1]+height/2), body.radius)

    time.sleep(0.025)
    pygame.display.update()
