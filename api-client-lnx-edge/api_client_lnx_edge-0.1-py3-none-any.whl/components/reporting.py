from datetime import datetime, date

from .base import BaseAPIClient


class ReportingAPI(BaseAPIClient):

    def _get_report(self,
                    dimensions: list,
                    start_date: (datetime, date, str),
                    end_date: (datetime, date, str),
                    timezone: str = 'America/New_York',
                    metrics: list = None,
                    filters: list = None,
                    rows_per_page: int = 10000,
                    row_offset: int = 0,
                    **kwargs):

        report_config = {
            'dimensions': dimensions,
            'metrics': metrics or ['sessions', 'clicks', 'conversions', 'paidConversions', 'lnxRevenue', 'lnxCost'],
            'dateRange': self.build_daterange(start_date, end_date),
            'timezone': timezone,
            'filters': self.build_filters(filters or [], **kwargs),
            'tableSort': {},
            'rowsPerPage': rows_per_page,
            'rowOffset': row_offset
        }

        # Overrides report_config with passed-in kwargs, but doesn't add any NEW keys to dict. Allows user to pass
        #  filters like `affiliate_id=XXXX` with ease.
        report_config.update((k, kwargs[k]) for k in report_config.keys() & kwargs.keys())

        resp = self._post('api/reports', json=report_config)

        return resp

    def get_advertiser_report(self, start_date: (datetime, date, str), end_date: (datetime, date, str), **kwargs):
        return self._get_report(
            dimensions=['advertiserId', 'advertiserName'],
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    def get_affiliate_report(self, start_date: (datetime, date, str), end_date: (datetime, date, str), **kwargs):
        return self._get_report(
            dimensions=['affiliateId', 'affiliateCompany'],
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    def get_click_report(self, start_date: (datetime, date, str), end_date: (datetime, date, str), **kwargs):
        return self._get_report(
            dimensions=['clickId', 'created_on', 'affiliateId', 'affiliateCompany', 'offerId', 'offerName',
                        's1', 's2', 's3', 's4', 's5', 'ipaddress', 'go_disposition'],
            metrics=['conversions', 'paidConversions', 'lnxProfit', 'lnxRevenue', 'lnxCost'],
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    def get_daily_report(self, start_date: (datetime, date, str), end_date: (datetime, date, str), **kwargs):
        return self._get_report(
            dimensions=['timestampDay'],
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    def get_hourly_report(self, start_date: (datetime, date, str), end_date: (datetime, date, str), **kwargs):
        return self._get_report(
            dimensions=['timestampDay', 'hourOfDay'],
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    def get_offer_report(self, start_date: (datetime, date, str), end_date: (datetime, date, str), **kwargs):
        return self._get_report(
            dimensions=['offerId', 'offerName'],
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    def get_paid_conversion_report(self, start_date: (datetime, date, str), end_date: (datetime, date, str), **kwargs):
        return self._get_report(
            dimensions=['clickId', 'created_on', 'affiliateId', 'affiliateCompany', 'offerId', 'offerName',
                        's1', 's2', 's3', 's4', 's5', 'ipaddress'],
            metrics=['lnxProfit', 'lnxRevenue', 'lnxCost'],
            filters=[{'type': 'gt', 'value': 0, 'column': 'paidConversions'}],
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    def get_product_report(self, start_date: (datetime, date, str), end_date: (datetime, date, str), **kwargs):
        return self._get_report(
            dimensions=['productId', 'productName'],
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    def get_sessions_report(self, start_date: (datetime, date, str), end_date: (datetime, date, str), **kwargs):
        return self._get_report(
            dimensions=['clickId', 'created_on', 'affiliateId', 'affiliateCompany', 'offerId', 'offerName',
                        's1', 's2', 's3', 's4', 's5', 'ipaddress', 'go_disposition'],
            metrics=['clicks', 'conversions', 'paidConversions', 'lnxProfit', 'lnxRevenue', 'lnxCost'],
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    def get_suboffer_report(self, start_date: (datetime, date, str), end_date: (datetime, date, str), **kwargs):
        return self._get_report(
            dimensions=['subOfferId', 'subOfferName'],
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    def get_total_conversion_report(self, start_date: (datetime, date, str), end_date: (datetime, date, str), **kwargs):
        return self._get_report(
            dimensions=['clickId', 'created_on', 'affiliateId', 'affiliateCompany', 'offerId', 'offerName',
                        's1', 's2', 's3', 's4', 's5', 'ipaddress'],
            metrics=['lnxProfit', 'lnxRevenue', 'lnxCost'],
            filters=[{'type': 'gt', 'value': 0, 'column': 'conversions'}],
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )

    def get_custom_report(self, report_config, **kwargs):
        return self._post('api/reports', json=report_config, **kwargs)

    @staticmethod
    def build_filters(filters, **kwargs):
        """ Provide any of `affiliate_id`, `offer_id`, `product_id`, `advertiser_id` to add to list of filters. """
        if 'affiliate_id' in kwargs.keys():
            filters.append({'column': 'affiliateId', 'type': 'includes', 'value': [kwargs['affiliate_id']]})
        if 'offer_id' in kwargs.keys():
            filters.append({'column': 'offerId', 'type': 'includes', 'value': [kwargs['offer_id']]})
        if 'product_id' in kwargs.keys():
            filters.append({'column': 'productId', 'type': 'includes', 'value': [kwargs['product_id']]})
        if 'advertiser_id' in kwargs.keys():
            filters.append({'column': 'advertiserId', 'type': 'includes', 'value': [kwargs['advertiser_id']]})

        return filters

    @staticmethod
    def build_daterange(start_date, end_date):
        _daterange = []
        if isinstance(start_date, datetime):
            _daterange.append(start_date.strftime('%Y-%m-%d'))
        elif isinstance(start_date, str):
            _daterange.append(start_date)
        else:
            raise ValueError('`start_date` must be a date/datetime object or a YYYY-MM-DD string.')

        if isinstance(end_date, datetime):
            _daterange.append(end_date.strftime('%Y-%m-%d'))
        elif isinstance(end_date, str):
            _daterange.append(end_date)
        else:
            raise ValueError('`end_date` must be a date/datetime object or a YYYY-MM-DD string.')

        return _daterange
