"""
Cornice Oil attachment files services.
"""
import base64
import logging
from pathlib import Path

from cornice import Service
from pyramid.httpexceptions import (HTTPBadRequest,
                                    HTTPNotFound)
from pyramid.response import Response

from adios_db_api.common.views import (cors_policy,
                                       can_modify_db)

logger = logging.getLogger(__name__)

attachment_api = Service(name='attachment',
                         path='/attachments/{oil_id}/*filename',
                         description="List Oil Attachments",
                         cors_policy=cors_policy)


@attachment_api.get()
def get_attachment(request):
    """
    We will do one of two possible things here.
    1. Return a listing of attached files for the specified oil in JSON format.
    2. Return the attached file specified for the specified oil.
    """
    oil_id = request.matchdict.get('oil_id')
    try:
        filename = request.matchdict.get("filename")[0]
    except IndexError:
        filename = None

    logger.info(f'GET /attachments: oil_id: {oil_id}, filename: {filename}')

    if filename is None:
        return get_attachment_list(request, oil_id)
    else:
        return get_attachment_file(request, oil_id, filename)


def get_attachment_list(request, oil_id):
    attachments = request.adb_session.attachments

    def fix_mongo_fields(record):
        # json has trouble serializing datetime & ObjectId types
        record['_id'] = str(record['_id'])
        record['uploadDate'] = record['uploadDate'].isoformat()

        # filename should not have path included
        record['filename'] = Path(record['filename']).name

        return record

    return [fix_mongo_fields(a)
            for a in attachments.find_oil_attachments(oil_id)]


def get_attachment_file(request, oil_id, filename):
    try:
        attachments = request.adb_session.attachments
        with attachments.find_one(oil_id, filename) as file_obj:
            return Response(content_type=file_obj.content_type,
                            content_length=file_obj.length,
                            body_file=file_obj,
                            conditional_response=True)
    except FileNotFoundError:
        logger.error(f'Not found! oil_id: {oil_id}, filename: {filename}')
        raise HTTPNotFound()


@attachment_api.post()
@can_modify_db
def post_attachment(request):
    """
    The oil_id will be a part of the URL, and will be required.

    The filename will be retrieved from the request headers, and will be
    required.

    The reason we don't get it from the URL is that we want the
    filename to be unmodified, and to put it in the URL will require that some
    file names be changed to fit the URL format.
    """
    (oil_id,
     filename,
     comments,
     _fields_only,
     ) = validate_post_put_params(request, 'post')

    try:
        attachments = request.adb_session.attachments

        if comments != '':
            attachments.insert_one(oil_id, filename,
                                   file_obj=request.body_file,
                                   comments=comments)
        else:
            attachments.insert_one(oil_id, filename,
                                   file_obj=request.body_file)
    except FileNotFoundError:
        logger.error(f'Not found! oil_id: {oil_id}, filename: {filename}')
        raise HTTPNotFound()
    except ValueError:
        logger.error(f'Bad request! oil_id: {oil_id}, filename: {filename}')
        raise HTTPBadRequest()


@attachment_api.put()
@can_modify_db
def update_attachment(request):
    """
    The oil_id will be a part of the URL, and will be required

    The filename will be retrieved from the request headers, and will be
    required.

    The reason we don't get it from the URL is that we want the
    filename to be unmodified, and to put it in the URL will require that some
    file names be changed to fit the URL format.
    """
    (oil_id,
     filename,
     comments,
     fields_only,
     ) = validate_post_put_params(request, 'put')

    try:
        if fields_only:
            update_attachment_fields(request, oil_id, filename, comments)
        else:
            update_attachment_file(request, oil_id, filename, comments)
    except FileNotFoundError:
        logger.error(f'Not found! oil_id: {oil_id}, filename: {filename}')
        raise HTTPNotFound()
    except ValueError:
        logger.error(f'Bad request! oil_id: {oil_id}, filename: {filename}')
        raise HTTPBadRequest()


def update_attachment_fields(request, oil_id, filename, comments):
    attachments = request.adb_session.attachments

    if comments != '':
        attachments.replace_fields(oil_id, filename, comments=comments)
    else:
        attachments.replace_fields(oil_id, filename)


def update_attachment_file(request, oil_id, filename, comments):
    attachments = request.adb_session.attachments

    if comments != '':
        attachments.replace_one(oil_id, filename,
                                file_obj=request.body_file,
                                comments=comments)
    else:
        attachments.replace_one(oil_id, filename,
                                file_obj=request.body_file)


def validate_post_put_params(request, req_type):
    content_type = request.content_type

    oil_id = request.matchdict.get('oil_id')
    filename = request.headers.get('filename')

    comments = base64.b64decode(
        request.headers.get('comments', '')
    ).decode('utf-8')  # Assuming UTF-8 encoding

    fields_only = request.headers.get('fields-only', False)
    fields_only = True if fields_only == 'true' else False

    max_file_size = int(request.registry.settings['caps.attachment_max_size'])

    req_type_lu = {
        'post': 'POST',
        'put': 'PUT',
    }

    logger.info(f'{req_type_lu[req_type.lower()]} /attachments: '
                f'{oil_id=}, {filename=}, {content_type=}, '
                f'filesize={len(request.body)}, '
                f'{fields_only=}')

    # look up the oil to see if we are dealing with a good request
    if request.adb_session.find_one(oil_id) is None:
        logger.error(f'Oil not found! oil_id: {oil_id}.  '
                     f'Cannot {req_type_lu[req_type.lower()]} an attachment.')
        raise HTTPNotFound()

    if filename is None:
        logger.error(f'Bad request! filename: {filename}')
        raise HTTPBadRequest()

    if len(request.body) > max_file_size:
        logger.error(f'Bad request! filename: {filename} is too large.  '
                     f'Files must be smaller than {max_file_size} bytes')
        raise HTTPBadRequest()
    elif len(request.body) == 0 and fields_only is False:
        logger.error(f'Bad request! file {filename} has zero length.')
        raise HTTPBadRequest()

    return (oil_id, filename, comments, fields_only)


@attachment_api.delete()
@can_modify_db
def delete_attachment(request):
    """
    In our attachments API, deletes of non-existent files are considered
    successful so we always return None
    """
    oil_id = request.matchdict.get('oil_id')
    try:
        filename = request.matchdict.get("filename")[0]
    except IndexError:
        filename = None

    attachments = request.adb_session.attachments

    logger.info(f'DELETE /attachments: {oil_id=}, {filename=}')

    return attachments.delete_one(oil_id, filename)
