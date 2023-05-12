import pygame, math, numpy, random

"""
open licence

trail_diffuse : how much trail is blurred each step
trail_decay : percent of trail that is removed each step
trail_feed : how much trail grows each step

agent_track : density of disposed pheramone
agent_speed : distance moved each step
agent_dtheta : change in angle each step, corelated to sensors

agency_turn : random turning each step
agency_roll : the chance that direction will rotate by 'agency_spin' radians
agency_run : the chance that distance will increase by 'agency_speed' units

"""

def dist(a, b):
  return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

#window settings
size = 150
window_size = 500
scale = window_size/size
gap_fill = 0

#window init
scr = pygame.display.set_mode((window_size, window_size))
pixeldata = numpy.zeros((size-2, size-2, 3))

#the main image drawn to
canvas = numpy.zeros((size, size, 3))


#pre-bake normalized direction of each pixel to light source
normdists = numpy.zeros((size-2, size-2, 2))
lpos = [size*0.5, size*0.0]
for y in range(size-2):
  for x in range(size-2):
    normdists[x, y] = [x-lpos[0], y-lpos[1]]
    dst = dist([x, y], lpos)
    if dst!=0.0: normdists[x, y] /= dst
    else: normdists[x, y]=0.0


#program variables
clock = pygame.time.Clock()
tmp=0
running = 1

realistic=1


#PARAMS
trail_diffuse = 0.01
trail_decay = 0.1
trail_feed = 0.12


sensor_angle = 0.8
sensor_length = 2.0


agent_track = 0.1
agent_speed = 1.2
agent_dtheta = 1.0


agency_turn = 0.0
agency_roll = 0.1
agency_spin = 3.15926*0.25
agency_run = 0.001
agency_speed = -10.0


agents = []
agent_count = 1000
for i in range(agent_count):
    pt = random.random()*2.0*3.14159 #direction
    rd = random.random()*10
    px, py = math.cos(pt)*rd, math.sin(pt)*rd
    pt+=random.random()*30
    agents.append([px+size*0.5, py+size*0.5, pt])


weight = [1/8, 1/8, -1.0]

def laplace(x):
    #center
    delsqd = x[1:size-1, 1:size-1]*weight[2]

    #direct
    delsqd += (x[0:size-2, 1:size-1]+
                x[2:size, 1:size-1]+
                x[1:size-1, 0:size-2]+
                x[1:size-1, 2:size])*weight[0]
    #diagonal
    delsqd +=  (x[0:size-2, 0:size-2]+
                x[0:size-2, 2:size]+
                x[2:size, 0:size-2]+
                x[2:size, 2:size])*weight[1]

    return delsqd
    
def blur(a, dt):
    a[1:size-1, 1:size-1] += laplace(a)*dt

while running: #gameloop
    pygame.display.set_caption(str(round(clock.get_fps(), 3)))
        
    #program inputs
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running = 0
      
    #simulation step
    
    for i in agents:
       
        sns_a = canvas[max(0, min(size-1, math.floor(math.cos(i[2]-sensor_angle)*sensor_length+i[0]))),
                       max(0, min(size-1, math.floor(math.sin(i[2]-sensor_angle)*sensor_length+i[1]))), 1]

        sns_b = canvas[max(0, min(size-1, math.floor(math.cos(i[2])*sensor_length+i[0]))),
                       max(0, min(size-1, math.floor(math.sin(i[2])*sensor_length+i[1]))), 1]

        sns_c = canvas[max(0, min(size-1, math.floor(math.cos(i[2]+sensor_angle)*sensor_length+i[0]))),
                       max(0, min(size-1, math.floor(math.sin(i[2]+sensor_angle)*sensor_length+i[1]))), 1]

        turn = 0
        
        if sns_b>(sns_a+sns_c)*0.5:
            turn = 0
        elif sns_a>(sns_b+sns_c)*0.5:
            turn = -1
        elif sns_c>(sns_a+sns_b)*0.5:
            turn = 1
        else:
            #power is the sharpness of turn
            turn = (2.0*(random.random()-0.5))**3

        
        i[2]+=turn*agent_dtheta

        i[2] += agency_turn*2.0*(random.random()-0.5)

        if (random.random()<agency_roll):
            i[2] += agency_spin*(2.0*(random.random()<0.5)-1)

        boost = 1+(random.random()<agency_run)*agency_speed
        
        i[0]+=math.cos(i[2])*agent_speed*boost
        i[1]+=math.sin(i[2])*agent_speed*boost
        
        i[0]%=size
        i[1]%=size

        canvas[math.floor(i[0]), math.floor(i[1])] += (1.0-canvas[math.floor(i[0]), math.floor(i[1])])*agent_track

    #update trail
    blur(canvas, trail_diffuse)
    canvas += canvas*-trail_decay + (1-canvas)*canvas*trail_feed

    
    #fix wrapping
    canvas[0, 0] = canvas[size-2, size-2]
    canvas[0, size-1] = canvas[size-2, 1]
    canvas[size-1, 0] = canvas[1, size-2]
    canvas[size-1, size-1] = canvas[1, 1]
    canvas[0]=canvas[size-2]
    canvas[size-1]=canvas[1]
    canvas[0:size-1, 0]=canvas[0:size-1, size-2]
    canvas[0:size-1, size-1]=canvas[0:size-1, 1]
    
    #program todo loop code
    pixeldata = canvas[1:size-1, 1:size-1]*1.0
    if realistic:
        bumpmap = canvas[1:size-1, 1:size-1]*1.0

        #r, g = difference of canvas over x and y
        bumpmap[1:size-2, 0:size, 0] -= bumpmap[0:size-3, 0:size, 0]
        bumpmap[0:size, 1:size-2, 1] -= bumpmap[0:size, 0:size-3, 1]

        #calculate dot product with vector pointing at light, store in blue channel
        bumpmap[0:size, 0:size, 0] *= normdists[0:size, 0:size, 0]
        bumpmap[0:size, 0:size, 1] *= normdists[0:size, 0:size, 1]
        bumpmap[0:size, 0:size, 2] = bumpmap[0:size, 0:size, 0]+bumpmap[0:size, 0:size, 1]

        #copy product into red and green channels
        bumpmap[0:size, 0:size, 0] = bumpmap[0:size, 0:size, 2]*1.0
        bumpmap[0:size, 0:size, 1] = bumpmap[0:size, 0:size, 2]*1.0

        #color canvas
        pixeldata = (1-pixeldata)*[0.3, 0.6, 0.7] + pixeldata*[1, 0.8, 0]

        #diffuse lighting
        pixeldata += bumpmap*0.6

        #simulate specular lighting by clipping values<0
        pixeldata += numpy.clip(bumpmap, 0.0, 1.0)*0.8
        
    pixeldata = numpy.clip(pixeldata, 0.0, 1.0)
    surf = pygame.surfarray.make_surface(pixeldata*255)
    scr.blit(pygame.transform.smoothscale(surf, 2*[window_size]), (0, 0))
        
        
     #setup for next loop
    pygame.display.update()
    clock.tick(120)
    tmp+=1
pygame.quit()
quit()
