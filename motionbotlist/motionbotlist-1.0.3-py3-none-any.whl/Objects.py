
class botobj(object):
    def __init__(self, data):
        self.id = data.get("bot_id")
        self.name = data.get("bot_name")
        self.avatar = data.get("avatar")
        self.status = data.get("bot_status")
        self.co_owners = data.get("co_owners")
        self.discord = data.get("discord")
        self.support_server = data.get("discord")
        self.invite = data.get("invite")
        self.lib = data.get("lib")
        self.list_date = data.get("list_date")
        self.owner_id = data.get("owner_id")
        self.owner_name = data.get("ower_name")
        self.prefix = data.get("prefix")
        self.servers = data.get("servers")
        self.site = data.get("site")
        self.website = data.get("site")
        self.tops = data.get("tops")
        self.vanity_url = data.get("vanity_url")

class voteobj(object):
    def __init__(self, data):
        self.vote_time = data.get("vote-time")
        self.is_user = data.get("user")
        self.user_id = data.get("id")
        self.user_name = data.get("user_name")


