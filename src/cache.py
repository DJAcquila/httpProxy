import socket, datetime, logging, threading

logging.basicConfig(filename = 'proxy.log', filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
log = logging.getLogger('proxy')

class Cache:
	def __init__(self, size):
		self.max = size
		self.actual_size = 0
		self.free_space = self.max
		self.cache = {}

	def free(self, n):
		self.free_space += n
		self.actual_size -= n

	def use(self, n):
		self.free_space -= n
		self.actual_size += n

	def popCache(self, url):
		self.free(len(self.cache[url]['data']))
		self.cache.pop(url)

	def update(self, url, response):
		self.popCache(url)
		self.cachePush(self, url, response)
		
	def getData(self, url):
		self.cache[url]['access_at'] = datetime.datetime.now()
		return self.cache[url]['data']

	def expiredCacheObject(self, url):
		if self.cache[url]['max-age'] == -1:
			return False
		expires_time = self.cache[key]['updated_at'] + datetime.timedelta(seconds=v['max_age'])

		if expires_time < datetime.datetime.now():
			return True
		else:
			return False

	def freeSpaceByLRUPolicy(self, size):
		while size > self.free_space or size != 0:

			least_access_time = datetime.datetime.now()
			least = None

			for url in self.cache.keys():
				if self.cache[url]['access_at'] < least_access_time:
					least = url
					least_access_time = self.cache[url]['access_at']
			if least:
				log.debug("(LRU) %s - %d bytes" %(least, len(self.cache[url]['data'])))
				self.popCache(least)

	def existingUrl(self, url):
		if url in self.cache.keys(): # Caso a url esteja armazenada no cache
			if self.expiredCacheObject(url): # Caso esteja expirada
				self.popCache(url) # Retirar do cahce
				return False # Nao esta no cache
			return True # Objeto nao expirado esta no cache
		return False # Objeto nao esta no cache

	def cachePush(self, url, response):
		response_size = len(response)
		if response_size > self.max:
			# Caso o limite de armazenamento seja ultrapassado, nao armazenar
			log.debug("Tamanho limite do cache ultrapassado: %d" % (response_size))
			return

		if response_size > self.free_space:
			# Caso nao tenha espaco no buffer, buscar objetos expirados do cache
			log.debug("Nao ha espaco sufuciente para %d bytes - A capacidade atual eh: %d" % (response_size, self.free_space))
			self.freeSpaceByLRUPolicy(response_size)
			log.debug("Apos a liberacao de espaco, temos: %d" % (self.free_space))

		self.cache[url] = {'data': response, 'update_at': datetime.datetime.now(), 'max-age': -1, 'access_at': datetime.datetime.now()}

		self.free_space -= response_size
		self.actual_size += response_size

		log.debug("%d bytes armazenados - capacidade atual: %d" % (response_size, self.free_space))


