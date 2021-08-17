class State:
	def __init__(self):
		self.turn = "black" #"black" or "white"
		self.phase = "select" #"select", "move", or "attack"
		self.prompt = SELECT_PROMPT #Describes what the current player needs to do.
		self.black = 0 #black's score
		self.white = 0 #white's score
		
		#The board represented as a 5 (orbits) x 18 (sectors) 2D array of strings.
		#Valid sector contents...
		# - empty: ""
		# - piece: "<color>#<type>"
		# - marker: "canMove", "start", or "willFall"
		# - piece and marker(s): "<color>#<type> selected", "<color>#<type> canHit", "<color>#<type> willFall", or "<color>#<type> selected willFall"
		self.board = [
			["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
			["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
			["", "", "", "white#fighter", "white#fighter", "white#fighter", "", "", "", "", "", "", "black#fighter", "black#fighter", "black#fighter", "", "", ""],
			["", "", "", "white#sweeper", "", "white#sweeper", "", "", "", "", "", "", "black#sweeper", "", "black#sweeper", "", "", ""],
			["", "", "", "white#bomber", "white#flag", "white#bomber", "", "", "", "", "", "", "black#bomber", "black#flag", "black#bomber", "", "", ""]
		]

SELECT_PROMPT = "select a piece"
INVALID_SELECT_PROMPT = "you cannot move that piece<br>select another"
MOVE_PROMPT = "choose a move<br>or<br>select a different piece"
INVALID_MOVE_PROMPT = "you cannot move there<br>choose a move<br>or<br>select a different piece"
ATTACK_PROMPT = "choose an attack<br>or<br>move back<br>or<br>deselect your piece to pass"
INVALID_ATTACK_PROMPT = "you cannot attack that piece<br>choose an attack<br>or<br>move back<br>or<br>deselect your piece to pass"
BLACK_WINS_PROMPT = "black wins!"
WHITE_WINS_PROMPT = "white wins!"

FLAG_POINTS = 9
BOMBER_POINTS = 6
SWEEPER_POINTS = 4
FIGHTER_POINTS = 2
MAX_SCORE = FLAG_POINTS + 2 * BOMBER_POINTS + 2 * SWEEPER_POINTS + 3 * FIGHTER_POINTS

def process(game_state, orbit, sector):
	if isinstance(game_state, State):
		global state 
		state = game_state
	
		if state.phase == "select":
			_process_select(orbit, sector)
		elif state.phase == "move":
			_process_move(orbit, sector)
		elif state.phase == "attack":
			_process_attack(orbit, sector)

def _process_select(orbit, sector):
	state.prompt = INVALID_SELECT_PROMPT #Assume the selection is invalid unless proven valid.
	selection = state.board[orbit][sector]
	if _get_current_color_prefix() in selection: #If the selection is a piece which belongs to the active player...
		type = selection.split("#")[1]
		if _project_moves(type, orbit, sector): #If that piece is free to move...
			_mark(orbit, sector, "selected")
			state.phase = "move"
			state.prompt = MOVE_PROMPT

def _project_moves(type, orbit, sector):
	can_move = False
	
	if type == "flag":
		can_move = _project_flag_moves(orbit, sector)
	elif type == "bomber":
		can_move = _project_bomber_moves(orbit, sector)
	elif type == "sweeper":
		can_move = _project_sweeper_moves(orbit, sector)
	elif type == "fighter":
		can_move = _project_fighter_moves(orbit, sector)
		
	return can_move

def _project_flag_moves(orbit, sector):
	can_move = False
	
	clockwise = (sector + 1) % 18
	counter = (sector + 17) % 18
	
	if state.board[orbit][clockwise] == "":
		state.board[orbit][clockwise] = "canMove"
		can_move = True
	
	if state.board[orbit][counter] == "":
		state.board[orbit][counter] = "canMove"
		can_move = True
	
	return can_move

def _project_bomber_moves(orbit, sector):
	can_move = False
	
	for i in range(3):
		o = orbit - 1 + i;
		if o >= 0 and o < 5:
			for j in range(3):
				s = (sector + 17 + j) % 18
				if state.board[o][s] == "":
					state.board[o][s] = "canMove"
					can_move = True
	
	return can_move;
	
def _project_sweeper_moves(orbit, sector):
	can_move = False
	
	up = orbit + 1
	down = orbit - 1
	
	if up < 5 and state.board[up][sector] == "":
		state.board[up][sector] = "canMove"
		can_move = True
		
	if down >= 0 and state.board[down][sector] == "":
		state.board[down][sector] = "canMove"
		can_move = True
		
	for i in range(1, 18):
		clockwise = (sector + i) % 18
		if state.board[orbit][clockwise] == "":
			state.board[orbit][clockwise] = "canMove"
			can_move = True
		else:
			break;
			
	for j in range(1, 18):
		counter = (sector + 18 - j) % 18
		if state.board[orbit][counter] == "":
			state.board[orbit][counter] = "canMove"
			can_move = True
		else:
			break;
			
	return can_move
	
def _project_fighter_moves(orbit, sector):
	can_move = False
	
	for i in range(1, 5):
		up = orbit + i
		clockwise = (sector + i) % 18
		
		if up < 5 and state.board[up][clockwise] == "":
			state.board[up][clockwise] = "canMove";
			can_move = True;
		else:
			break;
	
	for i in range(1, 5):
		up = orbit + i
		counter = (sector + 18 - i) % 18
		
		if up < 5 and state.board[up][counter] == "":
			state.board[up][counter] = "canMove";
			can_move = True;
		else:
			break;
	
	for i in range(1, 5):
		down = orbit - i
		clockwise = (sector + i) % 18
		
		if down >= 0 and state.board[down][clockwise] == "":
			state.board[down][clockwise] = "canMove";
			can_move = True;
		else:
			break;
		
	for i in range(1, 5):
		down = orbit - i
		counter = (sector + 18 - i) % 18
		
		if down >= 0 and state.board[down][counter] == "":
			state.board[down][counter] = "canMove";
			can_move = True;
		else:
			break;
	
	return can_move

def _process_move(orbit, sector):
	move = state.board[orbit][sector]
	
	if "canMove" in move:
		_move_selected_to(orbit, sector)
		_project_attacks(orbit, sector)
		state.prompt = ATTACK_PROMPT
		state.phase = "attack"
		_clear_marker("canMove")
	elif _get_current_color_prefix() in move:
		_clear_marker("selected")
		_clear_marker("canMove")
		_process_select(orbit, sector)
	else:
		state.prompt = INVALID_MOVE_PROMPT

def _move_selected_to(orbit, sector):
	type = ""
	oi = -1
	si = -1
	
	for o in range(5):
		for s in range(18):
			if "selected" in state.board[o][s]:
				type = state.board[o][s].split()[0].split("#")[1]
				oi = o
				si = s
				break
	
	state.board[orbit][sector] = state.board[oi][si]
	state.board[oi][si] = "start"
	
	_clear_marker("canMove")
		
def _project_attacks(orbit, sector):
	can_attack = False
	
	type = _get_selected_value().split()[0].split("#")[1]
	
	if type == "flag":
		can_attack = _project_flag_attacks(orbit, sector)
	elif type == "bomber":
		can_attack = _project_bomber_attacks(orbit, sector)
	elif type == "sweeper":
		can_attack = _project_sweeper_attacks(orbit, sector)
	elif type == "fighter":
		can_attack = _project_fighter_attacks(orbit, sector)
		
	return can_attack

def _project_flag_attacks(orbit, sector):
	can_attack = False
	
	if _project_flag_attacks_toward(orbit, sector, 0, 1): can_attack = True
	if _project_flag_attacks_toward(orbit, sector, 0, -1): can_attack = True
	if _project_flag_attacks_toward(orbit, sector, 1, 0): can_attack = True
	if _project_flag_attacks_toward(orbit, sector, -1, 0): can_attack = True
	if _project_flag_attacks_toward(orbit, sector, 1, 1): can_attack = True
	if _project_flag_attacks_toward(orbit, sector, 1, -1): can_attack = True
	if _project_flag_attacks_toward(orbit, sector, -1, 1): can_attack = True
	if _project_flag_attacks_toward(orbit, sector, -1, -1): can_attack = True
	
	return can_attack
	
def _project_flag_attacks_toward(orbit, sector, do, ds):
	can_attack = False
	
	for i in range(1, 4):
		o = orbit + (i * do)
		s = (sector + 18 + (i * ds)) % 18
		if o > 4 or o < 0: break;
		elif state.board[o][s] != "":
			can_attack = _project_flag_attack(o, s)
			break;
			
	return can_attack
	
def _project_flag_attack(orbit, sector):
	can_attack = False
	
	if _get_opposite_color_prefix() in state.board[orbit][sector]:
		_mark(orbit, sector, "canHit")
		can_attack = True
		if orbit >= 3:
			_mark(orbit - 3, sector, "willFall")
	
	return can_attack

def _project_bomber_attacks(orbit, sector):
	can_attack = False
	
	o = orbit - 1
	while o >= 0:
		if can_attack:
			_mark(o, sector, "willFall")
		elif "#" in state.board[o][sector]:
			state.board[o][sector] = state.board[o][sector] + " canHit"
			can_attack = True
		o -= 1
	
	return can_attack
	
def _project_sweeper_attacks(orbit, sector):
	can_attack = False
	
	if state.board[(orbit + 1) % 5][sector] != "start" and state.board[(orbit + 4) % 5][sector] != "start":
	
		was_clockwise = False
		was_counter = True
	
		for i in range(1, 18):
			value = state.board[orbit][(sector + i) % 18]
			if value == "start":
				was_clockwise = True
			elif value != "":
				if was_clockwise:
					was_clockwise = False
					break
				else:
					was_counter = False
		
		_project_sweeper_attack(orbit, sector)
	
		if was_clockwise:
			counter = (sector + 17) % 18
			while state.board[orbit][counter] == "":
				if _project_sweeper_attack(orbit, counter): can_attack = True
				counter = (counter + 17) % 18
		
		if was_counter:
			clockwise = (sector + 1) % 18
			while state.board[orbit][clockwise] == "":
				if _project_sweeper_attack(orbit, clockwise): can_attack = True
				clockwise = (clockwise + 1) % 18
				
	return can_attack
	
def _project_sweeper_attack(orbit, sector):
	can_attack = False
	
	up = orbit + 1
	down = orbit - 1
	
	if up < 5 and _get_opposite_color_prefix() in state.board[up][sector]:
		_mark(up, sector, "canHit")
		if down >= 0: _mark(down, sector, "willFall")
		can_attack = True
		
	return can_attack
	
def _project_fighter_attacks(orbit, sector):
	can_attack = False
	
	first = 0
	second = 0
	
	for i in range(1, 5):
		up = orbit + i
		down = orbit - i
		clockwise = (sector + i) % 18
		counter = (sector + 18 - i) % 18
		
		if up < 5: 
			if state.board[up][clockwise] == "start":
				first = (sector + 17) % 18
				second = (sector + 16) % 18
				break
			elif state.board[up][counter] == "start":
				first = (sector + 1) % 18
				second = (sector + 2) % 18
				break
		if down >= 0:
			if state.board[down][clockwise] == "start":
				first = (sector + 17) % 18
				second = (sector + 16) % 18
				break
			elif state.board[down][counter] == "start":
				first = (sector + 1) % 18
				second = (sector + 2) % 18
				break
			
	if(_get_opposite_color_prefix() in state.board[orbit][first]):
		_mark(orbit, first, "canHit")
		if orbit > 0: _mark(orbit - 1, first, "willFall")
		can_attack = True
	elif(_get_opposite_color_prefix() in state.board[orbit][second]):
		_mark(orbit, second, "canHit")
		if orbit > 0: _mark(orbit - 1, second, "willFall")
		can_attack = True
	
	return can_attack

def _process_attack(orbit, sector):
	attack = state.board[orbit][sector]
	
	if attack == "start":
		_move_selected_to(orbit, sector)
		_clear_marker("selected")
		_clear_marker("start")
		_clear_marker("canHit")
		_clear_marker("willFall")
		_process_select(orbit, sector)
	elif "canHit" in attack:
		_process_hit(orbit, sector)
		_change_turn()
	elif "selected" in attack:
		_change_turn()
	else:	
		state.prompt = INVALID_ATTACK_PROMPT
		
def _process_hit(orbit, sector):
	type = _get_selected_value().split()[0].split("#")[1]
	
	if type == "flag":
		_drop(orbit, sector, 3)
	elif type == "bomber":
		for i in range(orbit + 1):
			_drop(orbit - i, sector, 1)
	elif type == "sweeper":
		_process_sweeper_hit(orbit, sector)
	elif type == "fighter":
		_drop(orbit, sector, 1)
		
def _process_sweeper_hit(orbit, sector):
	was_clockwise = False
	
	of, sf = _get_selected_location()
	
	s = (sf + 1) % 18
	while s != sector:
		if state.board[of][s] == "start":
			was_clockwise = True
			break
		s = (s + 1) % 18
	
	s = sf
	while s != sector:
		if "canHit" in state.board[orbit][s]:
			_drop(orbit, s, 2)
		
		if was_clockwise: 
			s = (s + 17) % 18
		else:
			s = (s + 1) % 18
		
	_drop(orbit, sector, 2)
		
def _drop(orbit, sector, fall):
	of = orbit - fall
	if of >= 0:
		final = state.board[of][sector]
		if "#" in final:
			_drop(of, sector, 1)
		state.board[of][sector] = state.board[orbit][sector]
		state.board[orbit][sector] = ""
	else:
		state.board[orbit][sector] = ""
	
def _change_turn():
	_score()
	
	if state.black % 2 == 1:
		state.phase = "win"
		state.prompt = BLACK_WINS_PROMPT
	elif state.white % 2 == 1:
		state.phase = "win"
		state.prompt = WHITE_WINS_PROMPT
	else:
		if state.turn == "black":
			state.turn = "white"
		else:
			state.turn = "black"
			
		state.phase = "select"
		state.prompt = SELECT_PROMPT

	_clear_marker("selected")
	_clear_marker("canMove")
	_clear_marker("start")
	_clear_marker("canHit")
	_clear_marker("willFall")
	
def _score():
	black_points = 0
	white_points = 0
	
	for o in range(5):
		for s in range(18):
			if "#" in state.board[o][s]:
				piece = state.board[o][s].split()[0].split("#")
				color = piece[0]
				type = piece[1]
				points = 0
				if type == "flag": points = FLAG_POINTS - (2 * (4 - o)) 
				elif type == "bomber": points = BOMBER_POINTS
				elif type == "sweeper": points = SWEEPER_POINTS
				elif type == "fighter": points = FIGHTER_POINTS
				if color == "black": black_points += points
				else: white_points += points
				
	black_score = MAX_SCORE - white_points
	white_score = MAX_SCORE - black_points
	
	state.black = black_score
	state.white = white_score
	
def _mark(orbit, sector, marker):	
	if state.board[orbit][sector] == "":
		state.board[orbit][sector] = marker
	else:
		state.board[orbit][sector] = state.board[orbit][sector] + " " + marker
				
def _clear_marker(marker):
	for o in range(5):
		for s in range(18):
			if state.board[o][s] == marker:
				state.board[o][s] = ""
			elif marker in state.board[o][s]:
				state.board[o][s] = state.board[o][s].split()[0]

def _get_selected_value():
	for o in range(5):
		for s in range(18):
			if "selected" in state.board[o][s]:
				return state.board[o][s]

def _get_selected_location():
	for o in range(5):
		for s in range(18):
			if "selected" in state.board[o][s]:
				return o, s

def _get_current_color_prefix():
	if state.turn == "black":
		return "black#"
	else:
		return "white#"

def _get_opposite_color_prefix():
	if state.turn == "black":
		return "white#"
	else:
		return "black#"
		
	return opp_prefix