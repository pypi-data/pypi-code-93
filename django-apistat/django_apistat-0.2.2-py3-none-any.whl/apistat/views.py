import json
#from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.db import connection, connections
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ApiStatSpr
from .serializers import ApiStatSprSerializer

def query_db(query, args=(), db_alias='', one=False):
    if (db_alias == ''):
        cur = connection.cursor()
    else:
        cur = connections[db_alias].cursor()
    cur.execute(query, args)
    r = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.connection.close()
    return (r[0] if r else None) if one else r

class ListView(APIView):
  def get(self, request):
    items = ApiStatSpr.objects.all()
    serializer = ApiStatSprSerializer(items, many=True)
    return Response(serializer.data)

class ReportView(APIView):
  def get(self, request, pk):
    param = {}
    for q in request.GET.keys():
        param[q] = request.GET.get(q)
    print(param)
    items = ApiStatSpr.objects.filter(id=pk).first()
    if items is None:
        return Response({})
    try:
        my_query = query_db(items.sql, param, items.db_alias)
    except Exception as e:  # This is the correct syntax
        return Response({'error': str(e)})
    #my_query = query_db('SELECT name FROM sqlite_master WHERE type =\'table\'')
    #json_output = json.dumps(my_query, sort_keys=True, indent=1, cls=DjangoJSONEncoder)
    return Response(my_query)
