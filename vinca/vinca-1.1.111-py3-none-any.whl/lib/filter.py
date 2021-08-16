import re
import datetime
TODAY = datetime.date.today()

def filter(cards, pattern='', 
	   tags_include={}, tags_exclude={}, # specify a SET of tags
	   create_date_min=None, create_date_max=None,
	   seen_date_min=None, seen_date_max=None,
	   due_date_min=None, due_date_max=None,
	   editor=None, reviewer=None, scheduler=None,
	   deleted_only=False, 
	   due_only=False,
	   new_only=False,
	   invert=False):
	
	if due_only: due_date_max = TODAY
	# compile the regex pattern for faster searching
	p = re.compile(f'({pattern})')  # wrap in parens to create regex group \1

	tags_include, tags_exclude = set(tags_include), set(tags_exclude)

	f = lambda card: (((not tags_include or bool(tags_include & set(card.tags))) and
			(not tags_exclude or not bool(tags_exclude & set(card.tags))) and
			(not create_date_min or create_date_min <= card.create_date) and
			(not create_date_max or create_date_max >= card.create_date) and 
			(not seen_date_min or seen_date_min <= card.seen_date) and
			(not seen_date_max or seen_date_max >= card.seen_date) and 
			(not due_date_min or due_date_min <= card.due_date) and
			(not due_date_max or due_date_max >= card.due_date) and 
			(not editor or editor == card.editor) and
			(not reviewer or reviewer == card.reviewer) and
			(not scheduler or scheduler == card.scheduler) and
			(card.deleted or not deleted_only) and
			(not new_only or card.new) and
			(not pattern or bool(p.search(card.string)))) != # TODO invert
			invert)
	
	matches = [c for c in cards if f(c)]
	# matches.sort(key=lambda card: card.seen_date, reverse=True)

	return matches
