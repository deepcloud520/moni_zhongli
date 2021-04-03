import pygame as pg
import math,random as r
import time,sys
import multiprocessing as mp
from pygame.locals import *
# made in china,deepcloud
def printtext(text,font,x,y,bs,color=(255,255,255),shadow=0):
    screen = bs
    if shadow:
        image=font.render(text,True,(0,0,0))
        screen.blit(image,(x+shadow,y+shadow))
    image=font.render(text,True,color)
    screen.blit(image,(x,y))

G=0.5
PLANT_NUM=50
D=100
PLANT_MAX_radius=100
PLANT_LINE=0
# 0:PlantLine off 1:PlantLine on
PLANT_LINE_LONG=200
MODE=1
# 0:fast mode(no done) 1:slow mode
INFO_DRAW=0

window=(1200,800)
scr=pg.display.set_mode(window)
pg.display.set_caption('gave mass for radius,and not gave radius for mass')
pg.init()
bs=pg.Surface(window)
ft=pg.font.Font(None,22)
def get_d(x1,y1,x2,y2):
    dx=x1-x2
    dy=y1-y2
    return math.sqrt(dx**2+dy**2)
def target(x1,y1,x2,y2):
    dx=x2-x1
    dy=y2-y1
    return math.degrees(math.atan2(dy,dx))
def get_vec(der):
    return [math.cos(math.radians(der)),math.sin(math.radians(der))]
def boom(p1,p2):#del p2
    p1.vx=(p1.mass*p1.vx+p2.mass*p2.vx)/(p1.mass+p2.mass)
    p1.vy=(p1.mass*p1.vy+p2.mass*p2.vy)/(p1.mass+p2.mass)
    p1.mass+=p2.mass
    p1.re_radius()
class plant:
    def __init__(self,x,y,name=None,radius=None,vpos=()):
        self.x=x
        self.y=y
        self.color=(r.randint(0,255),r.randint(0,255),r.randint(0,255))
        if radius is None:
            self.radius=r.randint(40,PLANT_MAX_radius)/20
        else:    
            self.radius=radius
        self.mass=(self.radius**2)*6.28
        if name is None:
            self.name=''.join([r.choice('abcdefg12345678790-') for i in range(5)])
        else:
            self.name=name
        self.namesur=ft.render(self.name,True,(255,255,255))
        self._reinfo()
        if not vpos:
            self.vx=r.randint(-5,5)/5
            self.vy=r.randint(-5,5)/5
        else:
            self.vx=vpos[0]
            self.vy=vpos[1]
        self.lock=False
        self.alive=True
        self.lastpos=[]
    def draw(self,bs,b):
        pg.draw.circle(bs,self.color,(int(self.x-b[0]),int(self.y)-b[1]),int(self.radius),int(self.radius))
        bs.blit(self.namesur,(self.x-12-b[0],self.y-5-b[1]))
        if self.lock or not PLANT_LINE:return
        #print(self.lastpos,self.x,self.y)
        try:
            tx,ty=self.lastpos[-1]
            pg.draw.line(bs,self.color,(self.x-b[0],self.y-b[1]),(tx-b[0],ty-b[1]),2)
        except:
            return
        last=self.lastpos[-1]
        for pt in self.lastpos[-2::-1]:
            tx,ty=last
            px,py=pt
            pg.draw.line(bs,self.color,(tx-b[0],ty-b[1]),(px-b[0],py-b[1]),2)
            last=pt
    def re_radius(self):
        self.radius=math.sqrt(self.mass/6.28)
        self._reinfo()
    def _reinfo(self):
        self.infoscr=ft.render(self.name + ' mass:'+str(self.mass)+',radius:'+str(self.radius),True,self.color)
    def calc(self):
        if not self.lock:
            #if PLANT_LINE:
            self.lastpos.append((self.x,self.y))
            if len(self.lastpos)>PLANT_LINE_LONG:self.lastpos.remove(self.lastpos[0])
            self.x+=self.vx
            self.y+=self.vy
