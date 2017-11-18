#!/usr/bin/env python

import sys, pygame, time, math, glob, random
from itertools import repeat
assert sys.version_info >= (3,4), 'This script requires at least Python 3.4'

screen_size = (900,300)
FPS = 30
gravity = (0.0, 3.0)

#
# One Run Dungeon: The Endless Runner
#

def add_vectors(vect1, vect2):
        """ Returns the sum of two vectors """
        (angle1, length1) = vect1
        (angle2, length2) = vect2
        x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
        y  = math.cos(angle1) * length1 + math.cos(angle2) * length2    
        angle  = 0.5 * math.pi - math.atan2(y, x)
        length = math.hypot(x, y)
        return (angle, length)


class World(pygame.sprite.Sprite):
        def __init__(self):
                pygame.sprite.Sprite.__init__(self)
                self.background_images = self.running_images = glob.glob("resources/background/bg*.png")
                self.background_images.sort()
                self.background = []
                w,h = screen_size
                for b in self.background_images:
                        img = pygame.image.load(b)
                        r = img.get_rect()
                        temp = [img,(0,0,w,r.height-2*h)]
                        self.background.append(temp)
                self.rect = pygame.Rect((0,0,w,h))
                self.image = pygame.Surface(self.rect.size).convert()


                
                self.image.blit(self.background[0][0], (0,0), self.background[0][1])
                self.image.blit(self.background[1][0], (0,0), self.background[1][1])
                #self.image.blit(self.background[2][0], (0,0), self.background[2][1])
                #self.image.blit(self.background[3][0], (0,0), self.background[3][1])
                #self.image.blit(self.background[4][0], (0,0), self.background[4][1])
        
        def update(self,speed):
                speedx,speedy = speed
                px,py = (0,0)
                w,h = screen_size               
                for i in range(0,len(self.background)):
                        b = self.background[i]
                        r = b[0].get_rect()
                        (x1,y1,x2,y2) = b[1]
                        #x2 = w
                        
                        x1 += px
                        x2 += px
                        y1 += py
                        y2 += py

                        #print(x1)

                        #if x2 >= r.width:
                        #        x1 = 0

                        #if x2 > r.width:
                        #        x2 = w
                        
                        
                        #while x1 > r.width:
                        #        x1 = 0#r.width
                                #x2 += r.width
                                
                        while x2 > r.width:
                                x1 = 0# r.width
                                x2 = w
                        
                        self.background[i][1] = (x1,y1,x2,y2)
                        px += speedx
                        py += speedy
                self.image.blit(self.background[0][0], (0,0), self.background[0][1])
                self.image.blit(self.background[1][0], (0,0), self.background[1][1])
                #self.image.blit(self.background[2][0], (0,0), self.background[2][1])
                #self.image.blit(self.background[3][0], (0,0), self.background[3][1])
                #self.image.blit(self.background[4][0], (0,0), self.background[4][1])

class Pillar(pygame.sprite.Sprite):
        def __init__(self, chandelier = False):
                pygame.sprite.Sprite.__init__(self)
                self.chandelier = chandelier
                if chandelier:
                        self.image = pygame.image.load("resources/background/chandelier.png")
                        self.rect = self.image.get_rect()
                        self.rect.x = 700
                else:
                        self.image = pygame.image.load("resources/background/GreenPillar.png")
                        self.rect = self.image.get_rect()
                        self.rect.x = 1000
                
                #self.rect.y = 220
                

        def update(self, speed):
                speedx,speedy = speed
                if not self.chandelier:
                        speedx = speedx * 1.25
                self.rect.x -= speedx
                if random.randrange(0, FPS * 5) == 0:
                        self.reset()

        def reset(self):
                if self.rect.x < -150:
                        self.rect.x = 1100
                
class Hole(pygame.sprite.Sprite):
        def __init__(self):
                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.image.load("resources/obstacle/GreenHole.png")
                self.rect = self.image.get_rect()

                self.rect.y = 220
                self.rect.x = 500

        def update(self, speed):
                speedx,speedy = speed
                self.rect.x -= speedx
                self.reset()

        def reset(self):
                if self.rect.x < -150:
                        self.rect.x = random.randrange(1000, 2000)

class Player(pygame.sprite.Sprite):        
        def __init__(self, goblin = False, startingPosx = 50, jumpForce = 15):
                pygame.sprite.Sprite.__init__(self)
                self.goblin = goblin
                self.jumpForce = jumpForce
                if goblin:
                        self.running_images = glob.glob("resources/character/goblinRunAttack_*.png")
                else:
                        self.running_images = glob.glob("resources/character/wizardRun_*.png")
                self.running_images.sort()
                self.running = []
                for r in self.running_images:
                        temp = pygame.image.load(r)
                        self.running.append(temp)
                self.running_frame = 0
                self.image = self.running[self.running_frame]
                self.rect = self.image.get_rect()
                self.rect.x = startingPosx
                self.rect.y = 225
                self.originalRectY = self.rect.y
                self.speed = (10,0)
                self.normalSpeed = (10,0)
                self.sprintSpeed = (15, 0)
                self.falling = False
                self.dead = False
                self.sprint = False
                self.jumpDecay = 1

                self.timesDodged = 0                

                self.dy = 0

                self.last_update = pygame.time.get_ticks()

        
        def update(self, speed = (0, 0)):
                if not self.dead:
                        now = pygame.time.get_ticks()
                        if now - self.last_update > FPS * 2:
                                self.last_update = now
                                self.running_frame = (self.running_frame + 1) % len(self.running)
                                self.image = self.running[self.running_frame]

                        if self.sprint:
                                self.speed = self.sprintSpeed
                                pygame.mixer.Sound("worldflip.ogg").play()
                        else:
                                self.speed = self.normalSpeed
                else:
                        self.speed = (0, 0)
                        self.image = pygame.image.load("resources/character/wizardDie.png")

                self.rect.centery += self.dy
                if self.rect.y < self.originalRectY:
                        self.dy += self.jumpDecay
                if self.rect.y > self.originalRectY and not self.falling:
                        self.rect.y = self.originalRectY
                        self.dy = 0

                if self.goblin:
                        speedx,speedy = speed
                        self.rect.x -= speedx
                        self.reset()
                        self.jump()
                        
                #if self.falling:
                #        self.speed = add_vectors(self.speed,gravity)

        def jump(self):
                if not self.dead:
                        if self.rect.y == self.originalRectY:
                                self.dy -= self.jumpForce
                                if not self.goblin:
                                        pygame.mixer.Sound("shoot.ogg").play()

        def reset(self):
                if self.rect.x < -150:
                        self.rect.x = random.randrange(1000, 2000)
                        self.timesDodged += 1
        
