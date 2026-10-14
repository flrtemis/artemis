"""Agent's hot tool lifecycle adapted to one ARTEMIS registry/run/approval owner.

Original source is preserved, not imported as a server. Versioned code is DATA
in the canonical store, tested in Execution's JSON-only profile, and dispatched
only there. No sys.path hacks, name-derived egress, trusted plugin imports,
automatic downloads, competing chat loop or second job database.
"""
from __future__ import annotations

import hashlib
from vendor_sources.local_ollama_arena_agent.local_arena_agent.tools.base import Tool
from .capability_contract import (CONTRACT, SOURCE, CREATE_PROPERTIES, CREATE_REQUIRED,
                                  NAME, valid_name, validate_creation, validate_arguments)
from .extension_sandbox import ExtensionSandbox, LIMITS
from .tools import digest


class GeneratedTools:
    def __init__(self, runtime, execution):
        self.runtime = runtime
        self.tools = runtime.tools
        self.store = runtime.store
        self.sandbox = ExtensionSandbox(execution)
        self.load_errors = []
        self.reserved = set(self.tools.registry._tools) | {'create_tool', 'list_tools', 'rollback_tool'}
        for name, description, properties, required, function, approval in [
            ('create_tool', 'Propose a needed stdlib Python execute(**kwargs) capability. Operator approves exact code/schema/test; stage and sandbox-test before hot registration. No files/network/host state. Then call the new tool in THIS same run.',
             CREATE_PROPERTIES, CREATE_REQUIRED, self.create, True),
            ('list_tools', 'Inspect this same canonical catalogue and tested local extension versions, not a second agent inventory.',
             {}, [], lambda a: {'ok': True, 'tools': self.tools.manifest(), 'extensions': self.catalogue()}, False),
            ('rollback_tool', 'Approve activation of an immutable previously sandbox-tested version; exact active version must match. Never reruns its test or past actions.',
             {'name': {'type': 'string', 'pattern': NAME}, 'version': {'type': 'integer', 'minimum': 1},
              'expected_version': {'type': 'integer', 'minimum': 1}},
             ['name', 'version', 'expected_version'], self.rollback, True),
        ]:
            self.tools.registry.add(Tool(name, description,
                                        {'type': 'object', 'properties': properties, 'required': required,
                                         'additionalProperties': False}, function, approval, 'extensions'))
        self.tools.generated = self
        for row in self.store.extension_versions():
            if self.store.extension_active_version(row['name']) == row['version']:
                try:
                    self.install(row)
                except ValueError as e:
                    self.load_errors.append({'name': row['name'], 'error': str(e)})
        self.sync_availability()

    def sync_availability(self):
        state = self.sandbox.available()
        names = ['create_tool'] + [t.name for t in self.tools.registry._tools.values() if t.category == 'generated']
        for name in names:
            if state['available']:
                self.tools.unavailable.pop(name, None)
            else:
                self.tools.unavailable[name] = state.get('reason', 'Real isolation is required for generated tools')

    def isolated(self, name):
        t = self.tools.registry.get(name)
        return name == 'create_tool' or bool(t and t.category == 'generated')

    def owns(self, name):
        return name in ('create_tool', 'rollback_tool') or self.isolated(name)

    def validate(self, name, arguments):
        if name == 'create_tool':
            validate_creation(arguments, self.reserved)
            if arguments.get('replace_version', 0) != self.store.extension_active_version(arguments['name']):
                raise ValueError('Use the exact active replace_version; core tools cannot be replaced')
        elif name == 'rollback_tool':
            valid_name(arguments['name'])
            if arguments['name'] in self.reserved:
                raise ValueError('Cannot roll back a core capability')
            row = self.store.extension_version(arguments['name'], arguments['version'])
            self.check_record(row)
            if arguments['expected_version'] != self.store.extension_active_version(arguments['name']):
                raise ValueError('Active version changed before rollback proposal')
        elif self.isolated(name):
            row = self.store.extension_version(name)
            self.check_record(row)
            validate_arguments(row['manifest']['input_schema'], arguments)

    def fingerprint(self, name, arguments):
        target = arguments['name'] if name in ('create_tool', 'rollback_tool') else name
        active = self.store.extension_active_version(target)
        result = {'name': target, 'active_version': active}
        if active:
            row = self.store.extension_version(target, active)
            result['active_digest'] = digest({'manifest': row['manifest'], 'code': row['code'], 'status': row['status']})
        if name == 'rollback_tool':
            row = self.store.extension_version(target, arguments['version'])
            result['target_digest'] = digest({'manifest': row['manifest'], 'code': row['code'], 'status': row['status'], 'test_result': row['test_result']})
        return {'extension': result}

    def check_record(self, row):
        try:
            self._check_record(row)
        except (KeyError, TypeError, AttributeError) as e:
            raise ValueError('Stored extension manifest is malformed; fail closed') from e

    def _check_record(self, row):
        manifest = row['manifest']
        valid_name(row['name'])
        if row['name'] in self.reserved:
            raise ValueError('Stored extension collides with a reserved/core capability')
        if row['status'] != 'tested' or not row['test_result'] or not row['test_result'].get('ok'):
            raise ValueError('Untested extension cannot be activated or invoked')
        if manifest.get('contract') != CONTRACT or manifest.get('code_sha256') != hashlib.sha256(row['code'].encode()).hexdigest():
            raise ValueError('Stored extension integrity/contract mismatch')
        schema = validate_creation({'name': row['name'], 'description': manifest['description'],
                                    'parameters': manifest['input_schema']['properties'],
                                    'required_args': manifest['input_schema'].get('required', []),
                                    'python_code': row['code'], 'test_arguments': manifest['test']['arguments'],
                                    'expected_result': manifest['test']['expected_result']}, self.reserved)
        if schema != manifest['input_schema'] or manifest['permissions'] != self.permissions():
            raise ValueError('Stored extension schema/permission mismatch')
        if manifest['provenance']['mechanism'] != SOURCE:
            raise ValueError('Stored mechanism provenance mismatch; model URLs cannot establish source ownership')

    @staticmethod
    def permissions():
        return {'network': 'none', 'user_files': 'none', 'continuity': False,
                'operator_approval': 'every_creation_activation_and_invocation',
                'persistent_side_effects': 'none', 'output': 'untrusted_finite_JSON'}

    def manifest_for(self, arguments, schema, producer):
        try:
            run = self.store.run(producer)
            model = run['state'].get('provider', {}).get('model') if run['kind'] == 'chat' else None
        except KeyError:
            model = None
        return {'contract': CONTRACT, 'capability_id': 'local.generated/' + arguments['name'],
                'description': arguments['description'], 'input_schema': schema,
                'output_schema': {}, 'code_sha256': hashlib.sha256(arguments['python_code'].encode()).hexdigest(),
                'engine': 'isolated_stdlib_python_json_only',
                'requirements': ['working Bubblewrap + libseccomp OR prebuilt local Docker worker', 'Linux/WSL2'],
                'resources': dict(LIMITS), 'permissions': self.permissions(),
                'state_owner': 'ARTEMIS canonical Store/Runtime/Execution; no private plugin state',
                'actor_scope': 'operator, this data directory; not production multi-user isolation',
                'provenance': {'mechanism': SOURCE, 'implementation': 'local contribution; provider tag records configuration, not verified authorship or inference',
                               'model': model, 'license': arguments.get('license', 'LicenseRef-Unspecified')},
                'test': {'arguments': arguments['test_arguments'], 'expected_result': arguments['expected_result']},
                'failure': 'structured result/error returned to same run; no automatic retry',
                'cancellation': 'canonical run ID kills worker; uncertain outcomes are never replayed',
                'offline': True}

    def expected_precondition(self, name, arguments):
        expected = getattr(self.tools.local_context, 'expected_precondition', None)
        if expected is not None and self.fingerprint(name, arguments) != expected:
            raise ValueError('Extension version changed since approval; no code executed')

    def producer(self):
        return getattr(self.tools.local_context, 'producer', 'operator')

    def create(self, arguments):
        producer = self.producer()
        schema = validate_creation(arguments, self.reserved)
        expected_version = arguments.get('replace_version', 0)
        with self.tools.lock:
            self.expected_precondition('create_tool', arguments)
            if expected_version != self.store.extension_active_version(arguments['name']):
                raise ValueError('Active version changed before staging')
            row = self.store.stage_extension(arguments['name'], self.manifest_for(arguments, schema, producer),
                                             arguments['python_code'], producer)
        name, version = row['name'], row['version']
        self.runtime.emit('tool', 'Extension staged for isolated test', producer, tool=name, version=version,
                          phase='staged', code_sha256=row['manifest']['code_sha256'])
        result = self.sandbox.execute(row['code'], arguments['test_arguments'], producer)
        if result.get('ok') and digest(result.get('result')) != digest(arguments['expected_result']):
            result.update(ok=False, error='Sandbox test result does not match expected_result')
        self.store.extension_test_result(name, version, result)
        if not result.get('ok'):
            self.runtime.emit('tool', 'Extension test failed; not registered', producer, tool=name, version=version, phase='test_failed')
            return {'ok': False, 'name': name, 'version': version, 'registered': False,
                    'error': result.get('error', 'Sandbox test failed'), 'test': result}
        with self.tools.lock:
            if self.sandbox.cancelled(producer):
                return {'ok': False, 'blocked': True, 'error': 'Run cancelled; tested code was not activated', 'test': result}
            # Concurrent proposals cannot overwrite a version activated during testing.
            self.store.activate_extension(name, version, expected_version)
            self.install(self.store.extension_version(name, version))
        self.runtime.emit('tool', 'Sandbox-tested extension hot-registered', producer,
                          tool=name, version=version, phase='registered', contract=CONTRACT)
        return {'ok': True, 'name': name, 'version': version, 'registered': True,
                'test': result, 'contract': CONTRACT, 'next': 'Invoke ' + name + ' in this same running conversation; invocation requires its own approval.'}

    def install(self, row):
        self.check_record(row)
        name = row['name']
        self.tools.registry.add(Tool(name, row['manifest']['description'], row['manifest']['input_schema'],
                                    lambda arguments, name=name: self.use(name, arguments), True, 'generated'))
        self.sync_availability()

    def use(self, name, arguments):
        with self.tools.lock:
            self.expected_precondition(name, arguments)
            row = self.store.extension_version(name)
            self.check_record(row)
            validate_arguments(row['manifest']['input_schema'], arguments)
        # Version snapshot is immutable. A later activation never changes code in flight.
        result = self.sandbox.execute(row['code'], arguments, self.producer())
        return {**result, 'tool': name, 'version': row['version'], 'code_sha256': row['manifest']['code_sha256']}

    def rollback(self, arguments):
        with self.tools.lock:
            self.expected_precondition('rollback_tool', arguments)
            self.validate('rollback_tool', arguments)
            row = self.store.extension_version(arguments['name'], arguments['version'])
            self.store.activate_extension(row['name'], row['version'], arguments['expected_version'])
            self.install(row)
        self.runtime.emit('tool', 'Tested extension version activated by approval', self.producer(),
                          tool=row['name'], version=row['version'], phase='rollback')
        return {'ok': True, 'name': row['name'], 'version': row['version'], 'registered': True,
                'replayed_actions': False}

    def catalogue(self):
        return {'contract': CONTRACT, 'health': self.sandbox.available(), 'load_errors': self.load_errors,
                'versions': [{k: v for k, v in row.items() if k != 'code'} |
                             {'active': self.store.extension_active_version(row['name']) == row['version']}
                             for row in self.store.extension_versions()]}

    def export(self, name):
        valid_name(name)
        row = self.store.extension_version(name)
        self.check_record(row)
        m = row['manifest']
        return {'contract': CONTRACT, 'manifest': m,
                'proposal': {'name': row['name'], 'description': m['description'],
                             'parameters': m['input_schema']['properties'],
                             'required_args': m['input_schema'].get('required', []),
                             'python_code': row['code'], 'test_arguments': m['test']['arguments'],
                             'expected_result': m['test']['expected_result'],
                             'license': m['provenance']['license']}}
