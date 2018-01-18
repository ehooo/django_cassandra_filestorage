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
from django_cassandra_filestorage.models import CassandraFile

from django.core.files.storage import Storage
from django.core.files.base import File
from django.db.models.fields.files import FieldFile

from datetime import datetime
from StringIO import StringIO
import os


def _clean_name(name):
    # Useful for windows' paths
    path = os.path.normpath(name).replace('\\', '/')
    ret = {'name': os.path.basename(path), 'directory': os.path.dirname(path)}
    ret['parent_directory'] = os.path.dirname(ret['directory'])
    return ret


class CassandraStorage(Storage):
    def _open(self, name, mode='rb'):
        assert name, "The name argument is not allowed to be empty."
        return CassandraStorageFile(name, mode=mode)

    def _save(self, name, content):
        assert name, "The name argument is not allowed to be empty."
        f = CassandraStorageFile(name, mode='wb')
        f.write(content)
        f.close()
        return f.name

    def path(self, name):
        assert name, "The name argument is not allowed to be empty."
        raise NotImplementedError("This backend doesn't support absolute paths.")

    def url(self, name):
        assert name, "The name argument is not allowed to be empty."
        # TODO check from settings
        raise NotImplementedError("This backend doesn't support absolute paths.")

    def delete(self, name):
        assert name, "The name argument is not allowed to be empty."
        try:
            CassandraFile.objects.get(**_clean_name(name)).delete()
        except CassandraFile.DoesNotExist:
            raise IOError('File not found')

    def exists(self, name):
        assert name, "The name argument is not allowed to be empty."
        return CassandraFile.objects.filter(**_clean_name(name)).count() > 0

    def listdir(self, path):
        assert path, "The path argument is not allowed to be empty."
        raise NotImplementedError("This backend doesn't support absolute paths.")
        directories, files = [], []
        # TODO
        clean_name = _clean_name(path)
        CassandraFile.objects.filter(directory=clean_name['directory'])
        CassandraFile.objects.filter(parent_directory=clean_name['directory'])
        return directories, files

    def size(self, name):
        assert name, "The name argument is not allowed to be empty."
        return CassandraStorageFile(name).size

    def accessed_time(self, name):
        assert name, "The name argument is not allowed to be empty."
        return CassandraStorageFile(name).accessed_time

    def created_time(self, name):
        assert name, "The name argument is not allowed to be empty."
        return CassandraStorageFile(name).created_time

    def modified_time(self, name):
        assert name, "The name argument is not allowed to be empty."
        return CassandraStorageFile(name).modified_time


class CassandraStorageFile(File):
    def __init__(self, name_or_file, mode='rb'):
        self.file = StringIO()
        self._model = name_or_file
        self._is_new = True
        if isinstance(name_or_file, CassandraFile):
            if self._model.raw:
                self.file.write(self._model.raw)
                self._is_new = False
        else:
            try:
                self._model = CassandraFile.objects.get(**_clean_name(name_or_file))
                if 'w' not in self._mode:
                    self.file.write(self._model.raw)
                    self._is_new = False
            except CassandraFile.DoesNotExist:
                self._model = CassandraFile(**_clean_name(name_or_file))
        self._mode = mode
        self._is_dirty = False

    @property
    def name(self):
        return self._model.name

    @property
    def size(self):
        return self._model.size

    def __len__(self):
        return self.file.len

    @property
    def encoding(self):
        return self._model.encoding

    @encoding.setter
    def encoding(self, encoding):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        self._model.encoding = encoding
        self._is_dirty = True

    @property
    def accessed_time(self):
        return self._model.accessed_time

    @property
    def created_time(self):
        return self._model.created_time

    @property
    def modified_time(self):
        return self._model.modified_time

    def read(self, n=-1):
        self._model.update(accessed_time=datetime.utcnow())
        return self.file.read(n)

    def write(self, content):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        if isinstance(content, FieldFile):
            self._model.content_type = content.file.content_type
            content = content.file.read()
        self.file.write(content)
        self._is_dirty = True

    def writelines(self, iterable):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        self.file.writelines(iterable)
        self._is_dirty = True

    def close(self):
        if self._is_dirty:
            if not self._is_new:
                self._model.update(raw=self.file.getvalue())
            else:
                self._model.raw = self.file.getvalue()
                self._model.save()
        self.file.close()

    @property
    def md5(self):
        return self._model.md5

    @property
    def sha1(self):
        return self._model.sha1

    @property
    def sha256(self):
        return self._model.sha256

    @property
    def sha512(self):
        return self._model.sha512

