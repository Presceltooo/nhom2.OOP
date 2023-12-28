import pygame
import pickle
from os import path


pygame.init()

clock = pygame.time.Clock()
fps = 60

#tao cua so game
tile_size = 30
cols = 20
margin = 100
screen_width = tile_size * cols
screen_height = (tile_size * cols) + margin

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Level Editor')


#load anh
sun_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/sun.png')
sun_img = pygame.transform.scale(sun_img, (tile_size, tile_size))
bg_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/sky.png')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height - margin))
dirt_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/dirt.png')
grass_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/grass.png')
blob_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/blob.png')
platform_x_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/platform_x.png')
platform_y_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/platform_y.png')
lava_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/lava.png')
coin_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/coin.png')
exit_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/exit.png')
save_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/save_btn.png')
load_img = pygame.image.load('D:/WORKSPACE/OOP OF VJU/GAMES/load_btn.png')


#dinh nghia bien game
clicked = False
level = 1

#tao mau
white = (255, 255, 255)
green = (144, 201, 120)

font = pygame.font.SysFont('Futura', 18)

#tao mao trong
world_data = []
for row in range(20):
	r = [0] * 20
	world_data.append(r)

#tạo ranh giới
for tile in range(0, 20):
	world_data[19][tile] = 2 #can 2 tao do
	world_data[0][tile] = 1
	world_data[tile][0] = 1
	world_data[tile][19] = 1

#Chức năng xuất văn bản ra màn hình
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_grid():
	for c in range(21):
		#tao dg thang
		pygame.draw.line(screen, white, (c * tile_size, 0), (c * tile_size, screen_height - margin))
		#tao duong ngang
		pygame.draw.line(screen, white, (0, c * tile_size), (screen_width, c * tile_size))


def draw_world():
	for row in range(20):
		for col in range(20):
			if world_data[row][col] > 0:
				if world_data[row][col] == 1:
					#dirt blocks
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 2:
					#grass blocks
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 3:
					#enemy blocks
					img = pygame.transform.scale(blob_img, (tile_size, int(tile_size * 0.75)))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size * 0.25)))
				if world_data[row][col] == 4:
					#horizontally moving platform
					img = pygame.transform.scale(platform_x_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 5:
					#vertically moving platform
					img = pygame.transform.scale(platform_y_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size))
				if world_data[row][col] == 6:
					#lava
					img = pygame.transform.scale(lava_img, (tile_size, tile_size // 2))
					screen.blit(img, (col * tile_size, row * tile_size + (tile_size // 2)))
				if world_data[row][col] == 7:
					#coin
					img = pygame.transform.scale(coin_img, (tile_size // 2, tile_size // 2))
					screen.blit(img, (col * tile_size + (tile_size // 4), row * tile_size + (tile_size // 4)))
				if world_data[row][col] == 8:
					#exit
					img = pygame.transform.scale(exit_img, (tile_size, int(tile_size * 1.5)))
					screen.blit(img, (col * tile_size, row * tile_size - (tile_size // 2)))



class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self):
		action = False

		#lay vi tri chuot
		pos = pygame.mouse.get_pos()

		#k tra vi tri chout va dk click
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action

#tao nut save và load
save_button = Button(screen_width // 2 - 150, screen_height - 80, save_img)
load_button = Button(screen_width // 2 + 50, screen_height - 80, load_img)

#main game loop
run = True
while run:

	clock.tick(fps)

	#draw background
	screen.fill(green)
	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (tile_size * 2, tile_size * 2))

	#load and save level
	if save_button.draw():
		#save level data
		pickle_out = open(f'level{level}_data', 'wb')
		pickle.dump(world_data, pickle_out) # nhận vào hai đối số là đối tượng mà bạn muốn thực hiện pickle và tệp mà đối tượng sẽ được lưu.
		pickle_out.close()
	if load_button.draw():
		#load in level data
		if path.exists(f'level{level}_data'):
			pickle_in = open(f'level{level}_data', 'rb')
			world_data = pickle.load(pickle_in)


	#show the grid and draw the level tiles
	draw_grid()
	draw_world()


	#hien level hien tai
	draw_text(f'Level: {level}', font, white, tile_size, screen_height - 60)
	draw_text('Press UP or DOWN to change level', font, white, tile_size, screen_height - 40)

	#xu ly su kien game
	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#nhấp chuột để thay đổi 
		if event.type == pygame.MOUSEBUTTONDOWN and clicked == False:
			clicked = True
			pos = pygame.mouse.get_pos()
			x = pos[0] // tile_size
			y = pos[1] // tile_size
			#kiểm tra xem các tọa độ có nằm trong khu vực gạch không
			if x < 20 and y < 20:
				#update tile value
				if pygame.mouse.get_pressed()[0] == 1:
					world_data[y][x] += 1
					if world_data[y][x] > 8:
						world_data[y][x] = 0
				elif pygame.mouse.get_pressed()[2] == 1:
					world_data[y][x] -= 1
					if world_data[y][x] < 0:
						world_data[y][x] = 8
		if event.type == pygame.MOUSEBUTTONUP:
			clicked = False
		#kiểm tra xem các điểm có nằm trong khu vực gạch không
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_UP:
				level += 1
			elif event.key == pygame.K_DOWN and level > 1:
				level -= 1

	#update game display window
	pygame.display.update()

pygame.quit()