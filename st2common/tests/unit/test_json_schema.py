# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest2 import TestCase
from jsonschema.exceptions import ValidationError

from st2common.util import schema as util_schema

TEST_SCHEMA_1 = {
    'additionalProperties': False,
    'title': 'foo',
    'description': 'Foo.',
    'type': 'object',
    'properties': {
        'cmd_no_default': {
            'description': 'Foo',
            'required': True,
            'type': 'string'
        }
    }
}

TEST_SCHEMA_2 = {
    'additionalProperties': False,
    'title': 'foo',
    'description': 'Foo.',
    'type': 'object',
    'properties': {
        'cmd_default': {
            'default': 'date',
            'description': 'Foo',
            'required': True,
            'type': 'string'
        }
    }
}

TEST_SCHEMA_3 = {
    'additionalProperties': False,
    'title': 'foo',
    'description': 'Foo.',
    'type': 'object',
    'properties': {
        'arg_optional_default': {
            'default': 'bar',
            'description': 'Foo',
            'type': 'string'
        },
        'arg_optional_default_none': {
            'default': None,
            'description': 'Foo',
            'type': 'string'
        },
        'arg_optional_no_default': {
            'description': 'Foo',
            'type': 'string'
        }
    }
}

TEST_SCHEMA_4 = {
    'additionalProperties': False,
    'title': 'foo',
    'description': 'Foo.',
    'type': 'object',
    'properties': {
        'arg_optional_default': {
            'default': 'bar',
            'description': 'Foo',
            'anyOf': [
                {'type': 'string'},
                {'type': 'boolean'}
            ]
        },
        'arg_optional_default_none': {
            'default': None,
            'description': 'Foo',
            'anyOf': [
                {'type': 'string'},
                {'type': 'boolean'}
            ]
        },
        'arg_optional_no_default': {
            'description': 'Foo',
            'anyOf': [
                {'type': 'string'},
                {'type': 'boolean'}
            ]
        },
        'arg_optional_no_default_anyof_none': {
            'description': 'Foo',
            'anyOf': [
                {'type': 'string'},
                {'type': 'boolean'},
                {'type': 'null'}
            ]
        }
    }
}

TEST_SCHEMA_5 = {
    'additionalProperties': False,
    'title': 'foo',
    'description': 'Foo.',
    'type': 'object',
    'properties': {
        'arg_optional_default': {
            'default': 'bar',
            'description': 'Foo',
            'oneOf': [
                {'type': 'string'},
                {'type': 'boolean'}
            ]
        },
        'arg_optional_default_none': {
            'default': None,
            'description': 'Foo',
            'oneOf': [
                {'type': 'string'},
                {'type': 'boolean'}
            ]
        },
        'arg_optional_no_default': {
            'description': 'Foo',
            'oneOf': [
                {'type': 'string'},
                {'type': 'boolean'}
            ]
        },
        'arg_optional_no_default_oneof_none': {
            'description': 'Foo',
            'oneOf': [
                {'type': 'string'},
                {'type': 'boolean'},
                {'type': 'null'}
            ]
        }
    }
}


class JSONSchemaTestCase(TestCase):
    def test_use_default_value(self):
        # No default, no value provided, should fail
        instance = {}
        validator = util_schema.get_validator()

        expected_msg = '\'cmd_no_default\' is a required property'
        self.assertRaisesRegexp(ValidationError, expected_msg, util_schema.validate,
                                instance=instance, schema=TEST_SCHEMA_1, cls=validator,
                                use_default=True)

        # No default, value provided
        instance = {'cmd_no_default': 'foo'}
        util_schema.validate(instance=instance, schema=TEST_SCHEMA_1, cls=validator,
                             use_default=True)

        # default value provided, no value, should pass
        instance = {}
        validator = util_schema.get_validator()
        util_schema.validate(instance=instance, schema=TEST_SCHEMA_2, cls=validator,
                             use_default=True)

        # default value provided, value provided, should pass
        instance = {'cmd_default': 'foo'}
        validator = util_schema.get_validator()
        util_schema.validate(instance=instance, schema=TEST_SCHEMA_2, cls=validator,
                             use_default=True)

    def test_allow_default_none(self):
        # Let validator take care of default
        validator = util_schema.get_validator()
        util_schema.validate(instance=dict(), schema=TEST_SCHEMA_3, cls=validator,
                             use_default=True, allow_default_none=True)

    def test_allow_default_explicit_none(self):
        # Explicitly pass None to arguments
        instance = {
            'arg_optional_default': None,
            'arg_optional_default_none': None,
            'arg_optional_no_default': None
        }

        validator = util_schema.get_validator()
        util_schema.validate(instance=instance, schema=TEST_SCHEMA_3, cls=validator,
                             use_default=True, allow_default_none=True)

    def test_anyof_type_allow_default_none(self):
        # Let validator take care of default
        validator = util_schema.get_validator()
        util_schema.validate(instance=dict(), schema=TEST_SCHEMA_4, cls=validator,
                             use_default=True, allow_default_none=True)

    def test_anyof_allow_default_explicit_none(self):
        # Explicitly pass None to arguments
        instance = {
            'arg_optional_default': None,
            'arg_optional_default_none': None,
            'arg_optional_no_default': None,
            'arg_optional_no_default_anyof_none': None
        }

        validator = util_schema.get_validator()
        util_schema.validate(instance=instance, schema=TEST_SCHEMA_4, cls=validator,
                             use_default=True, allow_default_none=True)

    def test_oneof_type_allow_default_none(self):
        # Let validator take care of default
        validator = util_schema.get_validator()
        util_schema.validate(instance=dict(), schema=TEST_SCHEMA_5, cls=validator,
                             use_default=True, allow_default_none=True)

    def test_oneof_allow_default_explicit_none(self):
        # Explicitly pass None to arguments
        instance = {
            'arg_optional_default': None,
            'arg_optional_default_none': None,
            'arg_optional_no_default': None,
            'arg_optional_no_default_oneof_none': None
        }

        validator = util_schema.get_validator()
        util_schema.validate(instance=instance, schema=TEST_SCHEMA_5, cls=validator,
                             use_default=True, allow_default_none=True)
