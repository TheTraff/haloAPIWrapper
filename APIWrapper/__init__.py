"""Halo API wrapper for use with Halo 5 and future games"""

import time
import requests

class HaloAPIWrapper(object):
	"""The main class for the module
	parameters: API key: string
				gameTitle (Halo 5, Halo Wars 2, etc) : string
				will default to h5 if not presented with an argument
				rate request limit: tuple of how many requests in a time period
				will default to (10,10) if not given an argument
	"""

	def __init__(self, apiKey, gameTitle='h5', rateLimit=(10,10)):
		self.apiKey = apiKey
		self.gameTitle = gameTitle
		self.rateLimit = rateLimit

		self.allowance = rateLimit[0]
		self.lastTimeCheck = round(time.time())

	def update_rate_limit(self):
		"""
		updates the rate limit to the new vaule
		based on when the last call was
		"""
		current = round(time.time())
		timeElapse = current - self.lastTimeCheck
		self.lastTimeCheck = current
		allowance = self.allowance
		allowance += timeElapse * (self.rateLimit[0] / self.rateLimit[1])
		if allowance > self.rateLimit[0]:
			#if allowance is greater than rate limit, reduce it
			self.allowance = self.rateLimit[0]
		return allowance
	
	def can_request(self):
		"""
		returns True if a request can be made
		returns False if it will violate the ratLimit
		"""
		if self.allownce >= 1.0:
			return True
		else:
			return False

	
	def request(self, endpoint, params={}, headers={}):
		"""
		the base request function. attaches the endpoint
		to https://www.haloapi.com/
		endpoint (str): the desired endpoint for the request
		params (Optional dict): optional parameters for some calls
		headers (Optiona dict): optional header arguments
		apiKey will be appended if not present
		"""

		self.allowance = self.update_rate_limit()
		if not self.can_request:
			return "can't do that"

		if 'Ocp-Apim-Subscription-Key' not in headers:
			headers['Ocp-Apim-Subscription-Key'] = self.apiKey

		baseUrl = 'https://www.haloapi.com/'
		response = requests.get(
			baseUrl + endpoint,
			params=params,
			headers=headers
			)
		self.allowance -= 1
		return response
	
	def stats_request(self, endpoint, params={}, headers={}):
		"""
		base method for stat request, appends ''stats/{gameTitle}/'' to the end
		of the base URL

		endpoint(str): desired endpoint for the request
		params(optional dict): optional extra parameters for some calls
		headers(optional dict):optional headers for the call
		"""
		desiredEndpoint = "stats/{game}".format(game=self.gameTitle) 
		desiredEndpoint = desiredEndpoint + endpoint

		response = self.request(
			desiredEndpoint,
			params=params,
			headers=headers
			)
		return response
	
	def get_player_csr_leaderboards(self, seasonId, playlistId, count=20):
		"""
		gets the leaderboard of top players by CSR during
		the specified seasonId in the specified playlistId
		-Will always start at 0

		seasonId(str):Id of the desired season
		playlistId(str):Id of the desired playlist
		count(optional int): number of players to retrieve
		"""
		endpoint = '/player-leaderboards/csr/' + seasonId + '/'+ playlistId
		response = self.stats_request(
			endpoint,
			params={'count':count}
			)
		return response.json()
	
	def get_match_events_by_id(self, matchId):
		"""
		gets match events of the specified matchId

		matchId(str):the desired match's Id
		"""

		endpoint = '/matches/' + matchId + '/events'
		return self.stats_request(endpoint).json()

	def get_match_data_by_id(self, gameMode, matchId):
		"""
		gets match data from a match in the given gameMode
		
		gameMode(str):the deisred game mode = arena | campaign | warzone | custom
		matchId(str):the desired match's id
		"""
		ednpoint = '/' + gameMode + '/matches/' + matchId
		return self.stats_request(endpoint).json()
	
	def get_player_match_history(self, gamerTag, modes=None,start=None,count=None):
		"""returns data about a player's matches

		




halo = HaloAPIWrapper('2153dd0cd6cb4c1abf75c2e231897373')
response = halo.get_player_csr_leaderboards("54c9ee4f-d041-44ef-bd10-2c2f71edb5a4","c98949ae-60a8-43dc-85d7-0feb0b92e719",1)
print(response)
			


	
