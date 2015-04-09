from fanstatic import Library
from fanstatic import Resource

#Ignores hides the content of the library
library = Library('arche_pas_social', 'static', ignores='*')

def google_renderer(url):
    return '<script src="https://apis.google.com/js/client:platform.js" async defer></script>'


google_login_js = Resource(library, ".", renderer = google_renderer)
