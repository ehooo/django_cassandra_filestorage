Django Cassandra Filestorage
============================
Use Cassandra as File Storage in Django

License
-------

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


Install
-------
```
pip install https://github.com/ehooo/django_cassandra_filestorage.git
```

Getting Started on your local machine
-------------------------------------
```
# Install cassandra
echo "deb http://www.apache.org/dist/cassandra/debian 21x main" | sudo tee -a /etc/apt/sources.list.d/cassandra.list
echo "# deb http://www.apache.org/dist/cassandra/debian 21x main" | sudo tee -a /etc/apt/sources.list.d/cassandra.list

sudo gpg --keyserver pgp.mit.edu --recv-keys F758CE318D77295D
sudo gpg --export --armor F758CE318D77295D | sudo apt-key add -
sudo gpg --keyserver pgp.mit.edu --recv-keys 2B5C1B00
sudo gpg --export --armor 2B5C1B00 | sudo apt-key add -
sudo gpg --keyserver pgp.mit.edu --recv-keys 0353B12C
sudo gpg --export --armor 0353B12C | sudo apt-key add -

sudo apt-get update -y -qq
sudo apt-get install cassandra -y -qq

# Create Database
cqlsh 127.0.0.1
cqlsh> CREATE KEYSPACE dbname WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };
```
For remote access ``sudo nano /etc/cassandra/cassandra.yaml`` and
change ``seeds``, ``listen_address`` and/or ``rpc_address`` if it's needed; also see about 
[Firewall](http://www.datastax.com/documentation/cassandra/2.0/cassandra/security/secureFireWall_r.html) and configure
the [Authentication](http://www.datastax.com/documentation/cassandra/2.0/cassandra/security/security_config_native_authenticate_t.html)

Usage
-----
1. Add django_cassandra_filestorage to ``INSTALLED_APPS`` in your settings.py file:

	```
  INSTALLED_APPS += ('django_cassandra_filestorage',)
	```

2. Also create `CASSANDRA_FS` setting:

	```
  CASSANDRA_FS = {
    'NAME': 'dbname',
    'HOST': 'db1.example.com,db2.example.com',
    'OPTIONS': {
      'replication': {
        'strategy_class': 'SimpleStrategy',
        'replication_factor': 1
      }
    }
  }
  ```

3.1 Set as default storage:

  ```
DEFAULT_FILE_STORAGE = 'django_cassandra_filestorage.storage.CassandraStorage'
  ```

3.2 Optional use:

  ```
from django_cassandra_filestorage.storage import CassandraStorage
from django.db import models
fs = CassandraStorage()
class ExampleModel(models.Model):
  file = models.FileField(storage=fs)
  name = models.SlugField(unique=True)
  ```
