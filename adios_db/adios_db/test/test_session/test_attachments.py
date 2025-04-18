from pathlib import Path

import pytest

from adios_db.models.oil.oil import Oil

# we don't want this to fail if these tests are
# skipped and pymongo is not there.
try:
    import pymongo
except ModuleNotFoundError:
    print("pymongo module not there -- not importing the session modules")
    PYMONGO = False
else:
    PYMONGO = True
    from adios_db.util.db_connection import connect_mongodb

from .session_test_base import SessionTestBase

HERE = Path(__file__).parent
ATTACHMENTS_DATA = HERE.parent / 'data_for_testing' / 'example_attachments'
olive_oil_path = ATTACHMENTS_DATA / 'GC-Extra-Virgin-Olive-Oil.png'
olive_oil_path = olive_oil_path.as_posix()

# Pass the --mongo command line option if you want these to run.
# they require a mongo database to be running on localhost
pytestmark = pytest.mark.mongo


def test_pymongo():
    """
    Tests to see if pymongo got imported Not really a test, but it should serve
    to give folks a reasonable error message if they try to run the mongo tests
    without pymongo
    """
    assert PYMONGO, "The pymongo package needs to be installed in order to run the mongo tests"


class TestAttachmentsCRUD(SessionTestBase):
    """
    Testing the CRUD operations of our session class
    """
    def get_attachment_obj(self):
        session = connect_mongodb(self.settings)
        return session.attachments

    def test_init(self):
        attachments = self.get_attachment_obj()

        # we'll improve our test as we flesh out the class a bit more.
        assert hasattr(attachments, 'attachment_file_path')
        assert hasattr(attachments, 'find_one')

    def test_file_path(self):
        attachments = self.get_attachment_obj()

        file_path = attachments.attachment_file_path('AD01234',
                                                     'file_attachment.pdf')
        prefix, oil_id, filename = file_path.split('/')

        assert prefix == 'AD'
        assert oil_id == 'AD01234'
        assert filename == 'file_attachment.pdf'

    @pytest.mark.parametrize('filename, expected', [
        ('file_attachment.pdf', 'application/pdf'),
        ('file_attachment.jpg', 'image/jpeg'),
        ('file_attachment.csv', 'text/csv'),
        ('file_attachment.xls', 'application/vnd.ms-excel'),
        ('file_attachment.xlsx',
         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    ])
    def test_get_content_type(self, filename, expected):
        attachments = self.get_attachment_obj()

        content_type = attachments.get_content_type(filename)
        assert content_type == expected

    def test_list(self):
        attachments = self.get_attachment_obj()
        testfile = Path(olive_oil_path).name

        ret = attachments.list()
        assert len(ret) == 0

        with open(olive_oil_path, 'rb') as file_obj:
            inserted_id = attachments.insert_one('AD01234',
                                                 olive_oil_path,
                                                 file_obj=file_obj)
            print(f'{inserted_id=}')
            assert type(inserted_id).__name__ == 'ObjectId'

        ret = attachments.list()
        assert len(ret) == 1

    def test_find_oil_attachments(self):
        attachments = self.get_attachment_obj()
        testfile = Path(olive_oil_path).name

        with open(olive_oil_path, 'rb') as file_obj:
            inserted_id = attachments.insert_one('AD01234',
                                                 olive_oil_path,
                                                 file_obj=file_obj,
                                                 comments='Olive Oil Comment')

            print(f'{inserted_id=}')
            assert type(inserted_id).__name__ == 'ObjectId'

        ret = attachments.find_oil_attachments('AD01234')

        print(f'test_find_oil_attachments(): {ret=}')
        assert len(ret) == 1
        assert ret[0]['comments'] == 'Olive Oil Comment'

    def test_insert_one_bad_file(self):
        attachments = self.get_attachment_obj()

        with pytest.raises(ValueError):
            _result = attachments.insert_one('AD01234', olive_oil_path,
                                             file_obj='invalid_file_obj')

        with pytest.raises(FileNotFoundError):
            _result = attachments.insert_one('AD01234', 'bogus_path')

    def test_insert_one(self):
        attachments = self.get_attachment_obj()
        testfile = Path(olive_oil_path).name

        with open(olive_oil_path, 'rb') as file_obj:
            inserted_id = attachments.insert_one('AD01234',
                                                 olive_oil_path,
                                                 file_obj=file_obj)
            print(f'{inserted_id=}')
            assert type(inserted_id).__name__ == 'ObjectId'

        # subsequent inserts should clobber the previous matching file
        # and re-use its ID.
        inserted_id2 = attachments.insert_one('AD01234', olive_oil_path)
        print(f'{inserted_id2=}')
        assert type(inserted_id2).__name__ == 'ObjectId'
        assert inserted_id2 == inserted_id

        # We should only have one file matching our test file after
        # inserting the same file twice.
        assert len([f for f in attachments.list() if testfile in f]) == 1

    def test_insert_one_with_comment(self):
        attachments = self.get_attachment_obj()
        testfile = Path(olive_oil_path).name

        # Inserting a file for the first time returns an ID
        # we use a with/open to pass in an open file object
        with open(olive_oil_path, 'rb') as file_obj:
            inserted_id = attachments.insert_one('AD01234',
                                                 olive_oil_path,
                                                 file_obj=file_obj,
                                                 comments='Olive Oil Comment')
            print(f'{inserted_id=}')
            assert type(inserted_id).__name__ == 'ObjectId'

        file_obj = attachments.find_one(file_id=inserted_id)

        assert hasattr(file_obj, 'comments')
        assert file_obj.comments == 'Olive Oil Comment'

    def test_replace_one(self):
        attachments = self.get_attachment_obj()
        testfile = Path(olive_oil_path).name

        # Inserting a file for the first time returns an ID
        inserted_id = attachments.insert_one('AD01234', olive_oil_path)
        print(f'{inserted_id=}')
        assert type(inserted_id).__name__ == 'ObjectId'

        # subsequent replacements should clobber the previous matching file
        # and re-use its ID.
        updated_id = attachments.replace_one('AD01234', olive_oil_path)
        print(f'{updated_id=}')
        assert type(updated_id).__name__ == 'ObjectId'
        assert updated_id == inserted_id

        # We should only have one file matching our test file after
        # inserting the same file twice.
        assert len([f for f in attachments.list() if testfile in f]) == 1

    def test_replace_one_with_comments(self):
        attachments = self.get_attachment_obj()
        testfile = Path(olive_oil_path).name

        # Inserting a file for the first time returns an ID
        inserted_id = attachments.insert_one('AD01234', olive_oil_path)
        print(f'{inserted_id=}')
        assert type(inserted_id).__name__ == 'ObjectId'

        # subsequent replacements should clobber the previous matching file
        # and re-use its ID.
        updated_id = attachments.replace_one('AD01234', olive_oil_path,
                                             comments='Olive Oil Comment')
        print(f'{updated_id=}')

        file_obj = attachments.find_one(file_id=updated_id)

        assert hasattr(file_obj, 'comments')
        assert file_obj.comments == 'Olive Oil Comment'

    def test_delete_one(self):
        attachments = self.get_attachment_obj()

        testfile = Path(olive_oil_path).name

        # Inserting a file for the first time returns an ID
        inserted_id = attachments.insert_one('AD01234', olive_oil_path)
        print(f'{inserted_id=}')
        assert type(inserted_id).__name__ == 'ObjectId'

        # Deletes of non-existent files are considered successful
        # so we always return None
        result = attachments.delete_one('AD01234', olive_oil_path)
        assert result is None

    def test_find_one(self):
        attachments = self.get_attachment_obj()
        testfile = Path(olive_oil_path).name

        # Inserting a file for the first time returns an ID
        inserted_id = attachments.insert_one('AD01234', olive_oil_path)
        print(f'{inserted_id=}')
        assert type(inserted_id).__name__ == 'ObjectId'

        # Finding a file returns an open-file-like object
        result = attachments.find_one('AD01234', olive_oil_path)
        print(f'{result=}')

        # is there a read method?
        assert callable(getattr(result, 'read', None))

        # Finding non-existent files return a FileNotFoundError
        with pytest.raises(FileNotFoundError):
            _result = attachments.find_one('AD01234', 'bogus_path')

        with pytest.raises(FileNotFoundError):
            _result = attachments.find_one('bogus_oil_id', olive_oil_path)

        with pytest.raises(FileNotFoundError):
            _result = attachments.find_one('bogus_oil_id', 'bogus_path')
