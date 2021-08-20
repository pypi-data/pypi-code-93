import logging

from django.core.management import BaseCommand
from django.db import connection, IntegrityError
from tqdm import tqdm

from isc_common.models.images import Images
from isc_common.models.users_images import Users_images
from lfl_admin.competitions.models.calendar_images import Calendar_images
from lfl_admin.competitions.models.club_logo_history_images import Club_logo_history_images
from lfl_admin.competitions.models.clubs_images import Clubs_images
from lfl_admin.competitions.models.divisions_images import Divisions_images
from lfl_admin.competitions.models.leagues_images import Leagues_images
from lfl_admin.competitions.models.players_images import Players_images
from lfl_admin.competitions.models.referees_images import Referees_images
from lfl_admin.competitions.models.tournaments_images import Tournaments_images
from lfl_admin.constructions.models.fields_images import Fields_images
from lfl_admin.constructions.models.stadiums_images import Stadiums_images
from lfl_admin.decor.models.banners import Banners
from lfl_admin.decor.models.news_images import News_images
from lfl_admin.inventory.models.clothes_images import Clothes_images
from lfl_admin.region.models.city_images import City_images
from lfl_admin.region.models.region_images import Region_images
from lfl_admin.region.models.region_zone_images import Region_zone_images

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def update_model(self, model, id, idss):
        try:
            res = model.objects.filter(image_id__in=idss).update(image_id=id)
            # print(f'res: {res}')
        except IntegrityError:
            res = model.objects.filter(image_id__in=idss).delete()
            # print(f'res: {res}')

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute('''select count(*), real_name
                                    from isc_common_images
                                    group by real_name
                                    having count(*) > 1''')
            rows = cursor.fetchall()
            pbar = tqdm(total=len(rows))

            for row in rows:
                _, real_name = row
                ids = list(map(lambda x: x.id, Images.objects.filter(real_name=real_name)))
                id = ids[0]
                idss = ids[1:]

                self.update_model(model=Banners, id=id, idss=idss)
                self.update_model(model=Calendar_images, id=id, idss=idss)
                self.update_model(model=City_images, id=id, idss=idss)
                self.update_model(model=Clothes_images, id=id, idss=idss)
                self.update_model(model=Club_logo_history_images, id=id, idss=idss)
                self.update_model(model=Clubs_images, id=id, idss=idss)
                self.update_model(model=Divisions_images, id=id, idss=idss)
                self.update_model(model=Fields_images, id=id, idss=idss)
                self.update_model(model=Leagues_images, id=id, idss=idss)
                self.update_model(model=News_images, id=id, idss=idss)
                self.update_model(model=Players_images, id=id, idss=idss)
                self.update_model(model=Referees_images, id=id, idss=idss)
                self.update_model(model=Region_images, id=id, idss=idss)
                self.update_model(model=Region_zone_images, id=id, idss=idss)
                self.update_model(model=Stadiums_images, id=id, idss=idss)
                self.update_model(model=Tournaments_images, id=id, idss=idss)
                self.update_model(model=Users_images, id=id, idss=idss)

                res = Images.objects.filter(id__in=idss).delete()
                # print(f'res: {res}')

                pbar.update()

            pbar.close()
