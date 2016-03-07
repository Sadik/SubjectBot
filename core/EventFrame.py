class EventFrame:
	"""Frame for an event"""
	def __init__(self, id):
		self.id = id
		self.what = None
		self.where = None
		self.date = None
		self.time = None
		self.participants = set()
		self.costs = None

	def summary(self):
		template = """
		Action: {action}
		Ort: {where}
		Wann: {date}, {time} Uhr
		Teilnehmer: {participants}
		Kosten: {costs}"""
		summary_string = template.format(
			action = self.what,
			where = self.where,
			date = self.date,
			time = self.time,
			participants = self.participants,
			costs = self.costs)

		print(summary_string)
		return summary_string

	def add_action(self, action):#TODO: should print warning when action is not none
		self.what = action

	def add_location(self, location):
		self.where = location

	def add_time(self, time):
		self.time = time

	def add_date(self, date):
		self.date = date

	def add_costs(self, costs):
		self.costs = costs

	def add_participants(self, human_name):
		if (human_name not in self.participants):
			self.participants = self.participants | {human_name}