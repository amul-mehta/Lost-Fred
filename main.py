import pygame
import tmx

ncoins=0
stri= ''
Exit=False

class Coin(pygame.sprite.Sprite):
    def __init__(self, location, *groups):
        super(Coin, self).__init__(*groups)
        self.image = pygame.image.load('res/coin.png')
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        
    def update(self, dt, level):
        if pygame.sprite.spritecollide(level.player,level.coins, True):
            global ncoins
            ncoins = ncoins + 1
            level.coinsound.play()
           
class Enemy(pygame.sprite.Sprite):
    def __init__(self, location,  dire, intensity, *groups):
        super(Enemy, self).__init__(*groups)
        self.image = pygame.image.load('res/enemy.png')
        self.greenl = pygame.image.load('res/greenleft.png')
        self.greenr = pygame.image.load('res/greenright.png')
        self.bluel = pygame.image.load('res/blueleft.png')
        self.bluer = pygame.image.load('res/blueright.png')
        self.redl = pygame.image.load('res/redleft.png')
        self.redr = pygame.image.load('res/enemy.png')
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.direction = dire
        self.inten=intensity
         
    def update(self, dt, level):
                 
        self.rect.x += self.direction * 100 * dt
        for cell in level.tilemap.layers['triggers'].collide(self.rect, 'endp'):
            if self.direction > 0:
                self.rect.right = cell.left
            else:
                self.rect.left = cell.right
            self.direction *= -1
            break

        if self.direction > 0 and self.inten == 1:
            self.image=self.greenr
        elif self.direction < 0 and self.inten == 1:
            self.image=self.greenl    
        elif self.direction > 0 and self.inten == 2:
            self.image=self.bluer
        elif self.direction < 0 and self.inten == 2:
            self.image=self.bluel
        elif self.direction > 0 and self.inten == 3:
            self.image=self.redr
        elif self.direction < 0 and self.inten == 3:
            self.image=self.redl         
        
        if self.rect.colliderect(level.player.rect):
            level.player.is_dead = True
            global Exit
            Exit=True
            level.govr.play()

class Player(pygame.sprite.Sprite):
    def __init__(self, location, *groups):
        super(Player, self).__init__(*groups)
        #self.image = pygame.image.load('player.png')
        self.p_right=pygame.image.load('res/fredr.png')
        self.p_left=pygame.image.load('res/fredl.png')
        self.image=self.p_right
        self.rect = pygame.rect.Rect(location, self.image.get_size())
        self.resting = False
        self.dy = 0
        self.is_dead = False
        self.won=False
        self.direction = 1
        
    def update(self, dt, level):  
        last = self.rect.copy()

        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.rect.x -= 300 * dt
            self.image = self.p_left
            self.direction = -1
        if key[pygame.K_RIGHT]:
            self.rect.x += 300 * dt
            self.image = self.p_right
            self.direction = 1
        if self.resting and key[pygame.K_SPACE]:
            self.dy = -500
            level.jump.play()
        
        self.dy = min(400, self.dy + 40)

        self.rect.y += self.dy * dt

        new = self.rect
        self.resting = False


        for cell in level.tilemap.layers['triggers'].collide(new, 'blockers'):
            if last.right <= cell.left and new.right > cell.left:
                new.right = cell.left
            if last.left >= cell.right and new.left < cell.right:
                new.left = cell.right
            if last.bottom <= cell.top and new.bottom > cell.top:
                self.resting = True
                new.bottom = cell.top
                self.dy = 0
            if last.top >= cell.bottom and new.top < cell.bottom:
                new.top = cell.bottom
                self.dy = 0
            
        for celln in level.tilemap.layers['triggers'].collide(new, 'ground'):    
            if last.bottom <= celln.top and new.bottom > celln.top:
                self.is_dead=True 
                global Exit
                Exit=True 
                level.govr.play() 

        for cell in level.tilemap.layers['triggers'].collide(new, 'end'):
            if last.right <= cell.left and new.right > cell.left:
                self.won=True
            if last.left >= cell.right and new.left < cell.right:
                self.won=True
            if last.bottom <= cell.top and new.bottom > cell.top:
                self.won=True
            if last.top >= cell.bottom and new.top < cell.bottom:
                self.won=True
            level.door.play() 
            
        level.tilemap.set_focus(new.x, new.y)


