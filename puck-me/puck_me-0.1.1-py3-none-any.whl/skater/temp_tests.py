from puck_me.skater.skaters import Skaters

year = "2009"

nhl_players = Skaters.all_skaters("2009")

print(f"Found {len(nhl_players)} NHL players.")

for player in nhl_players[:1]:
    print(f"Player name: {player.name}.")
    print(player.games_played())
    print(player.goals())
    print(player.assists())
    print(player.points())
    print(player.plus_minus())
    print(player.penalty_mins())
    print(player.goals_even_strength())
    print(player.goals_power_play())
    print(player.goals_short_handed())
    print(player.goals_game_winning())
    print(player.shots())
    print(player.shooting_percentage())
    print(player.shifts())
    print(player.time_on_ice_per_game())
    print(player.time_on_ice_total())
    pass

print(len(nhl_players))
