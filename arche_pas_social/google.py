from betahaus.viewcomponent import view_action
from pyramid.renderers import render
import requests

from arche_pas_social.fanstatic_lib import google_login_js
from arche_pas_social.models import SocialAuth
from arche_pas_social import _


@view_action('arche_pas_social', 'google')
def render_login_button(context, request, va, **kw):
    google_login_js.need()
    response = {}
    response['CLIENT_ID'] = "XXX" #FIXME: Fetch from some smart place
    response['error_msg'] = _("Error while signing in with Google:")
    return render('arche_pas_social:templates/google.pt', response, request = request)


class GoogleAuth(SocialAuth):
    name = 'google'
    title = _("Google")

    def get_identifier(self, data):
        if data:
            return data.get('id', None)

    def get_data(self, request):
        access_token = request.POST.get('access_token', None)
        response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo?access_token=%s' % access_token)
        if response.ok:
            return response.json()

    def get_appstruct(self, data):
        appstruct = {}
        appstruct['email'] = data.get('email', '')
        appstruct['first_name'] = data.get('given_name', '')
        appstruct['last_name'] = data.get('family_name', '')
        return appstruct
        #FIXME: Picture?
# {
#  "id": "114828133366199135006",
#  "email": "robin@betahaus.net",
#  "verified_email": true,
#  "name": "Robin Harms Oredsson",
#  "given_name": "Robin",
#  "family_name": "Harms Oredsson",
#  "link": "https://plus.google.com/+RobinHarmsOredsson",
#  "picture": "https://lh5.googleusercontent.com/-1g6xFsm_vcA/AAAAAAAAAAI/AAAAAAAAACg/zAG89CH69jY/photo.jpg",
#  "gender": "male",
#  "locale": "sv",
#  "hd": "betahaus.net"
# }

def includeme(config):
    config.scan()
    config.registry.registerAdapter(GoogleAuth, name = GoogleAuth.name)
