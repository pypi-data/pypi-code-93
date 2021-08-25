from functools import reduce

from limes_common.connections import Criteria

from ..http import HttpConnection
from ... import config
from ...models.network import elab
from ...models.network.endpoints import ELabEndpoint

class ELabConnection(HttpConnection):
    def __init__(self) -> None:
        super().__init__(config.ELAB_API, [
            Criteria.SAMPLES
        ])
        self._token: str = ''

    def _getAuthHeader(self):
        return {'authorization': self._token}

    def SetToken(self, token:str) -> None:
        self._token = token

    def LoggedIn(self) -> bool:
        return self._token != ''

    def Login(self, username: str, password: str) -> elab.Login.Response:
        return elab.Login.Response(self.session.post(
            self._makeUrl(ELabEndpoint.LOGIN),
            data=elab.Login.MakeRequest(username, password)
        ))

    def _truncateToId(self, id: str) -> str:
        return id[-9:] if len(id) > 9 else id

    def SearchSamplesById(self, strIds: list[str]) -> elab.Sample.ListResponse:
        ids = list(self._truncateToId(id) for id in strIds)
        query = '' if len(strIds)==0 else '?sampleID=' + reduce(lambda s, id: '%s,%s' % (s, id), ids, '')[1:]
        return elab.Sample.ListResponse(self.session.get(
            '%s/%s%s' % (self._makeUrl(ELabEndpoint.SAMPLES), 'get', query),
            headers=self._getAuthHeader()
        ))

    def SearchSamplesByName(self, name: str) -> elab.Sample.ListResponse:
        query = '' if len(name)==0 else '?name=' + reduce(lambda s, id: '%s,%s' % (s, id), [name], '')[1:]
        return elab.Sample.ListResponse(self.session.get(
            '%s%s' % (self._makeUrl(ELabEndpoint.SAMPLES), query),
            headers=self._getAuthHeader()
        ))

    def SearchSamples(self, token: str) -> elab.Sample.ListResponse:
        return elab.Sample.ListResponse(self.session.get(
            '%s%s%s' % (self._makeUrl(ELabEndpoint.SAMPLES), '?search=', token),
            headers=self._getAuthHeader()
        ))

    def GetSample(self, id: str) -> elab.Sample.Response:
        id = self._truncateToId(id)
        return elab.Sample.Response(self.session.get(
            '%s/%s' % (self._makeUrl(ELabEndpoint.SAMPLES), id),
            headers=self._getAuthHeader()
        ))

    def GetSampleMeta(self, id: str) -> elab.SampleMeta.Response:
        id = self._truncateToId(id)
        return elab.SampleMeta.Response(self.session.get(
            '%s/%s/meta' % (self._makeUrl(ELabEndpoint.SAMPLES), id),
            headers=self._getAuthHeader()
        ))

    def UpdateSampleMeta(self, sampleId: str, metaKey: str, newValue: str) -> elab.SampleMeta.UpdateResponse:
        id = self._truncateToId(sampleId)
        meta = self.GetSampleMeta(id)
        fieldId=0
        field = elab.MetaField()
        for k, f in meta.Fields.items():
            if k == metaKey:
                fieldId = f.sampleMetaID
                field = f
                if field.sampleDataType in ['TEXTAREA']:
                    field.value = newValue
                else:
                    print('cannot update a non text meta field')
        return elab.SampleMeta.UpdateResponse(self.session.patch(
            '%s/%s/meta/%s' % (self._makeUrl(ELabEndpoint.SAMPLES), id, fieldId),
            headers=self._getAuthHeader(),
            data=field.ToDict(),
        ))