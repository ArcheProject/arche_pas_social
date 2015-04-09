from unittest import TestCase

from arche.testing import barebone_fixture
from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from arche_pas_social.interfaces import IProviderMapper
from arche_pas_social.interfaces import ISocialAuth



class ProviderMapperTests(TestCase):
    
    def setUp(self):
        self.config = testing.setUp()
 
    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from arche_pas_social.models import ProviderMapper
        return ProviderMapper

    def test_verify_class(self):
        verifyClass(IProviderMapper, self._cut)

    def test_verify_object(self):
        verifyObject(IProviderMapper, self._cut(testing.DummyResource()))

    def test_registration(self):
        self.config.include('arche_pas_social')
        root = barebone_fixture(self.config)
        self.failUnless(self.config.registry.queryAdapter(root, IProviderMapper))

    def test_add(self):
        root = barebone_fixture(self.config)
        obj = self._cut(root)
        obj.add('userid', 'dummy_service', 'identifier')
        self.assertIn('userid', obj.userid_to_services)
        self.assertIn(('dummy_service', 'identifier'), obj.service_identifier_to_userid)

    def test_remove(self):
        root = barebone_fixture(self.config)
        obj = self._cut(root)
        obj.add('userid', 'dummy_service', 'identifier')
        obj.add('userid', 'd1', 'i1')
        obj.add('userid', 'd2', 'i2')
        obj.remove('userid', 'd2', 'i2')
        self.assertIn(('dummy_service', 'identifier'), obj.service_identifier_to_userid)
        self.assertIn(('d1', 'i1'), obj.service_identifier_to_userid)
        self.assertNotIn(('d2', 'i2'), obj.service_identifier_to_userid)

    def test_remove_nonexistent(self):
        root = barebone_fixture(self.config)
        obj = self._cut(root)
        obj.remove('userid', 'dummy_service', 'identifier')
        obj.add('userid', 'd1', 'i1')
        obj.remove('userid', 'dummy_service', 'identifier')

    def test_remove_unknown_identifier(self):
        root = barebone_fixture(self.config)
        obj = self._cut(root)
        obj.add('userid', 'dummy_service', 'identifier')
        obj.add('userid', 'd1', 'i1')
        obj.add('userid', 'd2', 'i2')
        obj.remove('userid', 'd2')
        self.assertIn(('dummy_service', 'identifier'), obj.service_identifier_to_userid)
        self.assertIn(('d1', 'i1'), obj.service_identifier_to_userid)
        self.assertNotIn(('d2', 'i2'), obj.service_identifier_to_userid)

    def test_remove_userid(self):
        root = barebone_fixture(self.config)
        obj = self._cut(root)
        obj.add('userid', 'dummy_service', 'identifier')
        obj.add('userid', 'd1', 'i1')
        obj.add('userid', 'd2', 'i2')
        obj.add('u2', 'd1', 'i3')
        obj.remove_userid('userid')
        self.assertNotIn(('dummy_service', 'identifier'), obj.service_identifier_to_userid)
        self.assertNotIn(('d1', 'i1'), obj.service_identifier_to_userid)
        self.assertNotIn(('d2', 'i2'), obj.service_identifier_to_userid)
        self.assertNotIn('userid', obj.userid_to_services)
        self.assertIn(('d1', 'i3'), obj.service_identifier_to_userid)
        self.assertIn('u2', obj.userid_to_services)

    def test_cleanup_on_user_delete(self):
        from arche.api import User
        self.config.include('arche_pas_social.models')
        root = barebone_fixture(self.config)
        users = root['users']
        users['userid'] = User()
        obj = self._cut(root)
        obj.add('userid', 'dummy_service', 'identifier')
        del users['userid']
        self.assertNotIn(('dummy_service', 'identifier'), obj.service_identifier_to_userid)
        self.assertNotIn('userid', obj.userid_to_services)


class SocalAuthTests(TestCase):
    
    def setUp(self):
        self.config = testing.setUp()
 
    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from arche_pas_social.models import SocialAuth
        return SocialAuth

    def test_verify_class(self):
        verifyClass(ISocialAuth, self._cut)

    def test_verify_object(self):
        verifyObject(ISocialAuth, self._cut(testing.DummyResource()))

    def test_login(self):
        self.config.include('arche_pas_social')
        root = barebone_fixture(self.config)
        obj = self._cut(root)
        obj.name = 'dummy_service'
        self.assertEqual(obj.login('404'), None)
        mapper = IProviderMapper(root)
        mapper.add('userid', 'dummy_service', 'identifier')
        self.assertEqual(obj.login('identifier'), 'userid')