# this function creates our shake-generator
# it "moves" the screen to the left and right
# three times by yielding (-5, 0), (-10, 0),
# ... (-20, 0), (-15, 0) ... (20, 0) three times,
# then keeps yieling (0, 0)
def shake():
	s = -1
	for _ in range(0, 3):
		for x in range(0, 20, 5):
			yield (x*s, 0)
		for x in range(20, 0, 5):
			yield (x*s, 0)
		s *= -1
	while True:
		yield (0, 0)

def main():
        pygame.init()
        screen = pygame.display.set_mode(screen_size)
        clock = pygame.time.Clock()

        org_screen = pygame.display.set_mode(screen_size)
        screen = org_screen.copy()
        # 'offset' will be our generator that produces the offset
        # in the beginning of screen shake, we start with a generator that 
        # yields (0, 0) forever
        offset = repeat((0, 0))

        """
        screen.fill((0,0,0))
        fadeSurface = screen.copy()
        for i in range(255):
            fadeSurface.set_alpha(i)
            screen.blit(fadeSurface, (0,0))
            pygame.display.flip()
            clock.tick(60)
        """

        if not pygame.mixer:
                pygame.mixer.init(frequency=ogg.info.sample_rate)
        pygame.mixer.stop()
        pygame.mixer.Sound("One-Run-Theme.ogg").play(-1)
        pygame.mixer.Sound("roofloop_mixdown.ogg").play(-1)

        world = pygame.sprite.Group()
        world.add(World())
        
        player = Player()
        players = pygame.sprite.Group()
        players.add(player)

        goblin = Player(True, 2500, 20)
        goblins = pygame.sprite.Group()
        goblins.add(goblin)

        chandelier = Pillar(True)
        chandeliers = pygame.sprite.Group()
        chandeliers.add(chandelier)

        pillar = Pillar()
        pillars = pygame.sprite.Group()
        pillars.add(pillar)

        hole = Hole()
        holes = pygame.sprite.Group()
        holes.add(hole)

        keepPlaying = True

        while keepPlaying:
                clock.tick(FPS)
                screen.fill((0,0,0))
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                pygame.quit()
                                sys.exit(0)
                        if event.type == pygame.MOUSEMOTION:
                                pos = pygame.mouse.get_pos()
                        if event.type == pygame.MOUSEBUTTONUP:
                                pos = pygame.mouse.get_pos()
                                player.sprint = False
                                if player.dead:
                                        keepPlaying = False
                        if event.type == pygame.MOUSEBUTTONDOWN:
                                pos = pygame.mouse.get_pos()
                                player.sprint = True
                        if event.type == pygame.KEYDOWN:
                                keys = pygame.key.get_pressed()
                                player.jump()
                                if player.dead:
                                        keepPlaying = False

                if player.rect.centerx > hole.rect.x and player.rect.centerx < (hole.rect.x + hole.rect.width):
                        if player.rect.y == player.originalRectY:
                                player.falling = True
                                player.dead = True
                                player.dy = 15
                                pygame.mixer.Sound("grndpnd.ogg").play()
                                offset = shake() #create a new shake-generator
                                org_screen.blit(screen, next(offset))
                                
                if (goblin.rect.centerx > player.rect.x and goblin.rect.centerx < player.rect.x + player.rect.width) and (goblin.rect.centery > player.rect.y and goblin.rect.centery < player.rect.y + player.rect.height):
                        player.dead = True
                        pygame.mixer.Sound("Phit.ogg").play()
                        pygame.mixer.Sound("Ouches.ogg").play()
                        offset = shake() #create a new shake-generator
                        org_screen.blit(screen, next(offset))

                if goblin.rect.x > (hole.rect.x - 50) and (goblin.rect.x + goblin.rect.width) < (hole.rect.x + hole.rect.width + 50):
                        goblin.rect.x += 350


                world.update(player.speed)
                world.draw(screen)

                holes.update(player.speed)
                holes.draw(screen)

                players.update()
                players.draw(screen)

                goblins.update(player.speed)
                goblins.draw(screen)

                chandeliers.update(player.speed)
                chandeliers.draw(screen)

                pillars.update(player.speed)
                pillars.draw(screen)

                org_screen.blit(screen, next(offset))

                pygame.display.flip()

if __name__ == '__main__':
        while True:
                main()
