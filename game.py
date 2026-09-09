#!/usr/bin/env -S uv run --script
import arcade

SCEEN_WIDTH		= 800
SCREEN_HEIGHT	= 800

class Snake(arcade.Window):
	"""
	Snake game structure
	"""

	def __init__(self):
		super().__init__(SCEEN_WIDTH, SCREEN_HEIGHT, "Snake")

	def on_draw(self):
		self.clear()
		

if __name__ == "__main__":
	game = Snake()
	arcade.run()
