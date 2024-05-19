import curses
import time

def drawBorder(scr, y, x, height, width, attrib = None):
	if attrib == None:
		attrib = curses.color_pair(0)

	for i in range(1, width - 1):
		scr.addstr(y, x + 2 * i, "▄▄", attrib)
		scr.addstr(y + height - 1, x + 2 * i, "▀▀")

	for i in range(1, height - 1):
		scr.addstr(y + i, x, " █", attrib)
		scr.addstr(y + i, x + 2 * (width - 1), "█ ")

def fill(scr, y, x, height, width, attrib = None):
	for i in range(0, width):
		for j in range(0, height):
			scr.addstr(y + j, x + 2 * i, "██", curses.color_pair(0) if attrib == None else attrib)

def drawStrings(scr, y, x, max_len, strings):
	for [string, attrib] in strings:
		if max_len <= 0:
			return
		scr.addnstr(y, x, string, max_len, curses.color_pair(0) if attrib == None else attrib)
		string_len = len(string)
		max_len -= string_len
		x += string_len


class Viewer:
	def __init__(self, owner, height = 1, width = 1):
		curses.nocbreak()
		self.scr = curses.newpad(height, width)
		self.owner = owner
		self.owner.overlay = None
		self.width = width
		self.height = height
		self.offset_x = 0
		self.offset_y = 0
		self.owner.refresh()

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
		self.overlay = None
		self.updateSize()

	def updateSize(self):
		max_y, max_x = self.stdscr.getmaxyx()
		self.width = max_x
		self.height = max_y
		self.refresh()

	def draw(self):
		if self.content != None:
			self.content.draw()
			if self.overlay != None:
				self.overlay.draw()

		if self.content != None:
			self.content.refresh(1, 2, self.height - 2, self.width // 2 * 2 - 3)
			if self.overlay != None:
				self.overlay.refresh(1, 2, self.height - 2, self.width // 2 * 2 - 3)

	def handleInput(self, ch):
		if self.content != None:
			self.content.handleInput(ch)

	def refresh(self):
		self.stdscr.clear()
		drawBorder(self.stdscr, 0, 0, self.height, self.width // 2)
		self.stdscr.refresh()


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