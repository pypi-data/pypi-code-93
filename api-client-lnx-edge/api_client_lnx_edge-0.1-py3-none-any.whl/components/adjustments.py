import pytz
from datetime import datetime

from .base import BaseAPIClient


class AdjustmentsAPI(BaseAPIClient):

    def adjust(self, affiliate_id, offer_id_path: list, created_on: str, click_adjustment=0, conversion_adjustment=0,
               total_conversion_adjustment=0, conversion_amount_adjustment=0.00, payout_adjustment=0.00):
        data = {
            'affiliateId': affiliate_id,
            'offerIdPath': offer_id_path,
            'clickAdjustment': click_adjustment,
            'conversionAdjustment': conversion_adjustment,  # Paid conv, and total if that's not provided
            'conversionAmountAdjustment': conversion_amount_adjustment,
            'payoutAdjustment': payout_adjustment,
            'createdOn': self.format_adjustment_date(created_on)
        }

        if total_conversion_adjustment:
            data['totalConversionAdjustment'] = total_conversion_adjustment

        resp = self._post('api/adjust-stats', json=data)

        return resp

    @staticmethod
    def format_adjustment_date(date_str):
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date must be provided as YYYY-MM-DD.')
        tz = pytz.timezone('America/New_York')
        local_time = tz.localize(date).replace(hour=12)
        return local_time.astimezone(tz=pytz.timezone('UTC')).strftime('%Y-%m-%dT%H:00:00.000Z')
