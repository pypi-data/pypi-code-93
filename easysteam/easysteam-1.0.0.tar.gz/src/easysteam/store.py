from api_functions.get_games import Pull_Games
from __init__ import Config

class Market():

    def __init__(self):
        self.cached = None
        self.cat_urls = Config.Category_URLS

    def Pull(self, category, row):

        if 'https://' in category:
            market_category = category
            market_pull = Pull_Games(market_category, row)
            return market_pull

        else:
            market_category = ''

            try:
                market_category = self.cat_urls[category]

            except:
                for category_type in self.cat_urls:
                    if category_type.lower() == category.lower():
                        market_category = self.cat_urls[category_type]

            market_pull = Pull_Games(market_category, row)
            return market_pull

    def Pull_All(self, row):
        all = []

        for name in self.cat_urls:
            print(name)
            market_pull = Pull_Games(self.cat_urls[name], row)
            all.append(market_pull)

        return all

store = Market()
store.Pull_All('NewReleasesRows')
