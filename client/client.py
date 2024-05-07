from board import *
from color import *
from draw import *
from player import *
import threading
import os

invictus_string = '''
  _____            _      _             
 |_   _|          (_)    | |            
   | |  _ ____   ___  ___| |_ _   _ ___ 
   | | | '_ \ \ / / |/ __| __| | | / __|
  _| |_| | | \ V /| | (__| |_| |_| \__ \\
 |_____|_| |_|\_/ |_|\___|\__|\__,_|___/
                                        
'''

class MainScreen(MessageScreen):
	def __init__(self, owner):
		super().__init__(owner, invictus_string, LoadingScreen)


class LoadingScreen(Viewer):
	def __init__(self, owner):
		self.counter = 0
		super().__init__(owner, 1, len("Loading...") + 1)

		curses.halfdelay(5)

		self.player = None
		self.load_thread = threading.Thread(target=self.__load)
		self.load_thread.start()

	def draw(self):
		self.scr.clear()
		self.scr.addstr(0, 0, "Loading" + ("." * (self.counter % 4)))

	def handleInput(self, ch):
		if ch == -1:
			self.counter += 1

		if not self.load_thread.is_alive():
			self.load_thread.join()
			if self.player == None:
				self.owner.content = MessageScreen(self.owner, "Failed to connect to the server")
			elif self.player.id == 0:
				self.owner.content = MessageScreen(self.owner, "Game is full")
			else:
				self.player.start()
				self.owner.content = BoardScreen(self.owner, self.player)			

	def __load(self):
		try:
			self.player = Player()
		except:
			pass

def main(stdscr):
	Color.init()
	curses.curs_set(0)

	menu = Menu(stdscr)

	while True:
		if menu.content == None:
			menu.content = MainScreen(menu)
		menu.draw()
		ch = stdscr.getch()
		if ch == curses.KEY_RESIZE:
			menu.updateSize()
		else:
			menu.handleInput(ch)



if __name__ == '__main__':
	try:
		curses.wrapper(main)
	except:
		os._exit(1)