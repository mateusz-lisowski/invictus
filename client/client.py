from board import *
from color import *
from draw import *
from player import *

invictus_string = '''
  _____            _      _             
 |_   _|          (_)    | |            
   | |  _ ____   ___  ___| |_ _   _ ___ 
   | | | '_ \ \ / / |/ __| __| | | / __|
  _| |_| | | \ V /| | (__| |_| |_| \__ \\
 |_____|_| |_|\_/ |_|\___|\__|\__,_|___/
                                        
'''


class LoadingScreen(Viewer):
	def __init__(self, owner):
		self.counter = 0
		super().__init__(owner, 1, len("Loading...") + 1)

		curses.halfdelay(5)

	def draw(self):
		self.scr.clear()
		self.scr.addstr(0, 0, "Loading" + ("." * (self.counter % 4)))

	def handleInput(self, ch):
		if ch == -1:
			self.counter += 1
		if self.counter > 4:
			self.owner.content = BoardScreen(self.owner, Player("BLUE"))


class MenuScreen(Viewer):
	def __init__(self, owner):
		y = 0
		x = 0
		for line in invictus_string.split('\n'):
			x = max(x, len(line))
			y += 1
		super().__init__(owner, y, x + 1)

	def draw(self):
		self.scr.clear()
		self.scr.addstr(0, 0, invictus_string, curses.A_BOLD)

	def handleInput(self, _):
		self.owner.content = LoadingScreen(self.owner)
	


def main(stdscr):
	Color.init()
	curses.curs_set(0)

	menu = Menu(stdscr)
	menu.content = MenuScreen(menu)

	while not menu.closed:
		menu.draw()
		ch = stdscr.getch()
		if ch == curses.KEY_RESIZE:
			menu.updateSize()
		else:
			menu.handleInput(ch)



if __name__ == '__main__':
	curses.wrapper(main)