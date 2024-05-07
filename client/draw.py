import curses

def drawBorder(scr, y, x, height, width, attrib):
	for i in range(1, width - 1):
		scr.addstr(y, x + 2 * i, "▄▄", attrib)
		scr.addstr(y + height - 1, x + 2 * i, "▀▀", attrib)

	for i in range(1, height - 1):
		scr.addstr(y + i, x, " █", attrib)
		scr.addstr(y + i, x + 2 * (width - 1), "█ ", attrib)


class Viewer:
	def __init__(self, owner, height = 1, width = 1):
		curses.nocbreak()
		self.scr = curses.newpad(height, width)
		self.owner = owner
		self.width = width
		self.height = height
		self.offset_x = 0
		self.offset_y = 0

	def resize(self, height, width):
		self.scr.resize(height, width)
		self.width = width
		self.height = height

	def refresh(self, y, x, height, width):
		if width > self.width:
			x = x + (width - self.width) // 2
		if height > self.height:
			y = y + (height - self.height) // 2
		self.scr.refresh(self.offset_y, self.offset_x, y, x, height, width)


	def draw(self):
		pass

	def handleInput(self, _):
		pass


class Menu:
	def __init__(self, stdscr):
		self.stdscr = stdscr
		self.content = None
		self.updateSize()

	def updateSize(self):
		max_y, max_x = self.stdscr.getmaxyx()
		self.width = max_x
		self.height = max_y

	def draw(self):
		self.stdscr.clear()
		drawBorder(self.stdscr, 0, 0, self.height, self.width // 2, curses.color_pair(0))
		self.stdscr.refresh()
		if self.content != None:
			self.content.draw()
			self.content.refresh(1, 2, self.height - 2, self.width // 2 * 2 - 3)

	def handleInput(self, ch):
		if self.content != None:
			self.content.handleInput(ch)


class MessageScreen(Viewer):
	def __init__(self, owner, message, nextContent = None):
		self.message = message
		self.nextContent = nextContent

		y = 0
		x = 0
		for line in self.message.split('\n'):
			x = max(x, len(line))
			y += 1
		super().__init__(owner, y, x + 1)

	def draw(self):
		self.scr.clear()
		self.scr.addstr(0, 0, self.message, curses.A_BOLD)

	def handleInput(self, _):
		if self.nextContent == None:
			self.owner.content = None
		else:
			self.owner.content = self.nextContent(self.owner)