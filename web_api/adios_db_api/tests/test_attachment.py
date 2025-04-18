"""
Functional tests for the Model Web API

FIXME: We should have tests that test the API, not everything else!
"""
import copy
from pathlib import Path
import base64

import pytest

from .base import FunctionalTestBase
from .sample_oils import basic_noaa_fm

HERE = Path(__file__)
ATTACHMENTS_DATA = HERE.parent / 'data_for_testing' / 'example_attachments'
olive_oil_path = ATTACHMENTS_DATA / 'GC-Extra-Virgin-Olive-Oil.png'


class AttachmentTestBase(FunctionalTestBase):
    """
    This class just defines some functions for evaluating parts of the oil
    content.  They are not pytests in and of themselves, but return a
    valid status.

    For right now I think we will be following the jsonapi communication
    standard.  Not sure if it fits well for big files, but we can change it
    if we run into problems.
    """
    def jsonapi_request(self, attachment_obj):
        json_obj = {'data': {'attributes': attachment_obj}}

        json_obj['data']['type'] = 'attachments'

        return json_obj

    def jsonapi_to_attachment(self, jsonapi_obj):
        attachment_obj = jsonapi_obj['data']['attributes']
        return attachment_obj


class AttachmentTests(AttachmentTestBase):
    oil_id = 'AD012345'

    def test_get_no_id(self):
        """
        This request should result in an empty list,
        so that's all we can test for
        """
        self.testapp.get('/attachments', status=404)
        self.testapp.get('/attachments/', status=404)

    def test_get_invalid_id(self):
        # malformed url
        self.testapp.get(f'/attachments/AD01234/bogus_file.txt', status=307)

        # oil_id is not found
        self.testapp.get(f'/attachments/AD01234/bogus_file.txt/', status=404)

        new_oil_payload = copy.deepcopy(basic_noaa_fm)
        del new_oil_payload['oil_id']

        resp = self.testapp.post_json(
            '/oils/',
            params=self.jsonapi_request(new_oil_payload)
        )
        oil = resp.json_body
        oil_id = oil['data']['_id']

        # oil exists, but attachment is not found
        self.testapp.get(f'/attachments/{oil_id}/bogus_file.txt/', status=404)

    def test_post_no_associated_oil(self):
        """
        We can't add an attachment unless there is an associated oil.
        So we expect a 404 not found.
        """
        self.testapp.post('/attachments', status=404)
        self.testapp.post('/attachments/', status=404)

        self.testapp.post(f'/attachments/{self.oil_id}/', status=404)

    def test_post_no_filename(self):
        """
        We have an associated oil_id, so we don't fail with a 404,
        but we don't have a filename, so it is a bad request (400).
        """
        new_oil_payload = copy.deepcopy(basic_noaa_fm)
        del new_oil_payload['oil_id']

        resp = self.testapp.post_json(
            '/oils/',
            params=self.jsonapi_request(new_oil_payload)
        )
        oil = resp.json_body
        oil_id = oil['data']['_id']

        self.testapp.post(
            f'/attachments/{oil_id}/',
            upload_files=[(
                'filename',
                olive_oil_path.name,
                open(olive_oil_path, 'rb').read(),
            )],
            status=400,
        )

    def test_post_no_payload(self):
        """
        We have an associated oil_id, so we don't fail with a 404,
        but we don't have a payload, so it is a bad request (400).
        """
        new_oil_payload = copy.deepcopy(basic_noaa_fm)
        del new_oil_payload['oil_id']

        resp = self.testapp.post_json(
            '/oils/',
            params=self.jsonapi_request(new_oil_payload)
        )
        oil = resp.json_body
        oil_id = oil['data']['_id']

        self.testapp.post(
            f'/attachments/{oil_id}/',
            headers={'filename': olive_oil_path.name, },
            status=400,
        )

    def test_post_new_id(self):
        """
        We have an associated oil_id and a valid file attachment to upload,
        so we should succeed.  Check that the attachment was created.
        """
        new_oil_payload = copy.deepcopy(basic_noaa_fm)
        del new_oil_payload['oil_id']

        resp = self.testapp.post_json(
            '/oils/',
            params=self.jsonapi_request(new_oil_payload)
        )
        oil = resp.json_body
        oil_id = oil['data']['_id']

        self.testapp.post(
            f'/attachments/{oil_id}/',
            headers={'filename': olive_oil_path.name, },
            upload_files=[(
                'filename',
                olive_oil_path.name,
                open(olive_oil_path, 'rb').read(),
            )],
            status=200,
        )

        resp = self.testapp.get(f'/attachments/{oil_id}/')
        assert olive_oil_path.name == resp.json_body[0]['filename']

    def test_post_new_id_with_comments(self):
        """
        We have an associated oil_id and a valid file attachment to upload,
        so we should succeed.  Check that the attachment was created.
        """
        new_oil_payload = copy.deepcopy(basic_noaa_fm)
        del new_oil_payload['oil_id']

        resp = self.testapp.post_json(
            '/oils/',
            params=self.jsonapi_request(new_oil_payload)
        )
        oil = resp.json_body
        oil_id = oil['data']['_id']

        comments = 'Olive Oil Comment'
        encoded_comments = base64.b64encode(
            comments.encode('utf-8')
        ).decode('utf-8')

        self.testapp.post(
            f'/attachments/{oil_id}/',
            headers={
                'filename': olive_oil_path.name,
                'comments': encoded_comments
            },
            upload_files=[(
                'filename',
                olive_oil_path.name,
                open(olive_oil_path, 'rb').read(),
            )],
            status=200,
        )

        resp = self.testapp.get(f'/attachments/{oil_id}/')
        assert olive_oil_path.name == resp.json_body[0]['filename']
        assert resp.json_body[0]['comments'] == comments

    @pytest.mark.skipif(reason="Still having problems decoding the response")
    def test_get_valid_id(self):
        """
        We have an associated oil_id and a valid file attachment to upload,
        so we should succeed.  Check that the attachment was created.

        Then we try to download the attachment.
        """
        new_oil_payload = copy.deepcopy(basic_noaa_fm)
        del new_oil_payload['oil_id']

        resp = self.testapp.post_json(
            '/oils/',
            params=self.jsonapi_request(new_oil_payload)
        )
        oil = resp.json_body
        oil_id = oil['data']['_id']

        self.testapp.post(
            f'/attachments/{oil_id}/',
            headers={'filename': olive_oil_path.name, },
            upload_files=[(
                'filename',
                olive_oil_path.name,
                olive_oil_path.open('rb').read(),
            )],
            status=200,
        )

        resp = self.testapp.get(f'/attachments/{oil_id}/')
        assert olive_oil_path.name == resp.json_body[0]['filename']

        # now we download the actual attachment
        resp = self.testapp.get(
            f'/attachments/{oil_id}/',
            headers={'filename': olive_oil_path.name, },
        )

        # We should be getting the file contents here to compare with our
        # test file, but all we get in the response body is some header
        # information (filename, conteht_type, length, ...), not the entire
        # file.
        # The GET request/response works with no problems on the client,
        # so there must be something special we need to do here with the
        # response.
        print('resp = ', resp)
        print(f'{resp.body=}')

    def test_delete_bad_req(self):
        """
        In our attachments API, deletes of non-existent files are considered
        successful so we always return None
        """
        # an oil_id is required, otherwise we get a 404 not found
        self.testapp.delete('/attachments/', status=404)

        # deletes of non-existent files are considered successful,
        # so we always return a normal response.
        self.testapp.delete('/attachments/bogus_id/', status=200)
        self.testapp.delete('/attachments/bogus_id/bogus_file', status=200)

    def test_delete_valid_id(self):
        """
        We have an associated oil_id and a valid file attachment to upload,
        so we should succeed.  Check that the attachment was created.
        Then check that the attachment was deleted.
        """
        new_oil_payload = copy.deepcopy(basic_noaa_fm)
        del new_oil_payload['oil_id']

        resp = self.testapp.post_json(
            '/oils/',
            params=self.jsonapi_request(new_oil_payload)
        )
        oil = resp.json_body
        oil_id = oil['data']['_id']

        self.testapp.post(
            f'/attachments/{oil_id}/',
            headers={'filename': olive_oil_path.name, },
            upload_files=[(
                'filename',
                olive_oil_path.name,
                open(olive_oil_path, 'rb').read(),
            )],
            status=200,
        )

        resp = self.testapp.get(f'/attachments/{oil_id}/')
        assert olive_oil_path.name == resp.json_body[0]['filename']

        self.testapp.delete(
            f'/attachments/{oil_id}/{olive_oil_path.name}',
            status=200
        )

        resp = self.testapp.get(f'/attachments/{oil_id}/')
        assert len(resp.json_body) == 0

    def test_put_bad_req(self):
        """
        There are too many combinations of possible bad requests to represent
        here, but we will do the obvious ones and add to this as the need
        arises.
        """
        self.testapp.put('/attachments', params=[], status=404)
        self.testapp.put('/attachments/', params=[], status=404)
        self.testapp.put('/attachments/', params='asdf', status=404)

        self.testapp.put('/attachments/', params={"bad": 'attr'}, status=404)

    def test_put_no_payload(self):
        """
        We have an associated oil_id and an inserted attachment, so we don't
        fail with a 404.
        But we don't have a payload with our PUT request, so it is a
        bad request (400).
        """
        new_oil_payload = copy.deepcopy(basic_noaa_fm)
        del new_oil_payload['oil_id']

        # First insert the oil
        resp = self.testapp.post_json(
            '/oils/',
            params=self.jsonapi_request(new_oil_payload)
        )
        oil = resp.json_body
        oil_id = oil['data']['_id']

        # Next insert the attachment
        self.testapp.post(
            f'/attachments/{oil_id}/',
            headers={'filename': olive_oil_path.name, },
            upload_files=[(
                'filename',
                olive_oil_path.name,
                open(olive_oil_path, 'rb').read(),
            )],
            status=200,
        )

        resp = self.testapp.get(f'/attachments/{oil_id}/')
        assert olive_oil_path.name == resp.json_body[0]['filename']
        assert 'comments' not in resp.json_body[0]

        comments = 'Olive Oil Comment'
        encoded_comments = base64.b64encode(
            comments.encode('utf-8')
        ).decode('utf-8')

        # Next update the attachment with a PUT, but with no payload
        self.testapp.put(
            f'/attachments/{oil_id}/',
            headers={'filename': olive_oil_path.name,
                     'comments': encoded_comments},
            status=400,
        )

    def test_put_valid_id(self):
        new_oil_payload = copy.deepcopy(basic_noaa_fm)
        del new_oil_payload['oil_id']

        # First insert the oil
        resp = self.testapp.post_json(
            '/oils/',
            params=self.jsonapi_request(new_oil_payload)
        )
        oil = resp.json_body
        oil_id = oil['data']['_id']

        # Next insert the attachment
        self.testapp.post(
            f'/attachments/{oil_id}/',
            headers={'filename': olive_oil_path.name, },
            upload_files=[(
                'filename',
                olive_oil_path.name,
                open(olive_oil_path, 'rb').read(),
            )],
            status=200,
        )

        resp = self.testapp.get(f'/attachments/{oil_id}/')
        assert olive_oil_path.name == resp.json_body[0]['filename']
        assert 'comments' not in resp.json_body[0]

        comments = 'Olive Oil Comment'
        encoded_comments = base64.b64encode(
            comments.encode('utf-8')
        ).decode('utf-8')

        # Next update the attachment with a PUT
        self.testapp.put(
            f'/attachments/{oil_id}/',
            headers={
                'filename': olive_oil_path.name,
                'comments': encoded_comments,
            },
            upload_files=[(
                'filename',
                olive_oil_path.name,
                open(olive_oil_path, 'rb').read(),
            )],
            status=200,
        )

        resp = self.testapp.get(f'/attachments/{oil_id}/')
        assert olive_oil_path.name == resp.json_body[0]['filename']
        assert resp.json_body[0]['comments'] == comments
