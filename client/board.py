from color import *
from draw import *
from player import *

class BoardScreen(Viewer):
	def __init__(self, owner, player):
		self.player = player
		super().__init__(owner, self.player.board_height + 2, 2 * self.player.board_width + 4)
		self.selected = []
		curses.halfdelay(1)
		self.cursor_x = 0
		self.cursor_y = 0
		self.cursor_blink = 0
		self.selected_blink = 0

	def draw(self):
		self.__updateSize()
		self.scr.clear()

		drawBorder(self.scr, 0, 0, self.height, self.width // 2, curses.color_pair(0))
		self.__draw_map()
		self.__draw_cursor()

	def __draw_map(self):
		selected_blink = (self.selected_blink // 1) % 2
		for y in range(self.player.board_height):
			for x in range(self.player.board_width):
				cell = self.player.board[y][x]
				if (x, y) in self.selected:
					if cell == 0 or selected_blink == 0:
						self.scr.addstr(y + 1, 2 * x + 2, "██", Color.GRAY.as_curses())
						continue
				if cell != 0:
					self.scr.addstr(y + 1, 2 * x + 2, "██", Color.from_any(cell).lighten().as_curses())

	def __draw_cursor(self):
		cursor_blink = (self.cursor_blink // 4) % 2
		if cursor_blink == 1:
			return
		self.scr.addstr(self.cursor_y + 1, 2 * self.cursor_x + 2, "██", Color.WHITE.as_curses())


	def handleInput(self, ch):
		move_x = 0
		move_y = 0

		if ch == ord('q'):
			self.owner.content = None
			self.owner.closed = True
		elif ch == ord(' '):
			target = (self.cursor_x, self.cursor_y)
			if target in self.selected:
				self.selected.remove(target)
			else:
				self.selected.append(target)
		elif ch == ord('\n'):
			if len(self.selected) != 0:
				self.player.sendMove(self.selected)
				self.selected = []
		elif ch == curses.KEY_UP:
			move_y = -1
		elif ch == curses.KEY_DOWN:
			move_y = +1
		elif ch == curses.KEY_LEFT:
			move_x = -1
		elif ch == curses.KEY_RIGHT:
			move_x = +1
		if ch == -1:
			self.cursor_blink += 1
		self.selected_blink += 1
		
		if move_x != 0 or move_y != 0:
			self.__moveCursor(self.cursor_y + move_y, self.cursor_x + move_x)
			self.cursor_blink = 0


	def __moveCursor(self, y, x):
		self.cursor_x = max(0, min(x, self.player.board_width - 1))
		self.cursor_y = max(0, min(y, self.player.board_height - 1))
		self.offset_x = max(2 * self.cursor_x - self.owner.width + 9, min(self.offset_x, 2 * self.cursor_x + 2))
		self.offset_y = max(self.cursor_y - self.owner.height + 4, min(self.offset_y, self.cursor_y + 1))

		if self.width > self.owner.width - 2:
			self.offset_x = 2 * max(1, min(self.offset_x // 2, (self.width - self.owner.width + 3) // 2))
		else:
			self.offset_x = 0

		if self.height > self.owner.height - 2:
			self.offset_y = max(1, min(self.offset_y, self.height - self.owner.height + 1))
		else:
			self.offset_y = 0

	def __updateSize(self):
		if self.height != self.player.board_height or self.width != self.player.board_width:
			self.resize(self.player.board_height + 2, 2 * self.player.board_width + 4)
			self.__moveCursor(self.cursor_y, self.cursor_x)
