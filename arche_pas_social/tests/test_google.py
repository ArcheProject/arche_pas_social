from unittest import TestCase

from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from arche_pas_social.interfaces import ISocialAuth


class GoogleAuthTests(TestCase):
    
    def setUp(self):
        self.config = testing.setUp()
 
    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from arche_pas_social.google import GoogleAuth
        return GoogleAuth

    def test_verify_class(self):
        verifyClass(ISocialAuth, self._cut)

    def test_verify_object(self):
        verifyObject(ISocialAuth, self._cut(testing.DummyResource()))
