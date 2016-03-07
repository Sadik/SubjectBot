class EventFrame:
	"""Frame for an event"""
	def __init__(self, id):
		self.id = id
		self.what = None
		self.where = None
		self.date = None
		self.time = None
		self.participants = {}
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

	def add_action(action):
		self.what = action

	def add_location(location):
		self.where = location

	def add_time(time):
		self.time = time

	def add_date(date):
		self.date = date

	def add_costs(costs):
		self.costs = costs

	def add_participants(human_name):
		if (human_name not in self.participants):
			self.participants.add(human_name)