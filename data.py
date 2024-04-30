import os

def data_path(path: str) -> str:
	current_dir = os.path.dirname(__file__)
	abs_path = os.path.abspath(os.path.join(current_dir, path))
	return abs_path