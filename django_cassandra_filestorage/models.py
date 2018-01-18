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
from cqlengine import columns
from cqlengine.models import Model
from cqlengine.management import sync_table

from django.conf import settings
from django.core.files.base import File

from datetime import datetime
from StringIO import StringIO
import hashlib
import uuid

from django_cassandra_filestorage.utils import cassandra_connect


class CassandraRawFile(Model):  # TODO
    raw = columns.Bytes(required=True)
    size = columns.BigInt(required=True)

    md5 = columns.Text(max_length=32, min_length=32, required=True, index=True)
    sha1 = columns.Text(max_length=40, min_length=40, required=True, index=True)
    sha256 = columns.Text(max_length=64, min_length=64, required=True, index=True)
    sha512 = columns.Text(max_length=128, min_length=128, required=True, index=True)

    encoding = columns.Text(default=None, index=True)
    content_type = columns.Text(default=None, index=True)

    def save(self):
        self.md5 = hashlib.md5(self.raw).hexdigest()
        self.sha1 = hashlib.sha1(self.raw).hexdigest()
        self.sha256 = hashlib.sha256(self.raw).hexdigest()
        self.sha512 = hashlib.sha512(self.raw).hexdigest()
        self.size = len(self.raw)
        return super(CassandraRawFile, self).save()

    def update(self, **values):
        if 'raw' in values:
            md5 = hashlib.md5()
            sha1 = hashlib.sha1()
            sha256 = hashlib.sha256()
            sha512 = hashlib.sha512()
            if isinstance(values['raw'], File):
                f = StringIO()
                data = values['raw'].chunks()
                while f:
                    f.write(data)
                    md5.update(data)
                    sha1.update(data)
                    sha256.update(data)
                    sha512.update(data)
                    data = values['raw'].chunks()
                values['size'] = f.tell()
                f.seek(0)
                values['raw'] = f.getvalue()
                f.close()
            else:
                md5.update(values['raw'])
                sha1.update(values['raw'])
                sha256.update(values['raw'])
                sha512.update(values['raw'])
                values['size'] = len(values['raw'])
            values['md5'] = md5.hexdigest()
            values['sha1'] = sha1.hexdigest()
            values['sha256'] = sha256.hexdigest()
            values['sha512'] = sha512.hexdigest()
        return super(CassandraRawFile, self).update(**values)


class CassandraFile(Model):
    __table_name__ = 'django_cassandra_filestorage'

    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    directory = columns.Text(required=True, index=True)
    parent_directory = columns.Text(required=True, index=True)
    name = columns.Text(required=True, index=True)

    sha512 = columns.Text(max_length=128, min_length=128, required=True, index=True)

    created_time = columns.DateTime(required=True, default=datetime.utcnow())
    accessed_time = columns.DateTime(required=True, default=datetime.utcnow())
    modified_time = columns.DateTime(required=True, default=datetime.utcnow())

    def save(self):
        self.accessed_time = datetime.utcnow()
        self.modified_time = datetime.utcnow()
        return super(CassandraFile, self).save()

    def update(self, **values):
        values['accessed_time'] = datetime.utcnow()
        values['modified_time'] = datetime.utcnow()
        return super(CassandraFile, self).update(**values)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, CassandraFile):
            if self.sha512 == other.sha512:
                return True
        elif isinstance(other, File):
            hash = hashlib.sha512()
            data = other.chunks()
            while data:
                hash.update(data)
                data = other.chunks()
            if self.sha512 == hash.hexdigest():
                return True
        return False

if hasattr(settings, 'CASSANDRA_FS'):
    cassandra_connect(settings.CASSANDRA_FS)
    sync_table(CassandraFile)
