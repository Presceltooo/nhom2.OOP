import pygame
from pygame.locals import * #rut gon modun pygame, tiet kien time khi go
from pygame import mixer # them am thnah vao tro choi
import pickle
from os import path #đọc DATA


pygame.mixer.pre_init(44100, -16, 2, 512) # de tranh lag khi chay am thanh
mixer.init() # khoi tao modun
pygame.init()

clock = pygame.time.Clock() #kiem soat tan so quet
fps = 60 #lien quan den tan so quet khien nhan vat di nhanh hay cham

screen_width = 600
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height)) #dat kich thuoc tro choi
pygame.display.set_caption('Platformer')


#define font
font = pygame.font.SysFont('Bauhaus 93', 50)
font_score = pygame.font.SysFont('Bauhaus 93', 20)


#dinh nghia bien game
tile_size = 30
game_over = 0
main_menu = True
level = 0
max_levels = 7
score = 0


#tao mau
white = (255,255, 255)
red = (255, 0, 0)

# load anh
sun_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/sun.png') #notes: dung duong dan cua anh
bg_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/sky.png')
img3 = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/restart_btn.png')
restart_img = pygame.transform.scale(img3, (tile_size * 5, tile_size * 2))
img1 = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/start_btn.png')
start_img = pygame.transform.scale(img1, (tile_size * 4, tile_size * 2))
img2 = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/exit_btn.png')
exit_img = pygame.transform.scale(img2, (tile_size * 4, tile_size * 2))



#load am thanh
pygame.mixer.music.load('D:/WORKSPACE/OOP OF VJU/GAMES/music.wav')
pygame.mixer.music.play(-1, 0.0, 2500) # 2500 la phan nghin giay tre
coin_fx = pygame.mixer.Sound('D:/WORKSPACE/OOP OF VJU/GAMES/img_coin.wav') # de bien la con dung o cho khac
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('D:/WORKSPACE/OOP OF VJU/GAMES/img_jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('D:/WORKSPACE/OOP OF VJU/GAMES/img_game_over.wav')
game_over_fx.set_volume(0.5)

def draw_text(text, font, text_col, x, y):
	img = font.render(text, False, text_col) #text = nd, true, false đều đc nhug True, con lai la mau sac
	screen.blit(img, (x, y)) # dùng để vẽ 1 surface lên 1 surface khác


#func reset level
def reset_level(level):
	player.reset(60, screen_height - 78)
	blob_group.empty() # empty() de tao ra mang trong phu thuoc vao bo nho dang co, hay noi cach khac xoa di nd o map cu
	platform_group.empty()
	lava_group.empty()
	exit_group.empty()

	#load data level de tao map
	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	world = World(world_data)
	return world


class Button():
	def __init__ (self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect() #get_rect() de la toa do
		self.rect.x = x 
		self.rect.y = y 
		self.clicked = False

	def draw(self):
		action = False

		#lay vi tri cua chuot
		pos = pygame.mouse.get_pos() #cung cap toa do x, y cua chuot

		#check vi trị chuot và kiem tra click
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: # [0] la click chuot ben trai, 1 la co bam
				action = True
				self.clicked == True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		screen.blit(self.image, self.rect)

		return  action


class Player():
	def __init__(self, x, y):
		self.reset(x, y)



	def update(self, game_over):
		dx = 0 
		dy = 0
		walk_cooldown = 5
		col_thresh = 12

		if game_over == 0: #tuc game bat dau chay
			#lay phim đc bam
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False: # ngan k cho spam
				jump_fx.play()
				self.vel_y = -7
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 3
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				dx += 3
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#hoa hinh cua nhan vat
			if self.counter > walk_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images_right): #len(): dem so luong phan tu trong 1 dtuong
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			#tao tr luc
			self.vel_y += 1/3
			if self.vel_y > 8:
				self.vel_y = 8
			dy += self.vel_y

			#kiem tra va cham
			self.in_air = True
			for tile in world.tile_list:
				#kiểm tra va chạm theo hướng x
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0 
				#kiểm tra va chạm theo hướng y
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#kiểm tra nếu dưới mặt đất sẽ đc nhảy
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#kiểm tra nếu trên mặt đất tức là rơi
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False


			#va cham vs quai vat
			if pygame.sprite.spritecollide(self, blob_group, False): # ??
				game_over = -1
				game_over_fx.play()

			#va cham vs lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1
				game_over_fx.play()

			#va cham voi cua win
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1



			#kiểm tra va chạm với các platform
			for platform in platform_group:
				#va cham theo huong x
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#va cham theo huong y
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):				
					#neu o duoi platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#neu tren platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 3/5
						self.in_air = False
						dy = 0
					#di chuyển sang một bên với nền tảng
					if platform.move_x != 0:
						self.rect.x += platform.move_direction



			#update vi tri player
			self.rect.x += dx
			self.rect.y += dy



		elif game_over == -1:
			self.image = self.dead_image
			draw_text('GAME OVER!', font, red, (screen_width // 2) - 135, screen_height // 2 - 150)
			if self.rect.y > 200:
				self.rect.y -= 5


		#ve player len man hinh
		screen.blit(self.image, self.rect) #note: blit là vị trí, rect phai la 1 cap vi tri


		return game_over

	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'D:/WORKSPACE/OOP OF VJU/GAMES/guy{num}.png') #notes:"" trich dan loi noi, '' trich xuat; f de lay du lieu vao {}, roi trieu khai code 
			img_right = pygame.transform.scale(img_right, (24,48))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/ghost.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x 
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True


class World():
	def  __init__(self, data):
		self.tile_list = []

		# load anh
		dirt_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/dirt.png')
		grass_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/grass.png')
		
		row_count = 0 # bo dem hang
		for row in data:
			col_count = 0 # bo dem cot
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size)) #scale :ti le
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size #notes: col, row nhu ngang va doc
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile) 
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size)) #scale :ti le
					img_rect = img.get_rect() # rect :hinh chu nhat
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size + 12)
					blob_group.add(blob)
				if tile == 4:
					platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0) #1, 0 di chuyen ngang
					platform_group.add(platform)
				if tile == 5:
					platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1) #0, 1 di chuyen doc
					platform_group.add(platform)
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				if tile == 7:
					coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					coin_group.add(coin)
				if tile == 8:
					exit = Exit(col_count * tile_size, row_count * tile_size - 15)
					exit_group.add(exit)


				col_count += 1
			row_count += 1


	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite): #tao doi tuong di dong tren man hinh
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/blob.png')
		self.image = pygame.transform.scale(img, (tile_size * (30/35), tile_size * (30/46)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 3/5
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction # di chuyen
		self.move_counter += 3/5 #bo dem
		if abs(self.move_counter) > 25:
			self.move_direction *= -1
			self.move_counter *= -1


class Platform(pygame.sprite.Sprite):  
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/platform.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y 
		self.move_counter = 0
		self.move_direction = 3/5
		self.move_x = move_x
		self.move_y = move_y


	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 3/5
		if abs(self.move_counter) > 25:
			self.move_direction *= -1
			self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))  #Phép chia chỉ lấy phần nguyên (//)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/coin.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))  #Phép chia chỉ lấy phần nguyên (//)
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)



