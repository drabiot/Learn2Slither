#!/usr/bin/env -S uv run --script
import arcade
import random

SCREEN_WIDTH	= 800
SCREEN_HEIGHT	= 800
TILE_WIDTH		= 50
TILE_HEIGHT		= 50

class Snake(arcade.Window):
	"""
	Snake game structure
	"""

	def __init__(self):
		super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Snake")

		self.all_sprites = arcade.SpriteList()

		# Set Framerate
		self.set_update_rate(1 / 10)

		# Set Moveement
		self.up = self.down = self.left = self.right = False

		# Create Player texture
		self.snake_texture = arcade.make_soft_square_texture(int(SCREEN_WIDTH / TILE_WIDTH), arcade.color.LIME, 255, 255)

		# Generate Player Coordinate
		base_pos_x = random.randint(1, TILE_WIDTH)	#Set to 0
		base_pos_y = random.randint(1, TILE_HEIGHT)	#Set to 0

		if (random.randint(0, 1)):
			base_dir_x = 0
			base_dir_y = random.randint(1, 2)
			if (base_dir_y == 2):
				base_dir_y = -1
		else:
			base_dir_x = random.randint(1, 2)
			base_dir_y = 0
			if (base_dir_x == 2):
				base_dir_x = -1

		self.positions = [
    		(base_pos_x, base_pos_y), 
    		(base_pos_x - base_dir_x, base_pos_y - base_dir_y), 
    		(base_pos_x - (base_dir_x * 2), base_pos_y - (base_dir_y * 2))
		] #Create correctly the body (check if part outside the wall)
		self.direction = (base_dir_x, base_dir_y)
		self.grow = False

	def move(self):
		head_x, head_y = self.positions[0]
		delta_x, delta_y = self.direction
		new_head = (head_x + delta_x, head_y + delta_y)

		if (new_head in self.positions or not (1 <= new_head[0] <= TILE_WIDTH and 1 <= new_head[1] <= TILE_HEIGHT)):
			return False

		self.positions.insert(0, new_head)

		if (not self.grow):
			self.positions.pop()
		else:
			self.grow = False

		return True

	def grow_snake(self):
		self.grow = True

	def on_update(self, delta_time: float):
		"""Called automatically every frame by arcade to update game state"""
		if (self.up and self.direction != (0, -1)):
			self.direction = (0, 1)
		if (self.down and self.direction != (0, 1)):
			self.direction = (0, -1)
		if (self.left and self.direction != (1, 0)):
			self.direction = (-1, 0)
		if (self.right and self.direction != (-1, 0)):
			self.direction = (1, 0)

		self.move()

	def on_draw(self):
		"""
		Render the screen
		"""
		self.clear()

		# Clear sprite list each frame to prevent accumulation
		self.all_sprites.clear()

		# Render each segment of the snake
		for pos_x, pos_y in self.positions:
			center_x = pos_x * (SCREEN_WIDTH / TILE_WIDTH) - ((SCREEN_WIDTH / TILE_WIDTH) / 2)
			center_y = pos_y * (SCREEN_HEIGHT / TILE_HEIGHT) - ((SCREEN_HEIGHT / TILE_HEIGHT) / 2)

			player = arcade.Sprite(center_x=center_x, center_y=center_y)
			player.append_texture(self.snake_texture)
			player.set_texture(0)
			self.all_sprites.append(player)

		self.all_sprites.draw()

	def on_key_press(self, key, modifiers):
		"""
		Set movement on key press
		"""
		if (key == arcade.key.UP):
			self.up = True
		elif (key == arcade.key.DOWN):
			self.down = True
		elif (key == arcade.key.LEFT):
			self.left = True
		elif (key == arcade.key.RIGHT):
			self.right = True

	def on_key_release(self, key, modifiers):
		"""
		Set movement on key release
		"""
		if (key == arcade.key.UP):
			self.up = False
		elif (key == arcade.key.DOWN):
			self.down = False
		elif (key == arcade.key.LEFT):
			self.left = False
		elif (key == arcade.key.RIGHT):
			self.right = False
		

if __name__ == "__main__":
	game = Snake()
	arcade.run()
