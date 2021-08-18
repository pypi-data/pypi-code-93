import config
from berserk import session
from berserk import clients
from berserk import enums

session = session.TokenSession(config.API_KEYS['ADMIN_LICHESS_TOKEN'])
lichess = clients.Client(session=session)

x = lichess.users.get_crosstable('zccze', 'SatwantHundal', matchup=True)


y = lichess.users.get_user_performance('zccze', 'raopid')
print(y)
