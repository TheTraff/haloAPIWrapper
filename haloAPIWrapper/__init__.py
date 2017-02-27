"""Halo API wrapper for use with Halo 5 and future games"""

import time
import requests

class HaloAPIResult(object):
	"""
	A wrapper class for the dicts returned by the API
	constructor takes: 
	apiResult(dict):the result returned by an API call
	"""
	def __init__(self, apiResult):
		self.apiResult = apiResult
	
	def api_result(self):
		return self.apiResult
	
	def __getattr__(self, data):
		if data in self.apiResult:
			return self.apiResult[data]
		elif "Results" in self.apiResult and data in self.apiResult["Results"][0]:
			return self.apiResult["Results"][0][data]
		else:
			return self.apiResult
		

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

		baseUrl = 'https://www.haloapi.com'
		response = requests.get(
			baseUrl + endpoint,
			params=params,
			headers=headers
			)
		self.allowance -= 1
		return response.json()
	
	def meta_request(self, endpoint, params={}, headers={}):
		"""
		base method for meta API requests
		appends ''/metadata/{gameTitle}/metadata'' to the endpoint

		endpoint(str):the desired endpoint for the result
		params(optional dict):optional parameters for some calls
		headers(optional dict):optional headers for some calls
		"""
		desiredEndpoint = '/metadata/' + self.gameTitle + '/metadata'
		desiredEndpoint = desiredEndpoint + endpoint
		return self.request(
			desiredEndpoint,
			params=params,
			headers=headers
			)
	
	def stats_request(self, endpoint, params={}, headers={}):
		"""
		base method for stat request, appends ''stats/{gameTitle}/'' to the end
		of the base URL

		endpoint(str): desired endpoint for the request
		params(optional dict): optional extra parameters for some calls
		headers(optional dict):optional headers for the call
		"""
		desiredEndpoint = "/stats/{game}".format(game=self.gameTitle) 
		desiredEndpoint = desiredEndpoint + endpoint

		response = self.request(
			desiredEndpoint,
			params=params,
			headers=headers
			)
		return HaloAPIResult(response)
	
	"""
	------------------------------------------------------------------------
	Halo 5 meta request
	------------------------------------------------------------------------
	"""

	def get_campaign_missions(self):
		"""
		Returns a list of campaign missions as dicts
		"""
		response = self.meta_request('/campaign-missions')
		return [HaloAPIResult(item) for item in response]
	
	def get_commendations(self):
		"""
		returns a list of halo 5 commendations
		"""
		response = self.meta_request('/commendations')
		return [HaloAPIResult(item) for item in response]
	
	def get_csr_designations(self):
		"""
		returns a list of CSR designations
		"""
		response = self.meta_request('/csr-designations')
		return[HaloAPIResult(item) for item in response]
	
	def get_enemies(self):
		"""
		returns a list of halo 5 enemies
		"""
		response = self.meta_request('/enemies')
		return[HaloAPIResult(item) for item in response]

	def get_flexible_stats(self):
		"""
		returns a list of halo 5 flexible stats
		"""
		response = self.meta_request('/flexible-stats')
		return[HaloAPIResult(item) for item in response]
	


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
		return HaloAPIResult(response.json())
	
	def get_match_events_by_id(self, matchId):
		"""
		gets match events of the specified matchId

		matchId(str):the desired match's Id
		"""

		endpoint = '/matches/' + matchId + '/events'
		return self.stats_request(endpoint)

	def get_match_data_by_id(self, matchId, gameMode='arena'):
		"""
		gets match data from a match in the given gameMode
		
		gameMode(optional str):the deisred game mode = arena | campaign | warzone | custom
			will default to arena if not specified -BE CAREFUL-
		matchId(str):the desired match's id
		"""
		if self.gameTitle == 'hw2':
			endpoint = '/matches/' + matchId
		else:
			endpoint = '/' + gameMode + '/matches/' + matchId
		return self.stats_request(endpoint)
	
	def get_player_match_history(self, players, modes=None,start=None,count=None):	
		"""
		returns data about a player's recent matches
		max count is 25

		players(str):the gamertag of the player
		modes(optional string):the game mode match history desired
			can string mutliple game modes together with '',''
			for hw2, this is the ''matchType'' attribute
		start(optional number):indicates how many of the most recent matches to skip
		count(optional number):indicates how many matches to return
		"""
		endpoint = '/players/' + players + '/matches'
		params = {
			'modes':modes,
			'start':start,
			'count':count,
		}
		return self.stats_request(endpoint, params=params)
	
	def get_service_record(self, players, gameMode, seasonId=None):
		"""
		returns the service record data for the player
		from the specified game mode, seasonId is only used for Arena

		players(str):the gamertag of the player
			can be multiple players, just seperate with '',''
		gameMode(str):the game mode service record desired
			Arena | Campaign | Custom | Warzone
		seasonId(optional str): specifies the season of the returned results
			if not specified, the current season will be returned
		"""
		endpoint = '/servicerecords/' + gameMode + '?players=' + players
		params = {
			'seasonId':seasonId,
		}
		return self.stats_request(endpoint, params=params)
	
	def __hw2_player_request(self, endpoint, params={}):
		"""
		a request for player data for hw2

		endpoint(str):the desired endpoint for the player request
		params(optional dict):optional parameters for some calls
			currently, only match history uses this, but that is 
			covered in the same match history function for the other games
		"""
		desiredEndpoint = '/players' + endpoint
		return self.stats_request(desiredEndpoint, params=params)
	
	def get_hw2_campaign_progress(self, player):
		"""
		returns data about the player's campaign progress
		specific for hw2

		player(str):the player's gamertag
		"""
		return self.__hw2_player_request('/' + player + '/campaign-progress')
	
	def get_hw2_player_stat_summary(self, player, seasonId=None):
		"""
		returns data about the overall stat summary for the player
		only one player can be specified
		if seasonId is given, results will be of that season

		player(str):the player's gamertag
		seasonId(optional str):the optional season's Id number
		"""
		endpoint = '/' + player + '/stats'
		if seasonId:
			return self.__hw2_player_request(
				endpoint + '/seasons/' + seasonId
				).json()
		else:
			return self.__hw2_player_request(endpoint)
	
	def get_hw2_players_xp(self, players):
		"""
		returns xp and rank information for up to 6 players

		players(str):the players' gamertags
			up to 6 seperated by '','' in the same string
		"""
		return self.stats_request('/xp?players=' + players)
	







