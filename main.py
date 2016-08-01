import httplib2
from oauth2client import client
from apiclient.discovery import build

flow = client.flow_from_clientsecrets('../client_secret.json',
                                      scope='https://www.googleapis.com/auth/drive',
                                      redirect_uri='http://localhost/')

auth_uri = flow.step1_get_authorize_url()
print auth_uri
code = raw_input(">")
credentials = flow.step2_exchange(code)


http = httplib2.Http()
http = credentials.authorize(http)

service = build('drive', 'v3', http=http)


res = {
    'name': "Test",
    'filetype': 'text/plain',
    'parents': ['0BzGsAuPlSoqmc1hxMGN1cmNmRTQ']
}

media = {
    'mimeType': 'text/csv',
    'body': 'fuckthis'
}

results = service.files().create(resource=res, media=media, fields='id').execute()

print results
print results.get('id')
