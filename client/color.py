import curses
from enum import IntEnum

class Color(IntEnum):
	DARK_BLUE		= 0b0001
	DARK_GREEN		= 0b0010
	DARK_CYAN		= 0b0001
	DARK_RED		= 0b0100
	DARK_MAGENTA	= 0b0101
	DARK_YELLOW		= 0b0110
	GRAY			= 0b0111
	BLUE			= 0b1001
	GREEN			= 0b1010
	CYAN			= 0b1001
	RED				= 0b1100
	MAGENTA			= 0b1101
	YELLOW			= 0b1110
	WHITE			= 0b1111

	def lighten(self):
		return Color(self.value | 0b1000)

	def darken(self):
		return Color(self.value & 0b0111)

	def as_curses(self):
		return curses.color_pair(Color.from_any(self))

	def init():
		if curses.can_change_color():
			for col in Color:
				intensity = col & 0b1000
				r = (255 if intensity else 128) if (col & 0b0100) else 0
				g = (255 if intensity else 128) if (col & 0b0010) else 0
				b = (255 if intensity else 128) if (col & 0b0001) else 0
				curses.init_color(col, r, g, b)
				curses.init_pair(col, col, curses.COLOR_BLACK)
		else:
			for col in Color:
				curses.init_pair(col, (col & 0b0111), curses.COLOR_BLACK)

	def from_any(col):
		if type(col) == Color:
			return col
		elif type(col) == str:
			try:
				return Color[col.upper()]
			except KeyError:
				return Color.GRAY
		else:
			return Color.GRAY
