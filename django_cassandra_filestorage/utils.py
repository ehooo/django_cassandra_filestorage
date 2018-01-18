"""
    Copyright (C) 2018 [Victor Torre](https://github.com/ehooo)

    Licensed under the Apache License, Version 2.0 (the "License"); you may not
    use this file except in compliance with the License. You may obtain a copy of
    the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations under
    the License.
"""
from cassandra.auth import PlainTextAuthProvider
from cqlengine import connection


def cassandra_connect(config):
    if connection.cluster is not None:
        return
    host = config.get('HOST').split(',')
    keyspace = config.get('NAME')
    password = config.get('PASSWORD')
    user = config.get('USER')
    options = config.get('OPTIONS', {})
    connection_options = options.get('connection', {})

    if user and password and 'auth_provider' not in connection_options:
        connection_options['auth_provider'] = PlainTextAuthProvider(username=user, password=password)

    connection.setup(host, keyspace, **connection_options)
    # TODO check si existe "keyspace" y la tabla para los ficheros

    session_options = options.get('session', {})
    session = connection.get_session()
    for option, value in session_options.iteritems():
        setattr(session, option, value)


def cassandra_disconnect():
    session = connection.get_session()
    if session:
        session.shutdown()
    cluster = connection.get_cluster()
    if cluster:
        cluster.shutdown()
    connection.session = None
    connection.lazy_connect_args = None
    connection.default_consistency_level = None

