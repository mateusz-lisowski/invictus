import threading
import os

from board import *
from color import *
from draw import *
from player import *
from config import *


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
		super().__init__(owner, invictus_string, ServerIpScreen)


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
		elif ch == ord('q'):
			self.owner.content = None
			return

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


class ServerIpScreen(Viewer):
	def __init__(self, owner):
		super().__init__(owner, 3, len(" IP: 000.000.000.000 ") + 5)
		curses.halfdelay(1)
		self.ip_cursor_blink = 0
		self.ip_cursor_position = 0
		self.first_type = True

	def draw(self):
		self.scr.clear()
		drawBorder(self.scr, 0, 0, self.height, self.width // 2, curses.color_pair(0))

		ips = serverIp().split('.')
		self.scr.addstr(1, 2, f" IP: {ips[0]:>3}.{ips[1]:>3}.{ips[2]:>3}.{ips[3]:>3} ")

		cursor_blink = (self.ip_cursor_blink // 4) % 2
		if cursor_blink == 1:
			return
		self.scr.addstr(1, 7 + 4 * self.ip_cursor_position, "███", Color.WHITE.as_curses())

	def handleInput(self, ch):
		num = ch - ord('0') if (ch >= ord('0') and ch <= ord('9')) else -1

		if ch == -1:
			self.ip_cursor_blink += 1
		elif num == -1:
			self.ip_cursor_blink = 0
		else:
			self.ip_cursor_blink = 4

		if num != -1:
			ips = serverIp().split('.')
			ip = int(ips[self.ip_cursor_position])

			if self.first_type:
				ip = 0

			ip = 10 * ip + num
			if ip >= 256:
				ip = num

			ips[self.ip_cursor_position] = str(ip)
			setServerIp(f"{ips[0]}.{ips[1]}.{ips[2]}.{ips[3]}")
			self.first_type = False

		if ch == curses.KEY_LEFT:
			self.ip_cursor_position = max(self.ip_cursor_position - 1, 0)
			self.first_type = True
		elif ch == curses.KEY_RIGHT:
			self.ip_cursor_position = min(self.ip_cursor_position + 1, 3)
			self.first_type = True
		elif ch == ord('\t'):
			self.ip_cursor_position = (self.ip_cursor_position + 1) % 4
			self.first_type = True
		elif ch == ord('\n'):
			self.owner.content = LoadingScreen(self.owner)
		elif ch == ord('q'):
			self.owner.content = None
			


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
	except KeyboardInterrupt:
		os._exit(1)