class Level1(object):
    def main(self, screen,myfont,clock):
        self.jump = pygame.mixer.Sound('res/jump.ogg')
        self.door = pygame.mixer.Sound('res/win.wav')
        self.govr = pygame.mixer.Sound('res/go.ogg')
        self.coinsound = pygame.mixer.Sound('res/coin.wav')

        self.tilemap = tmx.load('res/initial2.tmx', screen.get_size()) #.tmx file and View Port       
        self.sprites = tmx.SpriteLayer()
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tilemap.layers.append(self.sprites)
        self.coins = tmx.SpriteLayer()
        
        for coin in self.tilemap.layers['triggers'].find('coin'):
            Coin((coin.px, coin.py), self.coins)
    
        self.tilemap.layers.append(self.coins)
        self.enemies = tmx.SpriteLayer()
        
        for enemy in self.tilemap.layers['triggers'].find('enemy1'):
            Enemy((enemy.px, enemy.py), 1,1, self.enemies)

        for enemy in self.tilemap.layers['triggers'].find('enemy2'):
            Enemy((enemy.px, enemy.py), 1, 2,self.enemies)

        for enemy in self.tilemap.layers['triggers'].find('enemy3'):
            Enemy((enemy.px, enemy.py), 1, 3,self.enemies)

        self.tilemap.layers.append(self.enemies)

        while 1:

            dt = clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    global Exit
                    Exit=True
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE :
                    global Exit
                    Exit=True
                    return False

            if self.player.is_dead != True and self.player.won != True:
                    self.tilemap.update(dt / 1000., self)
                    stri="Score : " + str(ncoins)
                    label = myfont.render(stri, True, (0,0,0))
                    score=pygame.image.load('res/score.png')
                    self.tilemap.draw(screen)
                    screen.blit(score,(2,0))
                    screen.blit(label,(10,2))
                    pygame.display.flip()

            if self.player.is_dead:
                return False

            if self.player.won:
                return True
        
class Level2(object):
    def main(self, screen,myfont,clock):
        self.jump = pygame.mixer.Sound('res/jump.ogg')
        self.door = pygame.mixer.Sound('res/win.wav')
        self.govr = pygame.mixer.Sound('res/go.ogg')
        self.coinsound = pygame.mixer.Sound('res/coin.wav')

        self.tilemap = tmx.load('res/lvl3.tmx', screen.get_size()) #.tmx file and View Port       
        self.sprites = tmx.SpriteLayer()
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tilemap.layers.append(self.sprites)
        self.coins = tmx.SpriteLayer()
        
        for coin in self.tilemap.layers['triggers'].find('coin'):
            Coin((coin.px, coin.py), self.coins)
        self.tilemap.layers.append(self.coins)
        self.enemies = tmx.SpriteLayer()
        for enemy in self.tilemap.layers['triggers'].find('enemy1'):
            Enemy((enemy.px, enemy.py), 1,1, self.enemies)

        for enemy in self.tilemap.layers['triggers'].find('enemy2'):
            Enemy((enemy.px, enemy.py), 1, 2,self.enemies)

        for enemy in self.tilemap.layers['triggers'].find('enemy3'):
            Enemy((enemy.px, enemy.py), 1, 3,self.enemies)

        self.tilemap.layers.append(self.enemies)

        while 1:

            dt = clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    global Exit
                    Exit=True
                    return
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    global Exit
                    Exit=True
                    return

            if self.player.is_dead != True and self.player.won != True:
                self.tilemap.update(dt / 1000., self)
                stri="Score : " + str(ncoins)
                label = myfont.render(stri, True, (0,0,0))
                self.tilemap.draw(screen)
                score=pygame.image.load('res/score.png')
                screen.blit(score,(2,0))
                screen.blit(label,(10,2))
                pygame.display.flip()

            if self.player.is_dead:
                global Exit
                Exit=True
                return False

            if self.player.won:
                return True
        
