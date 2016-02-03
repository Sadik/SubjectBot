class EventFrame:
	"""Frame for an event"""
	def __init__(self, id):
		self.id = id
		self.what = None
		self.where = None
		self.date = None
		self.time = None
		self.participants = []
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
			participants = self.participants
			costs = self.costs)
		print(summary_string)
		return summary_string