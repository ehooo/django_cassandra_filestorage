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
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseNotModified
from django.http import StreamingHttpResponse
from django_cassandra_filestorage.storage import CassandraStorage
from django.core.servers.basehttp import FileWrapper
import os
import zipfile
import tempfile


def download(request, filename, encoding=None, default_encoding='application/octet-stream',
             ziped=False, stream=True, blksize=8192):
    fs = CassandraStorage()
    if not fs.exists(filename):
        raise Http404
    request_file = fs.open(filename)

    last_mod = request_file.modified_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
    etag = request_file.md5
    mod_since = request.META.get('HTTP_IF_MODIFIED_SINCE')
    old_etag = request.META.get('HTTP_IF_NONE_MATCH')
    if last_mod == mod_since or etag == old_etag:
        return HttpResponseNotModified()

    basename = os.path.basename(filename)
    size_file = request_file.size
    if not encoding:
        encoding = default_encoding
        if request_file.encoding:
            encoding = request_file.encoding

    if ziped:
        encoding = 'application/zip'
        zip_file = tempfile.TemporaryFile()
        archive = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
        archive.writestr(basename, request_file.read())
        archive.close()
        request_file.close()
        request_file = FileWrapper(zip_file, blksize=blksize)
        basename += '.zip'
        size_file = zip_file.tell()
        zip_file.seek(0)
    else:
        request_file = FileWrapper(request_file, blksize=blksize)

    response_class = HttpResponse
    if stream:
        response_class = StreamingHttpResponse

    response = response_class(request_file, content_type=encoding)
    response['Content-Disposition'] = 'attachment; filename=' + basename
    response['Content-Length'] = size_file
    response['Last-Modified'] = last_mod
    response['Etag'] = etag
    return response
