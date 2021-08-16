# A dummy scheduler that always schedules for the next DAY
import datetime
TODAY = datetime.date.today()
DAY = datetime.timedelta(days=1)

def schedule(card):

	assert card.history, f'#{card.id} has no review history'

	if card.last_grade == 'create':
		card.due_date = TODAY
	if card.last_grade in ('edit','exit'):
		pass
	if card.last_grade == 'again':
		card.due_date = TODAY
	if card.last_grade == 'hard':
		card.due_date = TODAY + max(DAY, card.last_interval / 2)
	if card.last_grade == 'good':
		card.due_date = TODAY + card.last_interval * 2 + DAY
	if card.last_grade == 'easy':
		card.due_date = TODAY + card.last_interval * 3 + DAY*2

	# TODO refactor using match and case syntax in Python 3.10

