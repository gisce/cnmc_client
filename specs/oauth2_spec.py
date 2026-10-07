# -*- coding: utf-8 -*-
import base64
import json
import urlparse

from mock import patch, MagicMock
from expects import *

from cnmc_client import CNMC_API, Client


def http_response(status, content):
    response = MagicMock()
    response.status = status
    response.read.return_value = content
    return response


def token_response(token='the_token', expires_in=299):
    return http_response(200, json.dumps({
        'access_token': token,
        'scope': 'read',
        'token_type': 'Bearer',
        'expires_in': expires_in,
    }))


class FakeServer(object):
    """
    Collect the requests and answer them with the queued responses
    """

    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def __call__(self, host, timeout=None):
        connection = MagicMock()

        def request(method, path, body=None, headers=None):
            self.requests.append({
                'host': host, 'method': method, 'path': path,
                'body': body, 'headers': dict(headers or {}),
            })

        connection.request.side_effect = request
        connection.getresponse.side_effect = lambda: self.responses.pop(0)
        return connection

    def token_requests(self):
        return [r for r in self.requests if r['path'] == '/oauth2/token']


config = {
    'key': 'the_key',
    'secret': 'the_secret',
}


with description('CNMC API with OAuth 2.0'):

    with context('token request'):
        with it('uses client_credentials with basic auth against the environment'):
            server = FakeServer([token_response()])
            with patch('cnmc_client.cnmc.httplib.HTTPSConnection', server):
                api = CNMC_API(environment='staging', **config)
                token = api.get_token()

            expect(token).to(equal('the_token'))
            request = server.requests[0]
            expect(request['host']).to(equal('apipre.cnmc.gob.es:443'))
            expect(request['method']).to(equal('POST'))
            expect(request['headers']['Authorization']).to(equal(
                'Basic {}'.format(base64.b64encode('the_key:the_secret'))
            ))
            expect(urlparse.parse_qs(request['body'])).to(equal({
                'grant_type': ['client_credentials'], 'scope': ['read'],
            }))

        with it('uses prod by default'):
            server = FakeServer([token_response()])
            with patch('cnmc_client.cnmc.httplib.HTTPSConnection', server):
                CNMC_API(**config).get_token()
            expect(server.requests[0]['host']).to(equal('api.cnmc.gob.es:443'))

        with it('raises if the token can not be obtained'):
            server = FakeServer([http_response(401, 'invalid_client')])
            with patch('cnmc_client.cnmc.httplib.HTTPSConnection', server):
                api = CNMC_API(**config)
                expect(lambda: api.get_token()).to(raise_error(ValueError))

    with context('token lifecycle'):
        with it('reuses the token while valid'):
            server = FakeServer([
                token_response(), http_response(200, '{}'), http_response(200, '{}'),
            ])
            with patch('cnmc_client.cnmc.httplib.HTTPSConnection', server):
                api = CNMC_API(**config)
                api.get(resource='/api-oauth2/test/perfil')
                api.get(resource='/api-oauth2/test/perfil')

            expect(server.token_requests()).to(have_len(1))
            expect(server.requests[1]['headers']['Authorization']).to(equal('Bearer the_token'))
            expect(server.requests[2]['headers']['Authorization']).to(equal('Bearer the_token'))

        with it('asks a new token when it is about to expire'):
            server = FakeServer([
                token_response('first'), http_response(200, '{}'),
                token_response('second'), http_response(200, '{}'),
            ])
            with patch('cnmc_client.cnmc.httplib.HTTPSConnection', server):
                with patch('cnmc_client.cnmc.time.time') as mock_time:
                    mock_time.return_value = 1000
                    api = CNMC_API(**config)
                    api.get(resource='/api-oauth2/test/perfil')
                    # 299s token with 30s margin
                    mock_time.return_value = 1000 + 270
                    api.get(resource='/api-oauth2/test/perfil')

            expect(server.token_requests()).to(have_len(2))
            expect(server.requests[3]['headers']['Authorization']).to(equal('Bearer second'))

        with it('asks a new token and retries once on 401'):
            server = FakeServer([
                token_response('first'), http_response(401, ''),
                token_response('second'), http_response(200, '{"ok": true}'),
            ])
            with patch('cnmc_client.cnmc.httplib.HTTPSConnection', server):
                api = CNMC_API(**config)
                response = api.get(resource='/api-oauth2/test/perfil')

            expect(response['code']).to(equal(200))
            expect(response['result']).to(equal({'ok': True}))
            expect(server.requests[3]['headers']['Authorization']).to(equal('Bearer second'))

        with it('does not retry more than once on 401'):
            server = FakeServer([
                token_response('first'), http_response(401, ''),
                token_response('second'), http_response(401, 'unauthorized'),
            ])
            with patch('cnmc_client.cnmc.httplib.HTTPSConnection', server):
                api = CNMC_API(**config)
                response = api.get(resource='/api-oauth2/test/perfil')

            expect(response['code']).to(equal(401))
            expect(response['error']).to(be_true)
            expect(server.requests).to(have_len(4))

    with context('client resources'):
        with it('fetch uses the api-oauth2 verticales path'):
            server = FakeServer([token_response(), http_response(200, 'a,b\n1,2\n')])
            with patch('cnmc_client.cnmc.httplib.HTTPSConnection', server):
                client = Client(**config)
                client.fetch(['ES0021000000228141PR'], 'SIPS2026_PS_ELECTRICIDAD')

            expect(server.requests[1]['method']).to(equal('GET'))
            expect(server.requests[1]['path']).to(equal(
                '/api-oauth2/verticales/v1/SIPS/consulta/v1/SIPS2026_PS_ELECTRICIDAD.csv?cups=ES0021000000228141PR'
            ))

        with it('list sends the params as POST body to ficheros/consultar'):
            server = FakeServer([
                token_response(),
                http_response(200, json.dumps({'empresa': ['the_nif']})),
                http_response(200, '[]'),
            ])
            with patch('cnmc_client.cnmc.httplib.HTTPSConnection', server):
                client = Client(**config)
                client.list()

            expect(server.requests[1]['path']).to(equal('/api-oauth2/test/perfil'))
            request = server.requests[2]
            expect(request['method']).to(equal('POST'))
            expect(request['path']).to(equal('/api-oauth2/ficheros/consultar'))
            expect(urlparse.parse_qs(request['body'])).to(equal({
                'idProcedimiento': ['2'], 'nifEmpresa': ['the_nif'], 'estado': ['DISPONIBLE'],
            }))

        with it('test uses the profile resource'):
            server = FakeServer([token_response(), http_response(200, '{}')])
            with patch('cnmc_client.cnmc.httplib.HTTPSConnection', server):
                client = Client(**config)
                client.test()

            expect(server.requests[1]['path']).to(equal('/api-oauth2/test/perfil'))

        with it('download does not send the token'):
            server = FakeServer([http_response(200, '{}')])
            with patch('cnmc_client.cnmc.httplib.HTTPSConnection', server):
                client = Client(**config)
                client.download('https://api.cnmc.gob.es/ficheros/v1/descarga/the_id')

            expect(server.token_requests()).to(have_len(0))
            expect(server.requests[0]['path']).to(equal('/ficheros/v1/descarga/the_id'))
            expect(server.requests[0]['headers']).not_to(have_key('Authorization'))
