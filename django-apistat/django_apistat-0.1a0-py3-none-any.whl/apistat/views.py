import json
#from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.db import connection
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ApiStatSpr
from .serializers import ApiStatSprSerializer

def query_db(query, args=(), one=False):
    cur = connection.cursor()
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
    items = ApiStatSpr.objects.filter(id=pk).first()
    if items is None:
        return Response({})
    my_query = query_db(items.sql)
    #my_query = query_db('SELECT name FROM sqlite_master WHERE type =\'table\'')
    #json_output = json.dumps(my_query, sort_keys=True, indent=1, cls=DjangoJSONEncoder)
    return Response(my_query)
