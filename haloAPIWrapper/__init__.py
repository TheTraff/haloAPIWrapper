"""
Halo API wrapper for use with Halo 5 and future games
	meta requests: line 185
	profile requests: line 339
	stat requests: line 375
"""

import time
import requests

class Error(Exception):
	"""base class for exceptions"""
	pass

class responseError(Error):
	"""
	exception raised for any response code errors
	like 404, 503, etc
	responseCode: the code of the response error
	"""
	def __init__(self, responseCode):
		if responseCode == 400:
			self.responseCode = 'Unsupported character was entered'
		elif responseCode == 404:
			self.responseCode = 'Gamertag was not found'
		elif responseCode == 500:
			self.responseCode = 'Internal server error'
		else:
			self.responseCode = 'Something went wrong, please try again'
		self.responseCode = responseCode

class serviceRecordError(Error):
	"""
	Exception raised for service record issues
	gamerTag: the gamertag that caused the error
	message: the type of error that occured
	"""
	def __init__(self, gamerTag, resultCode):
		self.gamerTag = gamerTag
		if resultCode == 1:
			self.message = 'gamertag not found'
		elif resultCode == 2:
			self.message = 'service failure'
		else:
			self.message = 'service unavailiable'

class HaloAPIResult(object):
	"""
	A wrapper class for the dicts returned by the API
	constructor takes: 
	apiResult(dict):the result returned by an API call
	"""
	def __init__(self, apiResult):
		self.apiResult = apiResult.json()
		self.status_code = apiResult.status_code

	def api_result(self):
		if self.result_code == 200:
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

		if response.status_code != 200:
			raise responseError(response.status_code)
		return response
	
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
	
	def profile_request(self, endpoint, params={}, headers={}):
		"""
		base method for profile API requests
		appens ''/profile/{gameTitle}/profiles'' to the endpoint

		endpoint(str):the desired endpoint for the result
		params(optional dict):optional parameters for some calls
		headers(optional dict):optional headers for some calls
		"""
		desiredEnpoint = '/profile/' + self.gameTitle + '/profiles'
		desiredEnpoint = desiredEndpoint + endpoint
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
		return HaloAPIResult(response)
	
	def get_commendations(self):
		"""
		returns a list of halo 5 commendations
		"""
		response = self.meta_request('/commendations')
		return HaloAPIResult(response)

	
	def get_csr_designations(self):
		"""
		returns a list of CSR designations
		"""
		response = self.meta_request('/csr-designations')
		return HaloAPIResult(response)
	
	def get_enemies(self):
		"""
		returns a list of halo 5 enemies
		"""
		response = self.meta_request('/enemies')
		return HaloAPIResult(response)

	def get_flexible_stats(self):
		"""
		returns a list of halo 5 flexible stats
		"""
		response = self.meta_request('/flexible-stats')
		return HaloAPIResult(response)
	
	def get_game_base_variants(self):
		"""
		returns a list of halo 5 game base variants
		"""
		response = self.meta_request('/game-base-variants')
		return HaloAPIResult(response)

	def get_game_variant_by_id(self, ID):
		"""
		returns a list of game variants for the base variant
		"""
		response = self.meta_request("/game-variants/{}".format(ID))
		return HaloAPIResult(response)

	def get_impulses(self):
		"""
		returns a list of halo 5 impulses
		"""
		response = self.meta_request('/impulses')
		return HaloAPIResult(response)

	def get_map_variant_by_id(self, ID):
		"""
		returns info about a map with the passed ID
		"""
		response = self.meta_request("/map-variants/{}".format(ID))
		return HaloAPIResult(response)

	def get_maps(self):
		"""
		returns a list of halo 5 maps
		"""
		response = self.meta_request('/maps')
		return HaloAPIResult(response)

	def get_medals(self):
		"""
		returns a list of halo 5 medals
		"""
		response = self.meta_request('/medals')
		return HaloAPIResult(response)
	
	"""you're almost at the end of this section. keep going!!"""

	def get_playlists(self):
		"""
		returns a list of halo 5 playlists
		"""
		response = self.meta_request('/playlists')
		return HaloAPIResult(response)

	def get_requisition_by_id(self, ID):
		"""
		returns a halo 5 requestio with ID
		"""
		response = self.meta_request("/requisitions/{}".format(ID))
		return HaloAPIResult(response)

	def get_requisition_pack__by_id(self, ID):
		"""
		returns a halo 5 requestio with ID
		"""
		response = self.meta_request("/requisition-packs/{}".format(ID))
		return HaloAPIResult(response)

	def get_seasons(self):
		"""
		returns a list of halo 5 seasons
		"""
		response = self.meta_request('/seasons')
		return HaloAPIResult(response)

	def get_skulls(self):
		"""
		returns a list of halo 5 skulls
		"""
		response = self.meta_request('/skulls')
		return HaloAPIResult(response)

	def get_spartan_ranks(self):
		"""
		returns a list of halo 5 spartant ranks
		"""
		response = self.meta_request('/spartan-ranks')
		return HaloAPIResult(response)

	def get_team_colors(self):
		"""
		returns a list of halo 5 team colors
		"""
		response = self.meta_request('/team-colors')
		return HaloAPIResult(response)

	def get_vehicles(self):
		"""
		returns a list of halo 5 vehicles
		"""
		response = self.meta_request('/vehicles')
		return HaloAPIResult(response)

	def get_weapons(self):
		"""
		returns a list of halo 5 weapons
		"""
		response = self.meta_request('/weapons')
		return HaloAPIResult(response)
	
	"""
	-----------------------------------------
	Halo 5 profile requests
	-----------------------------------------
	"""
	
	def get_player_emblem_image(self, player, size=None):
		"""
		returns a response object containing the player's emblem image
		default size is 256, but must me one of:
			95 | 128 | 190 | 256 | 512
		player(str):the player's gamertag
		size(optional number): the size parameter for the image
		"""
		return self.profile_request(
			"/{player}/emblem".format(player=player),
			params={"size":size}
			)
	
	def get_player_spartan_image(self, player, size=None, crop=None):
		"""
		returns a response object containing the player's spartan image
		default size is 256, but must me one of:
			95 | 128 | 190 | 256 | 512
		player(str):the player's gamertag
		size(optional number): the size parameter for the image
		crop(optional str): a value that specifies the crop of the image
			must be: full | portrait
			default is full
		"""
		return self.profile_request(
			"/{player}/spartan".format(player=player),
			params= {"size":size, "crop":crop}
			)
	

	"""
	-----------------------------------------
	Halo 5 stat request
	-----------------------------------------
	"""

	"""new company api endpoints added July 14, 2017"""

	def get_company(self, companyId):
		"""
		Retrieves information about the Company. The response will contain the Company's name, status, and members.
		
		companyId(str): Id of the desired company
		"""
		endpoint = '/companies/' + companyId + '/'
		return self.stats_request(endpoint)

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
	
	def get_service_record(self, player, gameMode, seasonId=None):
		"""
		returns the service record data for the player
		from the specified game mode, seasonId is only used for Arena

		players(str):the gamertag of the player
		gameMode(str):the game mode service record desired
			Arena | Campaign | Custom | Warzone
		seasonId(optional str): specifies the season of the returned results
			if not specified, the current season will be returned
		"""
		endpoint = '/servicerecords/' + gameMode + '?players=' + player
		params = {
			'seasonId':seasonId,
		}
		response = self.stats_request(endpoint, params=params)
		if response.ResultCode != 0:
			raise serviceRecordError(player, response.ResultCode)
		return response

	
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
	







