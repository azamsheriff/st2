import mock
import six

from st2common.transport.publishers import PoolPublisher
from tests import FunctionalTest

http_client = six.moves.http_client

TRIGGER_0 = {
    'name': 'st2.test.trigger0',
    'description': 'test trigger',
    'type': 'st2.test.triggertype0',
    'parameters': {}
}

TRIGGER_1 = {
    'name': 'st2.test.trigger1',
    'description': 'test trigger',
    'type': 'st2.test.triggertype1',
    'parameters': {}
}

TRIGGER_2 = {
    'name': 'st2.test.trigger2',
    'description': 'test trigger',
    'type': 'st2.test.triggertype2',
    'parameters': {
        'param1': {
            'foo': 'bar'
        }
    }
}


@mock.patch.object(PoolPublisher, 'publish', mock.MagicMock())
class TestTriggerController(FunctionalTest):

    @classmethod
    def setUpClass(cls):
        super(TestTriggerController, cls).setUpClass()
        cls._setupTriggerTypes()

    def test_get_all(self):
        post_resp = self._do_post(TRIGGER_0)
        trigger_id_0 = self._get_trigger_id(post_resp)
        post_resp = self._do_post(TRIGGER_1)
        trigger_id_1 = self._get_trigger_id(post_resp)
        resp = self.app.get('/triggers')
        self.assertEqual(resp.status_int, http_client.OK)
        # TriggerType without parameters will register a trigger
        # with same name. So here we see 4 instead of 2.
        self.assertEqual(len(resp.json), 4, 'Get all failure.')
        self._do_delete(trigger_id_0)
        self._do_delete(trigger_id_1)

    def test_get_one(self):
        post_resp = self._do_post(TRIGGER_1)
        trigger_id = self._get_trigger_id(post_resp)
        get_resp = self._do_get_one(trigger_id)
        self.assertEqual(get_resp.status_int, http_client.OK)
        self.assertEqual(self._get_trigger_id(get_resp), trigger_id)
        self._do_delete(trigger_id)

    def test_get_one_fail(self):
        resp = self._do_get_one('1')
        self.assertEqual(resp.status_int, http_client.NOT_FOUND)

    def test_post(self):
        post_resp = self._do_post(TRIGGER_1)
        self.assertEqual(post_resp.status_int, http_client.CREATED)
        self._do_delete(self._get_trigger_id(post_resp))

    def test_post_with_params(self):
        post_resp = self._do_post(TRIGGER_2)
        self.assertEqual(post_resp.status_int, http_client.CREATED)
        self._do_delete(self._get_trigger_id(post_resp))

    def test_post_duplicate(self):
        post_resp = self._do_post(TRIGGER_1)
        self.assertEqual(post_resp.status_int, http_client.CREATED)
        # Trying to create the same trigger again will still say "CREATED"
        # but under the hood gets the one already in db. So we just check
        # id is same in both cases.
        post_resp_2 = self._do_post(TRIGGER_1)
        self.assertEqual(post_resp_2.status_int, http_client.CREATED)
        self.assertEqual(self._get_trigger_id(post_resp), self._get_trigger_id(post_resp_2))
        self._do_delete(self._get_trigger_id(post_resp))

    def test_put(self):
        post_resp = self._do_post(TRIGGER_1)
        update_input = post_resp.json
        update_input['description'] = 'updated description.'
        put_resp = self._do_put(self._get_trigger_id(post_resp), update_input)
        self.assertEqual(put_resp.status_int, http_client.OK)
        self._do_delete(self._get_trigger_id(put_resp))

    def test_put_fail(self):
        post_resp = self._do_post(TRIGGER_1)
        update_input = post_resp.json
        # If the id in the URL is incorrect the update will fail since id in the body is ignored.
        put_resp = self._do_put(1, update_input)
        self.assertEqual(put_resp.status_int, http_client.NOT_FOUND)
        self._do_delete(self._get_trigger_id(post_resp))

    def test_delete(self):
        post_resp = self._do_post(TRIGGER_1)
        del_resp = self._do_delete(self._get_trigger_id(post_resp))
        self.assertEqual(del_resp.status_int, http_client.NO_CONTENT)

    @classmethod
    def _setupTriggerTypes(cls):
        TRIGGERTYPE_0 = {
            'name': 'st2.test.triggertype0',
            'description': 'test trigger',
            'payload_schema': {'tp1': None, 'tp2': None, 'tp3': None},
            'parameters_schema': {}
        }
        TRIGGERTYPE_1 = {
            'name': 'st2.test.triggertype1',
            'description': 'test trigger',
            'payload_schema': {'tp1': None, 'tp2': None, 'tp3': None},
        }
        TRIGGERTYPE_2 = {
            'name': 'st2.test.triggertype2',
            'description': 'test trigger',
            'payload_schema': {'tp1': None, 'tp2': None, 'tp3': None},
            'parameters_schema': {'param1': {'type': 'object'}}
        }
        cls.app.post_json('/triggertypes', TRIGGERTYPE_0, expect_errors=False)
        cls.app.post_json('/triggertypes', TRIGGERTYPE_1, expect_errors=False)
        cls.app.post_json('/triggertypes', TRIGGERTYPE_2, expect_errors=False)

    @staticmethod
    def _get_trigger_id(resp):
        return resp.json['id']

    def _do_get_one(self, trigger_id):
        return self.app.get('/triggers/%s' % trigger_id, expect_errors=True)

    def _do_post(self, trigger):
        return self.app.post_json('/triggers', trigger, expect_errors=True)

    def _do_put(self, trigger_id, trigger):
        return self.app.put_json('/triggers/%s' % trigger_id, trigger, expect_errors=True)

    def _do_delete(self, trigger_id):
        return self.app.delete('/triggers/%s' % trigger_id)