class Level3(object):
    def main(self, screen,myfont,clock):
        self.jump = pygame.mixer.Sound('res/jump.ogg')
        self.door = pygame.mixer.Sound('res/win.wav')
        self.govr = pygame.mixer.Sound('res/go.ogg')
        self.coinsound = pygame.mixer.Sound('res/coin.wav')

        self.tilemap = tmx.load('res/initial3.tmx', screen.get_size()) #.tmx file and View Port       
        self.sprites = tmx.SpriteLayer()
        start_cell = self.tilemap.layers['triggers'].find('player')[0]
        self.player = Player((start_cell.px, start_cell.py), self.sprites)
        self.tilemap.layers.append(self.sprites)
        self.coins = tmx.SpriteLayer()
        for coin in self.tilemap.layers['triggers'].find('coin'):
            Coin((coin.px, coin.py), self.coins)
        self.tilemap.layers.append(self.coins)
        self.enemies = tmx.SpriteLayer()
        for enemy in self.tilemap.layers['triggers'].find('enemy1'):
            Enemy((enemy.px, enemy.py), 1,1, self.enemies)

        for enemy in self.tilemap.layers['triggers'].find('enemy2'):
            Enemy((enemy.px, enemy.py), 1, 2,self.enemies)

        for enemy in self.tilemap.layers['triggers'].find('enemy3'):
            Enemy((enemy.px, enemy.py), 1, 3,self.enemies)

        self.tilemap.layers.append(self.enemies)

        while 1:

            dt = clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    global Exit
                    Exit=True
                    return
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    global Exit
                    Exit=True
                    return

            if self.player.is_dead != True and self.player.won != True:
                self.tilemap.update(dt / 1000., self)
                stri="Score : " + str(ncoins)
                label = myfont.render(stri, True, (0,0,0))
                self.tilemap.draw(screen)
                score=pygame.image.load('res/score.png')
                screen.blit(score,(2,0))
                screen.blit(label,(10,2))
                pygame.display.flip()

            if self.player.is_dead:
                return False

            if self.player.won:
                return True
        
class Level(object):
    def main(self, screen,myfont):
        clock = pygame.time.Clock()

        self.over = False
        self.stat1= False
        self.stat2= False
        self.stat3= False
        you_won=pygame.image.load('res/finish.png')
        go_back = pygame.image.load("res/go.png")
        score=pygame.image.load('res/score.png')
        
        self.jump = pygame.mixer.Sound('res/jump.ogg')
        self.door = pygame.mixer.Sound('res/win.wav')
        self.govr = pygame.mixer.Sound('res/go.ogg')
        self.coinsound = pygame.mixer.Sound('res/coin.wav')

        if self.over == False:
            self.stat1=Level1().main(screen,myfont,clock)
            screen.fill((0,0,0))  
            pygame.display.update()

        if self.stat1 == True and self.over == False:
            self.stat2 = Level2().main(screen,myfont,clock)

        if self.stat1 ==   True and self.stat2 == True and self.over == False:
            self.stat3 = Level3().main(screen,myfont,clock)
            self.over=True
            global Exit
            Exit=True

        if self.stat1 == True and self.stat2 == True and self.stat3 == True and self.over == True:
            screen.blit(you_won,(0,0))
            stri="Score : " + str(ncoins)
            label = myfont.render(stri, True, (0,0,0))
            screen.blit(label, (7,398))
            pygame.display.flip()
            key = pygame.key.get_pressed()
            if key[pygame.K_RETURN]:
                return
        else:
            screen.blit(go_back, (0, 0))
            stri="Score : " + str(ncoins)
            label=myfont.render(stri , True , (0,0,0))
            screen.blit(label, (12,407))
            pygame.display.flip()
            key = pygame.key.get_pressed()
            if key[pygame.K_ESCAPE]:
                return

class Menu(object):
    def main(self,screen,myfont):
        start_page=pygame.image.load('res/Title_final.png')
        prologue=pygame.image.load('res/Prologue.png')
        credits=pygame.image.load('res/Credits.png')
        controls=pygame.image.load('res/Controls.png')
        global Exit
        while not Exit:
            screen.blit(start_page,(0,0))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos=pygame.mouse.get_pos()
                    px=pos[0]
                    py=pos[1]
                    if px > 105 and py > 130 and px < 196 and py < 181:
                        Level().main(screen,myfont)
                        self.Wait_State()
                    elif px > 224 and py > 234 and px < 327 and py < 288:
                        screen.blit(controls, (0,0))
                        pygame.display.flip()
                        self.Wait_State()
                    elif px > 94 and py > 317 and px < 196 and py < 369:
                        screen.blit(prologue ,(0,0))
                        pygame.display.flip()
                        self.Wait_State()
                    elif px > 229 and py > 402 and px < 327 and py < 447:
                        screen.blit(credits, (0,0))
                        pygame.display.flip()
                        self.Wait_State()
                if event.type == pygame.QUIT:
                    return            
        
        return
        
    def Wait_State(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return                



if __name__ == '__main__':
    pygame.init()
    myfont = pygame.font.Font("res/game_font.ttf", 35)
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("The Lost Fred Flintstones !! :)")
    Menu().main(screen,myfont)
 
