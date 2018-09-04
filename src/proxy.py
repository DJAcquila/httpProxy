import socket, logging 
from thread import start_new_thread
from cache import Cache
from util import *

# Configurar o logging

logging.basicConfig(filename = 'proxy.log', filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)

log = logging.getLogger('proxy')

class ServidorProxy():
	"""docstring for ServidorProxy"""
	def __init__(self):
		self.port = 54321
		self.buffer_size = 8192
		self.conexoes = 10
		self.cache = Cache(999999999)

	def start(self):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.bind(("localhost", self.port))
			sock.listen(self.conexoes)
		except Exception, e:
			print "Erro ao iniciar o servidor Proxy"
			print e
			return

		while True:
			conn, addr = sock.accept()
			data = conn.recv(self.buffer_size)
			start_new_thread(self.requestHandler, (data, conn, addr))

	def requestHandler(self, data, conn, addr):

		#Fazer o parsing da requisicao do cliente, que retorna um dicionario de dados chave-valor
		recv_data = parseHeader(data)
		response = ""
		# Nao continuar com o metodo nao implementado GET.
		if recv_data['method'] != 'GET':
			notImplementedMethod(conn)
			return

		# Recuperar url e hpst do servidor requisitado pelo cliente
		url = recv_data['url']
		host = recv_data['Host']
		log.info("Requisicao de %s para %s" % (addr, url))

		# Caso o campo 'no-cache' do cabecalho esteja evidente em 'pragma' ou 'cache-control', nao armazenar em cache
		
		if self.cache.existingUrl(url):
			# Ajustar codigo para suportar o campo If-modified-since
			if 'If-Modified-Since' in recv_data.keys():
				log.debug("[*] If-Modified-Since - Verificar objeto no servidor")
				result = getHttp(host, data, self.buffer_size)
				#log.debug("[*] If-Modified-Since - Resposta \n%s" %(result))
				parsed_result = parseServerHeader(result)

				#Caso o codigo retornado na resposta seja 304, o objeto ja esta atualizado, portanto urilizar o objeto do cache
				if parsed_result['status_code'] == '304':
					log.debug("[*] If-Modified-Since - Objeto %s Atualizado" %(url))
					log.info("Cache HIT: " + url)
					response = self.cache.getData(url)
				# Caso o codigo de retorno da resposta do servidor seja 200, o objeto estao desatualizado, pegar o objeto do servidor e adicionar ao cache
				elif parsed_result['status_code'] == '200':
					log.debug("[*] If-Modified-Since - Necessita atualizar %s" % (url))
					self.cache.update(url, result)
					response = result
					log.debug("[*] If-Modified-Since - %s Atualizado" %(url))
			else:
				# Caso nao tenha o campo If-Modified-Since, apenas puxa o elemento do cache
				log.info("Cache HIT: " + url)
				response = self.cache.getData(url)
		else:
			log.info("Cache MISS: "+ url)
			
			if 'Cache-Control' in recv_data.keys() and recv_data['Cache-Control'] == 'no-cache':
				log.info("Cache-Control - 'no-cache'")
				response = getHttp(host, data, self.buffer_size)
			else:
				response = getHttp(host, data, self.buffer_size)
				self.cache.cachePush(url, response)

		conn.send(response)
		conn.close()