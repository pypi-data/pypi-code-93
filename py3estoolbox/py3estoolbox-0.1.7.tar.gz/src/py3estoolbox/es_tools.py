#!/usr/bin/python3 -W ignore
import  os
import  requests
import  elasticsearch as es
import  json
import  py3toolbox     as tb
import urllib3
urllib3.disable_warnings()

from    elasticsearch import helpers
from    elasticsearch_dsl import Search





DEFAULT_ES_MAJOR_VERSION = "7"







class ES():
  def __init__(self, es_url):
    self.es_url  = es_url
    self.es_inst = es.Elasticsearch([self.es_url],scheme="https", verify_certs=False)
    self.indices = {}
    self.aliases = {}
    self.indices_list = []
    self.scanner = None
    self.batch_data = [] 
    self.get_es_info()
    self.scanner = None

  def get_es_info(self):
    self.indices  = { index_name: self.es_inst.indices.get('*')[index_name] for index_name in [ x for x in list( self.es_inst.indices.get('*').keys()) if not x.startswith('.') ]}
    self.aliases  = { index_name: self.es_inst.indices.get_alias('*')[index_name] for index_name in [ x for x in list( self.es_inst.indices.get_alias('*').keys()) if not x.startswith('.') ]}
    self.indices_list = list(self.indices.keys())
    self.indices_list.sort()
    return (self.indices, self.aliases)

  def show_info(self):
    info = []
    info.append("=" * (len(self.es_url) + 2))
    info.append(self.es_url)
    info.append('')
    for index in self.indices_list:
      alias = ','.join(self.aliases[index]['aliases'].keys())
      doc_count = self.get_doc_count(index=index)
      info.append(tb.format_str('{0:20} {1:10} {2:10}',index,alias,doc_count))
    info.append("-" * (len(self.es_url) + 2))
    return "\n".join(info)
  
  
  def _format_index_doc_id(self, index, doc_type,doc_id):
    return_str = '{0}|{1}|{2}'.format(index,doc_type,doc_id)
    return  return_str
    
  def _parse_index_doc_id(self, index_doc_id_str):
    m = re.match( r'^([^\|]+)\|([^\|]+)\|([^\|]+)$', index_doc_id_str, re.M|re.I)
    if m : return (m.group(1),m.group(2),m.group(3))
    else : return None   

  def init_scanner(self, index=None, alias=None, dsl_json=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    if dsl_json is None: # assume all records
      dsl_json = {"query": {"match_all": {}}}
    self.scanner = es.helpers.scan(self.es_inst, index=index, query=dsl_json)
 
  def get_index_by_alias(self, alias):
    result = []
    for k,v in self.aliases.items() :
      if alias in v['aliases']:
        result.append(k)
    if len(result) > 0: return  result[0]
    return None
  
  def delete_alias(self, alias, index=None) :
    if self.es_inst.indices.exists_alias(name=alias):
      if index is None : index = '*'
      self.es_inst.indices.delete_alias(index = index, name=alias)
 
  def set_alias(self, index, alias) :
    self.delete_alias(alias=alias)
    self.es_inst.indices.put_alias(index=index,      name=alias)       
    
  def get_doc_count(self, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    return int(self.es_inst.count(index=index)['count'])

  def get_ids(self, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    self.index_type_ids = []
    self.id_scanner = es.helpers.scan(self.es_inst, index=index, query={"stored_fields": ["_id"], "query": {"match_all": {}}})
    for doc in self.id_scanner :
      self.index_type_ids.append(self._format_index_doc_id(index,  doc['_type'] ,  doc['_id']))
    return (self.index_type_ids)
    
  def get_doc_by_id(self, doc_type, doc_id, index=None, alias=None) :
    if index is None: index = self.get_index_by_alias(alias=alias)
    doc = self.es_inst.search(index=index, doc_type=doc_type, body={"query": {"match": {"_id": doc_id}}})
    if int(doc['hits']['total']) == 0 : return None
    return (doc['hits']['hits'][0]['_source'])

  def bulk_exec(self, batch):
    helpers.bulk(self.es_inst, batch, request_timeout=120)
    
  def create_index(self, index, mapping_json):
    mapping = json.loads(mapping_json)
    if 'aliases' in mapping                            : mapping.pop('aliases', None)
    if 'creation_date' in mapping['settings']['index'] : mapping['settings']['index'].pop('creation_date', None)
    if 'provided_name' in mapping['settings']['index'] : mapping['settings']['index'].pop('provided_name', None)
    if 'uuid' in mapping['settings']['index']          : mapping['settings']['index'].pop('uuid', None)
    if 'version' in mapping['settings']['index']       : mapping['settings']['index'].pop('version', None)  
    
    self.es_inst.indices.create(index=index, body=json.dumps(mapping))
    self.get_es_info()
  
  def delete_index(self, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    self.es_inst.indices.delete(index=index, ignore=[400, 404])
    self.get_es_info()

  def delete_index_data(self, index=None, alias=None):
    batch = []
    item_count = 0
    doc_count = self.get_doc_count(index=index)
   
    self.init_scanner(index=index)
    try :
      start_time = time.time()
      for item in self.scanner:
        item_count +=1
        item.pop('_score', None)
        item['_index'] = index
        item_to_delete = {'_op_type' : "delete",  "_index" : item['_index'] , "_type" : item['_type'] , "_id" : item['_id'] } 
        batch.append(item_to_delete) 
        
        if (item_count % config['es_bulk_size']) == 0:  
          self.bulk_exec(batch)
          print (tb.show_progress_bar(current=item_count, total=doc_count, start_time=start_time), sep=' ', end='', flush=True)  
          batch = []
      self.bulk_exec(batch)
    except Exception as e:
      self.util.write_file(config['command_log'], 'Failed: ' + str(e) + + "\n")
    if (doc_count > 0) :
      print (self.util.show_progress_bar(current=item_count, total=doc_count, start_time=start_time), sep=' ', end='', flush=True)  
    
    print ("\n\n")
    return    
    
  def get_analyzer(self,index=None, alias=None):
    mapping_dic = self.get_mapping(json_fmt=False, index=index, alias=alias)
    analyzers   = {}
    for  a in mapping_dic['settings']['index']['analysis']['analyzer'].keys():
      analyzers[a] = {}
      analyzers[a]['filter'] = mapping_dic['settings']['index']['analysis']['analyzer'][a]['filter']
    return analyzers
  
  
  def get_mapping(self, json_fmt=True, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    mapping_dic = self.indices[index]
    if json_fmt :   mapping = json.dumps(mapping_dic, sort_keys=True, indent=2)
    else        :   mapping = mapping_dic
    return mapping

  def analyze_text(self, index=None, alias=None, analyzer=None, filter=None, text=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    url = self.es_url + '/' + index + '/_analyze'
    headers = {"Accept": "application/json"}
    
    if analyzer is not None: 
      body_data = '{"analyzer": "' + analyzer + '", "text":    "' + text + '" }'
      
    if filter is not None: 
      body_data = '{"filter": [' + json.dumps(filter) + '], "text":    "' + text + '" }'    
    response = requests.get(url,data = body_data)
    response_json = json.loads( response.text.replace("\\\"", "") )
    
    return (response_json)

    
    
    
  def test_analyzers(self, index=None, alias=None, text=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    analyze_result = {'analyzers': {}, 'filters': {} }
    filters = []
    for analyzer in  self.get_analyzer(index=index).keys():
      filter = self.get_analyzer(index=index)[analyzer]["filter"]
      filters.extend(filter)
      analyze_result['analyzers'][analyzer] = self.analyze_text(index=index,analyzer=analyzer,text=text)
    
    for filter in  list(set(filters)):
      analyze_result['filters'][filter]      = self.analyze_text(index=index,filter=filter,text=text)

    return analyze_result
  
  def query_by_dsl(self, doc_type, dsl_json, return_data=True, index=None, alias=None):
    if index is None: index = self.get_index_by_alias(alias=alias)
    if return_data == True :
      result = []
      result_page = self.es_inst.search(index=index, doc_type=doc_type, scroll = '5m', size=1000, body=dsl_json)
      scroll_id = result_page['_scroll_id']
      scroll_size = result_page['hits']['total']
      while (scroll_size > 0):
        result.extend(result_page['hits']['hits'])
        result_page = self.es_inst.scroll(scroll_id = scroll_id, scroll = '5m')
        scroll_id = result_page['_scroll_id']
        scroll_size = len(result_page['hits']['hits'])
      return (result)  
    else:
      result_page = self.es_inst.search(index=index, doc_type=doc_type, scroll = '5m', size=0, body=dsl_json) 
      return result_page['hits']['total']
  

  def update_index_refresh (self,  index=None, alias=None, refresh_interval_value='null') :
    if index is None: index = self.get_index_by_alias(alias=alias)
    put = self.es_inst.indices.put_settings(
        index=index,
        body='{"index": {"refresh_interval":' + refresh_interval_value + '}}',
        ignore_unavailable=True
    )

  def get_snapshot_repository(self):
    repos = self.es_inst.snapshot.get_repository()
    repos.pop("found-snapshots",None)
    for r in repos.keys():
      repos[r]["_snapshots"] = self.es_inst.snapshot.get(r,snapshot="*")
    
    return repos
  
  
  def delete_snapshot(self, repository, snapshot):
    repo = self.get_snapshot_repository()
    
    
    if repository in list(repo.keys()):
      for s in repo[repository]['_snapshots']['snapshots']:
        if s['snapshot'] == snapshot:
          self.es_inst.snapshot.delete(repository, snapshot)
          break;
    else:
      return True
    
    # verify
    found = True
    
    while found == True :
      repo = self.get_snapshot_repository()
      found = False
      if repository in list(repo.keys()):
        for s in repo[repository]['_snapshots']['snapshots']:
          if s['snapshot'] == snapshot:
            found = True
            print (repository + ":" + snapshot + " is still being deleted.")
            continue
      
    return True


  def create_snapshot(self, repository, snapshot):
    self.es_inst.snapshot.create(repository, snapshot)
   
    # verify
    created = False
    while created == False :
      repo = self.get_snapshot_repository()
      if repository in list(repo.keys()):
        for s in repo[repository]['_snapshots']['snapshots']:
          if s['snapshot'] == snapshot:
            if s['state'] != "SUCCESS":
              print (s['state'])
            else:
              created = True
              break
    return True  

  def restore_snapshot(self, repository, snapshot, body):
    self.es_inst.snapshot.restore(repository, snapshot, body=body, wait_for_completion = True )  
    return
 
if __name__ == "__main__": 
  
  pass  