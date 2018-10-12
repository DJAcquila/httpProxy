import socket

# Request
# GET /index.html HTTP/1.1\r\n
# Host: www-net.cs.umass.edu\r\n
# User-Agent: Firefox/3.6.10\r\n
# Accept: text/html,application/xhtml+xml\r\n
# Accept-Language: en-us,en;q=0.5\r\n
# Accept-Encoding: gzip,deflate\r\n
# Accept-Charset: ISO-8859-1,utf-8;q=0.7\r\n
# Keep-Alive: 115\r\n
# Connection: keep-alive\r\n
# \r\n

def parseHeader(data):

	print data
	# Separa a string em linhas
	linhas = data.splitlines()
	# Recupera a primeira linha
	primeira_linha = linhas[0].split(' ')
	# Coloca os resultados da primeira linha em um dicionario de dados
	resultado = {'method': primeira_linha[0], 'url': primeira_linha[1], 'version': primeira_linha[2]}
	# Percorre linha a linha (com excessao da primeira linha) e recupera as informaoes em um dicionario de dados
	for l in linhas[1:-1]:
		split = l.split(':', 1)
		resultado[split[0]] = split[1].strip()

	# retorna o dicionario de dados com a requisicao ja formatada
	return resultado

# Response
# HTTP/1.1 200 OK\r\n
# Date: Sun, 26 Sep 2010 20:09:20 GMT\r\n
# Server: Apache/2.0.52 (CentOS)\r\n
# Last-Modified: Tue, 30 Oct 2007 17:00:02 GMT\r\n
# ETag: "17dc6-a5c-bf716880"\r\n
# Accept-Ranges: bytes\r\n
# Content-Length: 2652\r\n
# Keep-Alive: timeout=10, max=100\r\n
# Connection: Keep-Alive\r\n
# Content-Type: text/html; charset=ISO-8859-1\r\n
# \r\n
# data data data data data ...
def parseServerHeader(data):
	linhas = data.splitlines()
	primeira_linha = linhas[0].split(' ')
	status_code = primeira_linha[1]
	resultado = {'version': primeira_linha[0], 'status_code': primeira_linha[1], 'status': primeira_linha[2]}

	for l in linhas[1:-1]:
		split = l.split(':', 1)
		resultado[split[0]] = split[1].strip()
	return resultado

def getHttp(url, response, buffer_size):
	response = response.replace("HTTP/1.1", "HTTP/1.0")
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((url, 80))
	sock.send(response)
	response = ""
	response_part = sock.recv(buffer_size)

	while response_part:
		if len(response_part) > 0:
			response += response_part
		else:
			break
		response_part = sock.recv(buffer_size)

	return response

def notImplementedMethod(conn):
	string = "HTTP/1.1 501 Not Implemented\n"
	string += "Date: Thu, 20 May 2004 21:12:58 GMT\n"
	string += "Connection: close\n"
	string += "Server: Python/6.6.6 (custom)\n"

	conn.send(string)

