from .. fetch_engine import FetchEngine
from .... config.default_config import DB_URL
from .... utilities.singleton import Singleton
from sqlalchemy import select, and_, outerjoin, join, column
import six,pdb
import numpy as np
import pandas as pd

@six.add_metaclass(Singleton)
class FetchSLYEngine(FetchEngine):
    def __init__(self):
        super(FetchSLYEngine, self).__init__('sly', DB_URL['sly'])
    
    def show_cloumns(self, name):
        result = self._insp.get_columns(name)
        result = [r for r in result if r['name'] not in ['timestamp','flag']]
        return pd.DataFrame(result).drop(['default','comment','nullable','autoincrement'],axis=1)
      
    
    def default_multiple(self, table, key_name, key_value,
                        query_name, query_values):
        return and_(table.__dict__[key_name] == key_value,
                   table.flag == 1, table.__dict__[query_name].in_(query_values)
                   )
    
    def default_dates(self, table,  dates, 
                      time_name='trade_date', codes=None, key=None):
       
        return and_(table.__dict__[time_name].in_(dates),
                    table.flag == 1) if key is None else and_(table.__dict__[time_name].in_(dates),
                    table.flag == 1, table.__dict__[key].in_(codes)) 
    
    def default_notdates(self, table, begin_date, end_date, 
                         time_name='trade_date',
                         codes=None, key=None):
        return and_(table.__dict__[time_name] >= begin_date, 
                               table.__dict__[time_name] <= end_date,
                               table.flag == 1) if key is None else and_(table.__dict__[time_name] >= begin_date, 
                               table.__dict__[time_name] <= end_date,
                               table.flag == 1, table.__dict__[key].in_(codes))
    
    def gd_overview(self, codes, key=None, columns=None):
        table = self._base.classes['gd_overview']
        return self.base_notime(table=table, codes=codes, key=key, 
                                columns=columns, clause_list=None)
    
    def gd_factor(self, codes=None, begin_date=None, end_date=None, dates=None, columns=None):
        table = self._base.classes['gd_factor']
        if begin_date is not None and end_date is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif dates is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                               table.__dict__['date'].in_(dates),
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
            
            
        
    def bd_count(self, codes, begin_date, 
                                    end_date, columns, freq, 
                                    dates):
        table = self._base.classes['bd_count']
        if begin_date is not None and end_date is not None and codes \
                    is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and codes \
                    is None:
            clause_list = and_(table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    
    def users(self, codes, key=None, columns=None):
        table = self._base.classes['user']
        clause_list = and_(table.__dict__[key].in_(codes),
                          table.flag == 1)
        return self.base_notime(table=table, codes=codes, key=key, 
                                columns=columns, clause_list=clause_list)
    
    
    def esg_metrics_detail(self, codes, key, columns): 
        table = self._base.classes['esg_metrics_detail']
        if codes is not None:
            clause_list = and_(table.__dict__[key].in_(codes),
                          table.flag == 1)
        else:
            clause_list = and_(table.flag == 1,
                          table.flag == 1)
        return self.base_notime(table=table, codes=codes, key=key, 
                                columns=columns, clause_list=clause_list)
    
    def gd_trend_ratings(self, codes=None, key=None, begin_date=None, end_date=None, 
               columns=None, freq=None, dates=None):
        table = self._base.classes['gd_trend_ratings']
        if dates is not None:
            clause_list = self.default_dates(table=table, dates=dates, 
                                             codes=codes, key=key, 
                                             time_name='trade_date') 
        else:
            clause_list = self.default_notdates(table=table, begin_date=begin_date, 
                                                end_date=end_date, codes=codes, key=key,
                                                time_name='trade_date')
        return self.base(table=table, begin_date=begin_date, end_date=end_date, 
                         codes=codes, key=key, columns=columns, freq=freq, 
                         dates=dates, clause_list=clause_list,time_name='trade_date')
    
    def gd_distribution_ratings(self, codes=None, key=None, columns=None):
        table = self._base.classes['gd_distribution_ratings']
        return self.base_notime(table=table, codes=codes, key=key, 
                                columns=columns, clause_list=None)
    
    def gd_reviews(self, codes=None, key=None, begin_date=None, end_date=None, 
               columns=None, freq=None, dates=None, limit=10, pos=0):
        table = self._base.classes['gd_reviews']
        if dates is not None:
            clause_list = self.default_dates(table=table, dates=dates, 
                                             codes=codes, key=key, 
                                             time_name='reviewDateTime') 
        else:
            clause_list = self.default_notdates(table=table, begin_date=begin_date, 
                                                end_date=end_date, codes=codes, key=key,
                                                time_name='reviewDateTime')
        return self.base(table=table, begin_date=begin_date, end_date=end_date, 
                         codes=codes, key=key, columns=columns, freq=freq, 
                         dates=dates, clause_list=clause_list,limit=limit,pos=pos,
                         time_name='reviewDateTime')
 
    def gdelt_volraw(self, codes=None,  categories=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None):
        table = self._base.classes['gdelt_volraw']
        if dates is not None and categories is not None and codes is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.__dict__['category'].in_(categories),
                           table.date.in_(dates),table.flag == 1)
        elif begin_date is not None and end_date is not None and categories \
                is not None and codes is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.__dict__['category'].in_(categories),
                           table.date >= begin_date, 
                           table.date <= end_date,
                               table.flag == 1)
            
        elif dates is not None and codes is not None and categories is None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date.in_(dates),table.flag == 1)
            
        elif begin_date is not None and end_date is not None and codes is not \
            None and categories is None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date >= begin_date, 
                           table.date <= end_date,table.flag == 1)
            
        elif dates is not None and categories is not None and code is None:
            clause_list = and_(table.__dict__['category'].in_(categories),
                           table.date.in_(dates),table.flag == 1)
            
        elif begin_date is not None and end_date is not None and categories \
                is not None and codes is None:
            clause_list = and_(table.__dict__['category'].in_(categories),
                           table.date >= begin_date, 
                           table.date <= end_date,table.flag == 1)
            
        elif begin_date is not None and end_date is not None and categories \
                is  None and codes is None:
            clause_list = and_(table.date >= begin_date, 
                           table.date <= end_date,table.flag == 1)
        elif dates is not None and categories is  None and codes is None:
            clause_list = and_(table.date.in_(dates),table.flag == 1)
            
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    
    def gdelt_tone(self, codes=None,  categories=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None):
        table = self._base.classes['gdelt_tone']
        if dates is not None and categories is not None and codes is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.__dict__['category'].in_(categories),
                           table.date.in_(dates),table.flag == 1)
        elif begin_date is not None and end_date is not None and categories \
                is not None and codes is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.__dict__['category'].in_(categories),
                           table.date >= begin_date, 
                           table.date <= end_date,table.flag == 1)
            
        elif dates is not None and codes is not None and categories is None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date.in_(dates),table.flag == 1)
            
        elif begin_date is not None and end_date is not None and codes is not \
            None and categories is None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date >= begin_date, 
                           table.date <= end_date,table.flag == 1)
            
        elif dates is not None and categories is not None and code is None:
            clause_list = and_(table.__dict__['category'].in_(categories),
                           table.date.in_(dates),table.flag == 1)
            
        elif begin_date is not None and end_date is not None and categories \
                is not None and codes is None:
            clause_list = and_(table.__dict__['category'].in_(categories),
                           table.date >= begin_date, 
                           table.date <= end_date,table.flag == 1)
        elif begin_date is not None and end_date is not None and categories \
                is  None and codes is None:
            clause_list = and_(table.date >= begin_date, 
                           table.date <= end_date,
                               table.flag == 1)
        elif dates is not None and categories is  None and codes is None:
            clause_list = and_(table.date.in_(dates),
                               table.flag == 1)
            
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    
    def bhr_overview(self, codes, key=None, columns=None):
        table = self._base.classes['bhr_overview']
        return self.base_notime(table=table, codes=codes, key=key, 
                                columns=columns, clause_list=None)
    
    def gdelt_feed(self, codes=None, key=None, begin_date=None, end_date=None,
                          columns=None, freq=None, dates=None, time_name='publish_time'):
        table = self._base.classes['gdelt_feed']
        if dates is not None:
            clause_list = self.default_dates(table=table, dates=dates, 
                                             codes=codes, key=key, 
                                             time_name=time_name) 
        else:
            clause_list = self.default_notdates(table=table, begin_date=begin_date, 
                                                end_date=end_date, codes=codes, key=key,
                                                time_name=time_name)
            
        return self.base(table=table, begin_date=begin_date, end_date=end_date, 
                         codes=codes, key=key, columns=columns, freq=freq, 
                         dates=dates, clause_list=clause_list,time_name=time_name)
    
    
    def gdelt_feed_feature(self, codes=None, key=None, columns=None):
        table = self._base.classes['gdelt_label']
        clause_list = and_(table.__dict__['feed_id'].in_(codes),
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    
    def gdelt_feed_sentiment(self, codes=None, key=None, columns=None):
        table = self._base.classes['gdelt_sentiment']
        clause_list = and_(table.__dict__['feed_id'].in_(codes),
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    
    
    def refinitiv_feed(self, codes=None, key=None, begin_date=None, end_date=None,
                          columns=None, freq=None, dates=None, time_name='publish_time'):
        table = self._base.classes['refinitiv_feed']
        if dates is not None:
            clause_list = self.default_dates(table=table, dates=dates, 
                                             codes=codes, key=key, 
                                             time_name=time_name) 
        else:
            clause_list = self.default_notdates(table=table, begin_date=begin_date, 
                                                end_date=end_date, codes=codes, key=key,
                                                time_name=time_name)
            
        return self.base(table=table, begin_date=begin_date, end_date=end_date, 
                         codes=codes, key=key, columns=columns, freq=freq, 
                         dates=dates, clause_list=clause_list,time_name=time_name)
    
    
    def refinitiv_feed_feature(self, codes=None, key=None, columns=None):
        table = self._base.classes['refinitiv_label']
        clause_list = and_(table.__dict__[key].in_(codes),
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    
    
    def refinitiv_esg_category(self, codes=None, key=None, columns=None):
        table = self._base.classes['refinitiv_esg_category']
        clause_list = and_(table.__dict__[key].in_(codes),
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
            
        
    def esg_metrics(self, codes=None, key=None, begin_date=None, end_date=None,
                          columns=None, freq=None, dates=None, time_name='date'):
        table = self._base.classes['esg_metrics']
        if dates is not None:
            clause_list = self.default_dates(table=table, dates=dates, 
                                             codes=codes, key=key, 
                                             time_name=time_name) 
        else:
            clause_list = self.default_notdates(table=table, begin_date=begin_date, 
                                                end_date=end_date, codes=codes, key=key,
                                                time_name=time_name)
            
        return self.base(table=table, begin_date=begin_date, end_date=end_date, 
                         codes=codes, key=key, columns=columns, freq=freq, 
                         dates=dates, clause_list=clause_list,time_name=time_name) 
        
    def esg_metrics_data(self, table_name, codes=None, key=None, begin_date=None, end_date=None,
                          columns=None, freq=None, dates=None, time_name='date'):
        table = self._base.classes['esg_metrics' + '_' + table_name]
        if dates is not None:
            clause_list = self.default_dates(table=table, dates=dates, 
                                             codes=codes, key=key, 
                                             time_name=time_name) 
        else:
            clause_list = self.default_notdates(table=table, begin_date=begin_date, 
                                                end_date=end_date, codes=codes, key=key,
                                                time_name=time_name)
            
        return self.base(table=table, begin_date=begin_date, end_date=end_date, 
                         codes=codes, key=key, columns=columns, freq=freq, 
                         dates=dates, clause_list=clause_list,
                         time_name=time_name) 
    
    def esg_metrics_indicator(self, codes=None, name=None, begin_date=None, 
                              end_date=None, columns=None):
        table = self._base.classes['esg_metrics_indicator']
        clause_list = and_(table.__dict__['flag'] == 1,
                           table.__dict__['flag'].isnot(None))
        if codes is not None:
            exp = table.__dict__['code'].in_(codes)
            clause_list.append(exp)
        if name is not None:
            exp = table.__dict__['name'].in_(name)
            clause_list.append(exp)
        if begin_date is not None and end_date is not None:
            clause_list.append(table.__dict__['date'] >= begin_date)
            clause_list.append(table.__dict__['date'] <= end_date)
            
        return self.base_multiple(table=table, clause_list=clause_list, 
                                  columns=columns)
        
        
    def bhr_feed(self, codes=None, key=None, begin_date=None, end_date=None,
                          columns=None, freq=None, dates=None, time_name='publish_time'):
        table = self._base.classes['bhr_feed']
        if dates is not None:
            clause_list = self.default_dates(table=table, dates=dates, 
                                             codes=codes, key=key, 
                                             time_name=time_name) 
        else:
            clause_list = self.default_notdates(table=table, begin_date=begin_date, 
                                                end_date=end_date, codes=codes, key=key,
                                                time_name=time_name)
            
        return self.base(table=table, begin_date=begin_date, end_date=end_date, 
                         codes=codes, key=key, columns=columns, freq=freq, 
                         dates=dates, clause_list=clause_list,time_name=time_name)
    
    def bhr_feed_feature(self, codes=None, key=None, columns=None):
        table = self._base.classes['bhr_label']
        clause_list = and_(table.__dict__['feed_id'].in_(codes),
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
        
    def bhr_label(self, key_name, key_value, query_name, query_values, 
                  columns=None, freq=None):
        table = self._base.classes['bhr_label']
        if key_name is not None and query_name is not None:
            clause_list = self.default_multiple(table, key_name, key_value,
                        query_name, query_values)
        elif key_name is not None and query_name is None:
            clause_list = and_(table.__dict__[key_name] == key_value,
                   table.flag == 1)
            
        return self.base_multiple(table=table, clause_list=clause_list, columns=None)
        
    def bd_label_data(self, codes=None, key=None, begin_date=None, end_date=None,
                          columns=None, freq=None, dates=None):
        table = self._base.classes['bd_label_data']
        if dates is not None:
            clause_list = self.default_dates(table=table, dates=dates, 
                                             codes=codes, key=key, 
                                             time_name='date') 
        else:
            clause_list = self.default_notdates(table=table, begin_date=begin_date, 
                                                end_date=end_date, codes=codes, key=key,
                                                time_name='date')
        return self.base(table=table, begin_date=begin_date, end_date=end_date, 
                         codes=codes, key=key, columns=columns, freq=freq, 
                         dates=dates, clause_list=clause_list,time_name='date')
    
    
    def index_components(self, codes=None, key='code', category='sp500', columns=None):
        table = self._base.classes['index_components']
        if codes is None:
            clause_list = and_(table.flag == 1,
                              table.index_name==category)
        else:
            clause_list = and_(table.__dict__[key].in_(codes),
                               table.index_name==category,
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns) 
    
    
    def industry(self, codes=None, key='code', category='GICS', columns=None):
        table = self._base.classes['industry']
        if codes is None:
            clause_list = and_(table.flag == 1,
                              table.industry==category)
        else:
            clause_list = and_(table.__dict__[key].in_(codes),
                               table.industry==category,
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns) 
        
    def company(self, codes=None, primary=[1], key='code', columns=None):
        table = self._base.classes['company']
        if codes is None:
            clause_list = and_(table.flag == 1,
                              table.is_primary.in_(primary))
        else:
            clause_list = and_(table.__dict__[key].in_(codes),
                              table.is_primary.in_(primary),
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns) 

    
    def bhr_category_mapping(self, name=None, columns=None):
        table = self._base.classes['bhr_category_mapping']
        if name is None:
            clause_list = and_(table.flag == 1)
        elif name is not None:
            clause_list = and_(table.__dict__['name'].in_(name),
                              table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    def esg_feed(self, codes=None,  categories=None, key='category', begin_date=None, end_date=None,
                columns=None, freq=None, dates=None, limit=10, pos=0):
        table = self._base.classes['esg_feed']
        clause_list = None
        if begin_date is not None and end_date is not None and categories is not None \
            and codes is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.__dict__[key].in_(categories),
                           table.publish_time >= begin_date, 
                           table.publish_time <= end_date,
                           table.__dict__['flag'] == 1)
        elif begin_date is not None and end_date is not None  \
            and codes is not None:
            clause_list = and_(table.__dict__[key].in_(codes),
                           table.publish_time >= begin_date, 
                           table.publish_time <= end_date,
                           table.__dict__['flag'] == 1)
        elif begin_date is not None and end_date is not None and categories is not None \
            and codes is None:
            clause_list = and_(table.__dict__[key].in_(categories),
                           table.publish_time >= begin_date, 
                           table.publish_time <= end_date,
                           table.__dict__['flag'] == 1)
        return self.base_multiple(table=table, clause_list=clause_list, 
                                  columns=columns, limit=limit, pos=pos)

    def gdelt_factor(self, codes=None,  categories=None, level=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None):
        table = self._base.classes['gdelt_factor'] if level is None else self._base.classes['gdelt_factor_level' + str(level)]
        if dates is not None and categories is not None and codes is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.__dict__['category'].in_(categories),
                           table.date.in_(dates),
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and categories \
                    is not None and codes is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.__dict__['category'].in_(categories),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif dates is not None and categories is not None:
            clause_list = and_(table.__dict__['category'].in_(categories),
                           table.date.in_(dates),
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and categories \
                    is not None:
            clause_list = and_(table.__dict__['category'].in_(categories),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif dates is not None and codes is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date.in_(dates),
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and codes \
                    is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and codes \
                    is None and categories is None:
            clause_list = and_(table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    def esg_factor(self, codes=None,  categories=None, level=None, begin_date=None, end_date=None,
                columns=None, freq=None, dates=None):
        table = self._base.classes['esg_factor_level' + str(level)]
        if dates is not None and categories is not None and codes is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.__dict__['category'].in_(categories),
                           table.date.in_(dates),
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and categories \
                    is not None and codes is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.__dict__['category'].in_(categories),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif dates is not None and categories is not None:
            clause_list = and_(table.__dict__['category'].in_(categories),
                           table.date.in_(dates),
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and categories \
                    is not None:
            clause_list = and_(table.__dict__['category'].in_(categories),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif dates is not None and codes is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date.in_(dates),
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and codes \
                    is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and codes \
                    is None and categories is None:
            clause_list = and_(table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    def esg_detail(self, classify=None, category=None, level=1, columns=None):
        table = self._base.classes['esg_detail'] 
        if classify is not None:
            clause_list = and_(table.__dict__['classify'].in_(classify),
                               table.flag == 1)
        elif category is not None and level is not None:
            clause_list = and_(table.__dict__['level'+str(level) + '_category'].in_(category),
                               table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    def user_model_rating(self, tabel_name, codes, uid, begin_date, 
                                    end_date, columns, freq, 
                                    dates):
        table = self._base.classes[tabel_name]
        if begin_date is not None and end_date is not None and codes \
                    is not None and uid is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.__dict__['uid'].in_(uid),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and codes \
                    is None and uid is not None:
            clause_list = and_(table.__dict__['uid'].in_(uid),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and codes \
                    is not None and uid is None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and codes \
                    is None and uid is None:
            clause_list = and_(table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    def bd_glassdoors_rating(self, codes, begin_date, end_date, columns, freq, dates):
        table = self._base.classes['bd_gd_rating']
        if begin_date is not None and end_date is not None and codes \
                    is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and codes \
                    is None:
            clause_list = and_(table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    
    def bd_model_rating(self, tabel_name, codes, begin_date, 
                                    end_date, columns, freq, 
                                    dates):
        table = self._base.classes[tabel_name]
        if begin_date is not None and end_date is not None and codes \
                    is not None:
            clause_list = and_(table.__dict__['code'].in_(codes),
                           table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        elif begin_date is not None and end_date is not None and codes \
                    is None:
            clause_list = and_(table.date >= begin_date, 
                           table.date <= end_date,
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
            
        
    def ultron_gentic(self, rootid=None, fitness=None, classify=None, columns=None):
        table = self._base.classes['ultron_gentic']
        if rootid is not None and fitness is not None:
            clause_list = and_(table.rootid == rootid,
                           table.__dict__['fitness'] >= fitness,
                           table.flag == 1)
        elif rootid is not None:
            clause_list = and_(table.rootid == rootid,
                           table.flag == 1)
        else:
            clause_list = and_(table.is_vaild == 0,
                           table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    
    def cn_market_daily(self, codes=None, key=None, is_adj_before=True,
                        begin_date=None, end_date=None, dates=None, columns=None):
        table = self._base.classes['cn_adj_before_market'] if is_adj_before else \
            self._base.classes['cn_market']
        if begin_date is not None and end_date is not None:
            clause_list = and_(table.trade_date >= begin_date, 
                           table.trade_date <= end_date,
                           table.flag == 1)
        elif dates is not None:
            clause_list = and_(table.__dict__['trade_date'].in_(dates),
                               table.flag == 1)
            
        if codes is not None:
            clause_list.append(table.__dict__[key].in_(codes),table.flag == 1)
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    
    def hk_market_daily(self, codes=None, key=None, is_adj_before=True,
                        begin_date=None, end_date=None, dates=None, columns=None):
        table = self._base.classes['hk_adj_before_market'] if is_adj_before else \
            self._base.classes['hk_market']
        if begin_date is not None and end_date is not None:
            clause_list = and_(table.trade_date >= begin_date, 
                           table.trade_date <= end_date,
                           table.flag == 1)
        elif dates is not None:
            clause_list = and_(table.__dict__['trade_date'].in_(dates),
                               table.flag == 1)
            
        if codes is not None:
            clause_list.append(table.__dict__[key].in_(codes))
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)
    
    def us_market_daily(self, codes=None, key=None, is_adj_before=True,
                        begin_date=None, end_date=None, dates=None, columns=None):
        table = self._base.classes['us_adj_before_market'] if is_adj_before else \
            self._base.classes['us_market']
        if begin_date is not None and end_date is not None:
            clause_list = and_(table.trade_date >= begin_date, 
                           table.trade_date <= end_date,
                           table.flag == 1)
        elif dates is not None:
            clause_list = and_(table.__dict__['trade_date'].in_(dates),
                               table.flag == 1)
            
        if codes is not None:
            clause_list.append(table.__dict__[key].in_(codes))
        return self.base_multiple(table=table, clause_list=clause_list, columns=columns)