class unv:
    def __init__(self,plants):
        self.plants=plants
        self.target=plants[0]
        self.bb=[0,0]
    def _pltcalc(self,b):
        vx=0
        vy=0
        for i in self.plants:
            if b==i:continue
            d=get_d(b.x,b.y,i.x,i.y)
            if (d<=(b.radius+i.radius*0.99 if i.radius>b.radius else i.radius+b.radius*0.99)):
                if b.radius>i.radius:
                    if not b.lock:
                        boom(b,i)
                    i.alive=False
                    #self.plants.remove(i)
                else:
                    #''
                    if not i.lock:
                        boom(i,b)
                    try:
                        b.alive=False
                    #self.plants.remove(b)
                    except:
                        print(plant,b,i)
                        pass
                #''
                    pass
            if not b.alive:
                continue
            g=((G*b.mass*i.mass)/(d**2))/D/b.mass
            vt=get_vec(target(b.x,b.y,i.x,i.y))
            vt[0]*=g
            vt[1]*=g
            vx+=vt[0]
            vy+=vt[1]
        b.vx+=vx
        b.vy+=vy
        b.calc()
    def calc(self):
        vx=0
        vy=0
        ps=[]
        if MODE:
            for i in self.plants:
                #for ii in range(D):
                self._pltcalc(i)
            for i in self.plants:
                if not i.alive:
                    ps.append(i)
                    #self.plants.remove(i)
            for i in ps:
                self.plants.remove(i)
        else:
            for b in self.plants:
                p=mp.Process(target=self._pltcalc,args=[b])
                p.start()
                ps.append(p)
            for p in ps:
                p.join()
            '''
            for i in self.plants:
                if b==i:continue
                d=get_d(b.x,b.y,i.x,i.y)
                if (d<=b.radius or d<=i.radius):
                    if b.radius>i.radius:
                        if not b.lock:
                            boom(b,i)
                        self.plants.remove(i)
                    else:
                        if not i.lock:
                            boom(i,b)
                        try:
                            self.plants.remove(b)
                        except:
                            print(plant,b,i)
                            pass
                    continue
                g=(G*b.mass*i.mass)/d
                vt=get_vec(target(b.x,b.y,i.x,i.y))
                vt[0]*=g
                vt[1]*=g
                vx+=vt[0]
                vy+=vt[1]
            b.vx+=vx
            b.vy+=vy
            vx=0
            vy=0
            b.calc()
            '''
    def draw(self,bs):
        self.updata()
        self.bb[0]=int(self.target.x-window[0]/2)
        self.bb[1]=int(self.target.y-window[1]/2)
        #+' - '+str(get_d(self.target.x,self.target.y,self.plants[0].x,self.plants[0].y))
        printtext('Target: '+self.target.name,ft,500,15,bs,(50,200,50))
        for i in self.plants:
            i.draw(bs,self.bb)
        if INFO_DRAW:
            y=20
            for i in self.plants[:20]:
                bs.blit(i.infoscr,(6,y))
                y+=12
            printtext(str(len(self.plants)),ft,6,6,bs)
    def updata(self):
        if self.target not in self.plants:
            self.set_target(0)
    def set_target(self,num):
        p=self.plants[num]
        self.target=p
        self.bb[0]=p.x-window[0]//2
        self.bb[1]=p.y-window[1]//2
    def tar_last(self):
        try:
            i=self.plants.index(self.target)-1
        except:
            i=0
        if i<0:i=len(self.plants)-1
        self.set_target(i)
    def tar_next(self):
        try:
            i=self.plants.index(self.target)+1
        except:
            i=0
        if i>=len(self.plants):i=0
        self.set_target(i)
sun=plant(600,400,'187J3X1',21)
sun.re_radius()
sun.mass=1000000
sun.lock=True
lst=[]
#lst=[plant(455,400,'ssd',10,(0,0)),plant(330,400,'moon',1,(0,1))]#,plant(440,450,'ssds',5,)]
#lst=[plant(200,500,'sd',6,(10,-2.5))]#
lst.append(sun)
lst.extend([plant(r.randint(-400,1600),r.randint(-400,1200)) for i in range(PLANT_NUM)])
u=unv(lst)
u.set_target(0)
while True:
    for e in pg.event.get():
        if e.type==12:
            sys.exit()
    #time.sleep(0.001)
    key=pg.key.get_pressed()
    if key[K_SPACE] and PLANT_LINE:
        PLANT_LINE=0
        INFO_DRAW=0
        time.sleep(0.3)
    elif key[K_SPACE] and not PLANT_LINE:
        PLANT_LINE=1
        INFO_DRAW=1
        time.sleep(0.05)
    elif key[K_n]:
        u.tar_last()
    elif key[K_m]:
        u.tar_next()
    bs.fill((0,0,0))
    u.calc()
    u.draw(bs)
    scr.blit(bs,(0,0))
    pg.display.update()
                