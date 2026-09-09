#!/usr/bin/env -S uv run --script
import arcade
import random

SCREEN_WIDTH	= 800
SCREEN_HEIGHT	= 800
GRID_COLS		= 10
GRID_ROWS		= 10
TILE_SIZE_X		= SCREEN_WIDTH / GRID_COLS
TILE_SIZE_Y		= SCREEN_HEIGHT / GRID_ROWS
FPS				= 7


class GoodApple:
	"""
	A simple data holder for the apple's position + texture.
	"""

	def __init__(self, snake_positions):
		self.texture = arcade.make_soft_circle_texture(int(TILE_SIZE_X / 2), arcade.color.APPLE_GREEN, 255, 255)
		self.position = self.random_position(snake_positions)

	def random_position(self, snake_positions):
		"""
		Pick a random grid cell that isn't currently occupied by the snake.
		"""
		while True:
			position = (random.randint(1, GRID_COLS), random.randint(1, GRID_ROWS))
			if position not in snake_positions:
				return position

	def respawn(self, snake_positions):
		self.position = self.random_position(snake_positions)

class BadApple:
	"""
	A simple data holder for the apple's position + texture.
	"""

	def __init__(self, snake_positions):
		self.texture = arcade.make_soft_circle_texture(int(TILE_SIZE_X / 2), arcade.color.CANDY_APPLE_RED, 255, 255)
		self.position = self.random_position(snake_positions)

	def random_position(self, snake_positions):
		"""
		Pick a random grid cell that isn't currently occupied by the snake.
		"""
		while True:
			position = (random.randint(1, GRID_COLS), random.randint(1, GRID_ROWS))
			if position not in snake_positions:
				return position

	def respawn(self, snake_positions):
		self.position = self.random_position(snake_positions)


