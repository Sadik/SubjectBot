class EventFrame:
	"""Frame for an event"""
	def __init__(self, id=0):
		self.id = id
		self.what = None
		self.where = None
		self.date = None
		self.time = None
		self.participants = set()
		self.costs = None

	def summary(self):
		template = """Action: {action}\nOrt: {where}\nTag: {date}\nUhrzeit: {time} Uhr\nTeilnehmer: {participants}\n"""
		summary_string = template.format(
			action = self.what,
			where = self.where,
			date = self.date,
			time = self.time,
			participants = self.participants
		)

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

	def remove_participants(self, human_name):
		if (human_name in self.participants):
			self.participants.remove(human_name)

	@staticmethod
	def readable_frame_list(frame_list):
		text = ""
		for frame in frame_list:
			text += frame.summary() + "\n"

		return text