class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/exit.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))  #Phép chia chỉ lấy phần nguyên (//)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y



player = Player(60, screen_height - 78)

blob_group = pygame.sprite.Group() # gop vao de quan ly cap nhat, xu ly va cham
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


#create dummy coin for showing the score
score_coin = Coin(tile_size // 2, tile_size // 2) # vi tri
coin_group.add(score_coin)


#tạo xu giả để hiển thị điểm số
if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)

#tao nut bam
restart_button = Button(screen_width // 2 - 80, screen_height // 2 + 20, restart_img) # vi tri
start_button = Button(screen_width // 2 - 210, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 90, screen_height // 2, exit_img)
exit_button1 = Button(screen_width // 2 - 65, screen_height // 2 + 120, exit_img)



run = True
while run:

	clock.tick(fps)
	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (100, 100)) #note: sap xep anh nhu sap sep layer

	if main_menu == True: #note: co the if-else van chay lan luot
		if exit_button.draw(): # if thi can dung
			run = False # game se dung
		if start_button.draw():
			main_menu = False # game tiep tuc voi dieu kien false
	else:
		world.draw()

		if game_over == 0:
			blob_group.update()
			platform_group.update()
			#update score
			#check if a coin has been collected
			if pygame.sprite.spritecollide(player, coin_group, True): #player, coin_.. muon kiem tra va cham, true se xoa khoi nhom, false thì k
				score += 1
				coin_fx.play()
			draw_text('X' + str(score), font_score, white, tile_size - 6, 5)


		blob_group.draw(screen)
		platform_group.draw(screen)
		lava_group.draw(screen)
		coin_group.draw(screen)
		exit_group.draw(screen)

		game_over = player.update(game_over)

		#neu player that bai
		if game_over == -1:
			draw_text('X' + str(score), font_score, white, tile_size - 6, 5)
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0
			if exit_button1.draw():
					run = False

		#neu player hoan thanh tang choi
		if game_over == 1:
			#reset game và tao tang choi moi
			level += 1
			score = 0
			if level <= max_levels:
				world_data = []
				world = reset_level(level)
				game_over = 0
			else:
				draw_text('YOU WIN!', font, red, (screen_width // 2) - 84, screen_height // 2 - 150)
				#restart game 
				if restart_button.draw():
					level = 0
					world_data = []
					world = reset_level(level)
					game_over = 0
				if exit_button1.draw():
					run = False

	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()			

pygame.quit()