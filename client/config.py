
__serverIp = "127.0.0.1"
__serverPort = "8080"

def serverIp():
	global __serverIp
	return __serverIp

def setServerIp(ip):
	global __serverIp
	__serverIp = ip


def serverPort():
	global __serverPort
	return __serverPort

def setServerPort(port):
	global __serverPort
	__serverPort = port
