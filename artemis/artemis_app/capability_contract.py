"""Versioned, local capability contract. JSON-only v1 is deliberately narrow.

This validates metadata, NOT code safety. Isolation belongs to Execution. No
schema references are resolved, no packages downloaded, no plugin imported into
trusted Python, and no source claim is inferred from a model-authored URL.
"""
from __future__ import annotations

import ast
import copy
import re
from jsonschema import Draft202012Validator
from .store import dump

CONTRACT = 'artemis.capability/v1'
NAME = r'^[a-z][a-z0-9_]{2,47}$'
SOURCE = {'repository': 'flrtemis/agent', 'branch': 'main',
          'commit': 'a09f1d25b0aeb5700f03600618aff34408f3fcf6',
          'paths': ['agent.py', 'agent2.py'],
          'adaptation': 'Hot create_tool/load_tools/execute(**kwargs) lifecycle; original handlers are not executed.'}
CREATE_PROPERTIES = {
    'name': {'type': 'string', 'pattern': NAME},
    'description': {'type': 'string', 'minLength': 1, 'maxLength': 1000},
    'parameters': {'type': 'object', 'description': 'JSON Schema properties map (original Agent format).'},
    'required_args': {'type': 'array', 'items': {'type': 'string'}, 'maxItems': 32, 'uniqueItems': True},
    'python_code': {'type': 'string', 'minLength': 1, 'maxLength': 8000},
    'test_arguments': {'type': 'object', 'description': 'One sandbox test input; never user files.'},
    'expected_result': {'description': 'Exact finite JSON value expected from execute(**kwargs).'},
    'replace_version': {'type': 'integer', 'minimum': 0, 'description': '0 for a new name; exact active version for a reviewed replacement.'},
    'license': {'type': 'string', 'minLength': 1, 'maxLength': 120,
                'description': 'Declared contribution license; defaults to LicenseRef-Unspecified, not a redistribution grant.'},
}
CREATE_REQUIRED = ['name', 'description', 'parameters', 'required_args', 'python_code', 'test_arguments', 'expected_result']
KEYWORDS = {'type', 'description', 'title', 'enum', 'properties', 'required',
            'additionalProperties', 'items', 'minLength', 'maxLength', 'minItems',
            'maxItems', 'minimum', 'maximum', 'minProperties', 'maxProperties'}
TYPES = {'object', 'array', 'string', 'integer', 'number', 'boolean', 'null'}


def valid_name(name):
    if not isinstance(name, str) or not re.fullmatch(NAME, name):
        raise ValueError('Tool name must be 3–48 lowercase letters/digits/underscores, starting with a letter')
    return name


def parameter_schema(properties, required):
    if not isinstance(properties, dict) or len(properties) > 32:
        raise ValueError('Parameters must be a properties map with at most 32 keys')
    if not isinstance(required, list) or len(set(required)) != len(required) or not set(required) <= set(properties):
        raise ValueError('Required arguments must be unique declared parameter names')
    # Preserve the original property-map contract, do not guess among formats.
    schema = {'type': 'object', 'properties': copy.deepcopy(properties),
              'required': list(required), 'additionalProperties': False}
    count = 0

    def bound(node, depth=0):
        nonlocal count
        count += 1
        if depth > 6 or count > 128:
            raise ValueError('Extension schema depth/size exceeds v1 bounds')
        if not isinstance(node, dict) or set(node) - KEYWORDS:
            raise ValueError('Unsupported schema keyword; references/combinators are not allowed in v1')
        if node.get('type') not in TYPES:
            raise ValueError('Every parameter schema needs one supported type')
        typ = node['type']
        if typ == 'object':
            props = node.setdefault('properties', {})
            if not isinstance(props, dict) or len(props) > 32:
                raise ValueError('Object properties outside contract bounds')
            if node.get('additionalProperties', False) is not False:
                raise ValueError('Additional object properties are not permitted')
            node['additionalProperties'] = False
            req = node.get('required', [])
            if not isinstance(req, list) or any(not isinstance(k, str) for k in req) or len(set(req)) != len(req) or not set(req) <= set(props):
                raise ValueError('Invalid nested required arguments')
            for key, child in props.items():
                if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,63}', key):
                    raise ValueError('Invalid parameter name')
                bound(child, depth + 1)
        if typ == 'array':
            if 'items' not in node:
                raise ValueError('Array items must have a schema')
            node.setdefault('maxItems', 128)
            if type(node['maxItems']) is not int or not 0 <= node['maxItems'] <= 128:
                raise ValueError('Array maxItems outside v1 bounds')
            bound(node['items'], depth + 1)
        if typ == 'string':
            node.setdefault('maxLength', 4096)
            if type(node['maxLength']) is not int or not 0 <= node['maxLength'] <= 4096:
                raise ValueError('String maxLength outside v1 bounds')
        if 'enum' in node and (not isinstance(node['enum'], list) or len(node['enum']) > 128):
            raise ValueError('Enum exceeds v1 bounds')
    bound(schema)
    try:
        dump(schema)
        Draft202012Validator.check_schema(schema)
    except Exception as e:
        raise ValueError('Invalid extension parameter schema: ' + str(e)[:200]) from e
    return schema


def validate_creation(args, reserved):
    try:
        dump(args)
        Draft202012Validator({'type': 'object', 'properties': CREATE_PROPERTIES,
                              'required': CREATE_REQUIRED, 'additionalProperties': False}).validate(args)
    except Exception as e:
        raise ValueError('Invalid create_tool arguments: ' + str(e)[:200]) from e
    name = valid_name(args['name'])
    if name in reserved:
        raise ValueError('Cannot replace a core/reserved capability')
    schema = parameter_schema(args['parameters'], args['required_args'])
    try:
        tree = ast.parse(args['python_code'])  # Parse ONLY; never import/exec here.
    except (SyntaxError, ValueError) as e:
        raise ValueError('Invalid Python syntax: ' + str(e)[:200]) from e
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'execute']
    if len(functions) != 1:
        raise ValueError('Define exactly one top-level execute(**kwargs) function')
    sig = functions[0].args
    if not sig.kwarg or sig.args or sig.posonlyargs or sig.kwonlyargs or sig.vararg:
        raise ValueError('v1 entry point must be execute(**kwargs), with no other arguments')
    validate_arguments(schema, args['test_arguments'])
    if len(dump(args['expected_result']).encode('utf-8')) > 64_000:
        raise ValueError('Expected test result exceeds 64 KB')
    return schema


def validate_arguments(schema, arguments):
    try:
        if not isinstance(arguments, dict) or len(dump(arguments).encode('utf-8')) > 32_000:
            raise ValueError('Arguments must be a JSON object under 32 KB')
        Draft202012Validator(schema).validate(arguments)
    except Exception as e:
        raise ValueError('Invalid extension invocation arguments: ' + str(e)[:200]) from e