class Snake(arcade.Window):
	"""
	Snake game structure
	"""

	def __init__(self):
		super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Snake")

		self.all_sprites = arcade.SpriteList()

		# Checkerboard background, built once and reused every frame
		self.background_sprites = self._build_checkerboard()

		# Set Framerate
		self.set_update_rate(1 / FPS)

		# Set Movement
		self.up = self.down = self.left = self.right = False
		self.start = False
		self.game_over = False
		self.score = 0

		# Create Player texture
		self.snake_texture_even = arcade.make_soft_square_texture(int(TILE_SIZE_X), arcade.color.AIR_FORCE_BLUE, 255, 255)
		self.snake_texture_odd = arcade.make_soft_square_texture(int(TILE_SIZE_X), arcade.color.AIR_SUPERIORITY_BLUE, 255, 255)
		self.snake_head_texture = arcade.make_soft_square_texture(int(TILE_SIZE_X), arcade.color.AFRICAN_VIOLET, 255, 255)

		# Generate a valid starting body: keep retrying until every
		# segment is inside the grid and they don't overlap.
		self.positions = self._generate_start_body()
		self.direction = (0, 0)
		self.grow = False

		# Spawn two good apples (ensuring neither overlaps with the snake or each other)
		apple1 = GoodApple(self.positions)
		apple2 = GoodApple(self.positions + [apple1.position])
		self.apples = [apple1, apple2]

		# Spawn bad apple ensuring no overlap
		occupied = self.positions + [a.position for a in self.apples]
		self.bad_apple = BadApple(occupied)

	def _build_checkerboard(self):
		"""
		Build the checkerboard background once as a SpriteList
		"""
		dark_tile = (162, 209, 73)     
		light_tile = (170, 215, 81)  
		
		background = arcade.SpriteList()
		for col in range(1, GRID_COLS + 1):
			for row in range(1, GRID_ROWS + 1):
				center_x = col * TILE_SIZE_X - (TILE_SIZE_X / 2)
				center_y = row * TILE_SIZE_Y - (TILE_SIZE_Y / 2)
				color = dark_tile if (col + row) % 2 == 0 else light_tile
				tile = arcade.SpriteSolidColor(int(TILE_SIZE_X), int(TILE_SIZE_Y), color=color)
				tile.center_x = center_x
				tile.center_y = center_y
				background.append(tile)
		return background


	def _generate_start_body(self):
		"""
		Randomly pick a head position + direction and build a 3-segment
		body, retrying until the whole body fits on the grid.
		"""
		while True:
			base_pos_x = random.randint(1, GRID_COLS)
			base_pos_y = random.randint(1, GRID_ROWS)

			if random.randint(0, 1):
				base_dir_x = 0
				base_dir_y = random.choice((1, -1))
			else:
				base_dir_x = random.choice((1, -1))
				base_dir_y = 0

			positions = [
				(base_pos_x, base_pos_y),
				(base_pos_x - base_dir_x, base_pos_y - base_dir_y),
				(base_pos_x - (base_dir_x * 2), base_pos_y - (base_dir_y * 2)),
			]

			if len(set(positions)) == len(positions) and all(
				1 <= x <= GRID_COLS and 1 <= y <= GRID_ROWS for x, y in positions
			):
				return positions

	def move(self):
		head_x, head_y = self.positions[0]
		delta_x, delta_y = self.direction
		new_head = (head_x + delta_x, head_y + delta_y)

		if new_head in self.positions or not (1 <= new_head[0] <= GRID_COLS and 1 <= new_head[1] <= GRID_ROWS):
			return False

		self.positions.insert(0, new_head)

		ate_good_apple = False
		for apple in self.apples:
			if new_head == apple.position:
				self.grow_snake()
				self.score += 1
				ate_good_apple = True

				other_apples_pos = [a.position for a in self.apples if a != apple]
				occupied = self.positions + other_apples_pos + [self.bad_apple.position]
				apple.respawn(occupied)
				break

		# Bad apple: shrinks the snake and costs a point instead of growing it
		ate_bad_apple = False
		if not ate_good_apple and new_head == self.bad_apple.position:
			ate_bad_apple = True
			self.score = max(0, self.score - 1)

			occupied = self.positions + [a.position for a in self.apples]
			self.bad_apple.respawn(occupied)

		if not self.grow:
			self.positions.pop()
		else:
			self.grow = False

		# Extra shrink on top of the normal tail removal above
		if ate_bad_apple and len(self.positions) > 1:
			self.positions.pop()
		elif ate_bad_apple and len(self.positions) <= 1:
			self.game_over = True

		return True

	def grow_snake(self):
		self.grow = True

	def on_update(self, delta_time: float):
		"""
		Called automatically every frame by arcade to update game state
		"""
		if self.game_over:
			arcade.close_window()

		if self.up and self.direction != (0, -1):
			self.direction = (0, 1)
		elif self.down and self.direction != (0, 1):
			self.direction = (0, -1)
		elif self.left and self.direction != (1, 0):
			self.direction = (-1, 0)
		elif self.right and self.direction != (-1, 0):
			self.direction = (1, 0)

		if self.start and not self.move():
			self.game_over = True

	def on_draw(self):
		"""
		Render the screen
		"""
		self.clear()

		# Draw the checkerboard background first
		self.background_sprites.draw()

		# Clear sprite list each frame to prevent accumulation
		self.all_sprites.clear()

		# Render each segment of the snake
		for i, (pos_x, pos_y) in enumerate(self.positions):
			center_x = pos_x * TILE_SIZE_X - (TILE_SIZE_X / 2)
			center_y = pos_y * TILE_SIZE_Y - (TILE_SIZE_Y / 2)

			player = arcade.Sprite(center_x=center_x, center_y=center_y)
			if i == 0:
				player.append_texture(self.snake_head_texture)
			elif not i % 2:
				player.append_texture(self.snake_texture_even)
			else:
				player.append_texture(self.snake_texture_odd)
			player.set_texture(0)
			self.all_sprites.append(player)

		# Render all good apples
		for apple in self.apples:
			apple_center_x = apple.position[0] * TILE_SIZE_X - (TILE_SIZE_X / 2)
			apple_center_y = apple.position[1] * TILE_SIZE_Y - (TILE_SIZE_Y / 2)
			apple_sprite = arcade.Sprite(center_x=apple_center_x, center_y=apple_center_y)
			apple_sprite.append_texture(apple.texture)
			apple_sprite.set_texture(0)
			self.all_sprites.append(apple_sprite)

		# Render bad apple
		bad_apple_center_x = self.bad_apple.position[0] * TILE_SIZE_X - (TILE_SIZE_X / 2)
		bad_apple_center_y = self.bad_apple.position[1] * TILE_SIZE_Y - (TILE_SIZE_Y / 2)
		bad_apple_sprite = arcade.Sprite(center_x=bad_apple_center_x, center_y=bad_apple_center_y)
		bad_apple_sprite.append_texture(self.bad_apple.texture)
		bad_apple_sprite.set_texture(0)
		self.all_sprites.append(bad_apple_sprite)

		self.all_sprites.draw()

		# Score
		arcade.Text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 25, arcade.color.WHITE, 16).draw()

	def on_key_press(self, key, modifiers):
		"""
		Set movement on key press
		"""
		if self.game_over:
			return

		if not self.start and key in (arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
			self.start = True

		if key == arcade.key.UP:
			self.up = True
		elif key == arcade.key.DOWN:
			self.down = True
		elif key == arcade.key.LEFT:
			self.left = True
		elif key == arcade.key.RIGHT:
			self.right = True

	def on_key_release(self, key, modifiers):
		"""
		Set movement on key release
		"""
		if key == arcade.key.UP:
			self.up = False
		elif key == arcade.key.DOWN:
			self.down = False
		elif key == arcade.key.LEFT:
			self.left = False
		elif key == arcade.key.RIGHT:
			self.right = False


if __name__ == "__main__":
	game = Snake()
	arcade.run()