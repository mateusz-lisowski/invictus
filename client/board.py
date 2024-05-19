from color import *
from draw import *
from player import *

class BoardScreen(Viewer):
	def __init__(self, owner, player):
		self.player = player
		super().__init__(owner, *self.__resizeSize())
		self.owner.overlay = BoardOverlay(owner, player)
		self.selected = []
		curses.halfdelay(1)
		self.cursor_x = 0
		self.cursor_y = 0
		self.cursor_blink = 0
		self.selected_blink = 0

	def refresh(self, y, x, height, width):
		width = width - BoardOverlay.WIDTH
		if width > self.width:
			x = x + (width - self.width) // 2
		if height > self.height:
			y = y + (height - self.height) // 2
		self.scr.refresh(self.offset_y, self.offset_x, y, x, height, width)

	def draw(self):
		self.__updateSize()
		self.scr.clear()

		drawBorder(self.scr, 0, 0, self.player.board_height + 2, self.player.board_width + 2)
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
		if self.player.disconnected:
			self.owner.content = MessageScreen(self.owner, "Disconnected from the server")

		move_x = 0
		move_y = 0

		if ch == ord('q'):
			self.owner.content = None
		elif ch == ord(' '):
			target = (self.cursor_x, self.cursor_y)
			if target in self.selected:
				self.selected.remove(target)
			elif self.player.cells > len(self.selected):
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
		space_width = self.owner.width - BoardOverlay.WIDTH
		space_height = self.owner.height

		self.cursor_x = max(0, min(x, self.player.board_width - 1))
		self.cursor_y = max(0, min(y, self.player.board_height - 1))
		self.offset_x = max(2 * self.cursor_x - space_width + 9, min(self.offset_x, 2 * self.cursor_x + 2))
		self.offset_y = max(self.cursor_y - space_height + 4, min(self.offset_y, self.cursor_y + 1))

		if self.width > space_width - 2:
			self.offset_x = 2 * max(1, min(self.offset_x // 2, (self.width - space_width + 3) // 2))
		else:
			self.offset_x = 0

		if self.height > space_height - 2:
			self.offset_y = max(1, min(self.offset_y, self.height - space_height + 1))
		else:
			self.offset_y = 0

	def __updateSize(self):
		self.resize(*self.__resizeSize())
		self.__moveCursor(self.cursor_y, self.cursor_x)

	def __resizeSize(self):
		return (self.player.board_height + 2, 2 * self.player.board_width + 4)


class BoardOverlay(Viewer):
	WIDTH = 20

	def __init__(self, owner, player):
		self.player = player
		super().__init__(owner, 6, BoardOverlay.WIDTH + 1)

	def refresh(self, y, x, height, width):
		x = (x + width - BoardOverlay.WIDTH) // 2 * 2
		self.scr.refresh(self.offset_y, self.offset_x, y, x, height, width)

	def draw(self):
		if self.height != self.owner.height:
			self.resize(max(self.owner.height, 6), BoardOverlay.WIDTH + 1)
		self.scr.clear()

		fill(self.scr, 0, 0, self.height, 1, Color.GRAY)
		drawStrings(self.scr, 1, 4, BoardOverlay.WIDTH - 6, [ 
			("Color: ", None), 
			("██", Color.from_any(self.player.color).as_curses()) 
		])
		drawStrings(self.scr, 3, 4, BoardOverlay.WIDTH - 6, [ 
			(f"Cells: {self.player.cells - len(self.owner.content.selected)}", None) 
		])

		fill(self.scr, 5, 2, 1, BoardOverlay.WIDTH // 2 - 1)

		offset = 7
		for (color, score) in self.player.scores:
			if offset >= self.height:
				return
			drawStrings(self.scr, offset, 4, BoardOverlay.WIDTH - 6, [ 
				("██", Color.from_any(color).as_curses()),
				(f" {score}", None),
			])
			offset += 2
