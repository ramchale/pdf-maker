from datetime import datetime
from unittest.mock import patch

from hamcrest import assert_that, equal_to
from pdf_maker.pdf import Metadata


def test_encode_metadata():
    result = Metadata.encode_metadata('Some value')

    assert_that(result, equal_to(b'(\xFE\xFF\x00S\x00o\x00m\x00e\00 \00v\00a\00l\00u\00e)'))


@patch('pdf_maker.pdf.Metadata.get_time_stamp')
def test_metadata_str(mock):
    mock.return_value = datetime(2010, 10, 8)

    result = str(Metadata(23, 'Title', 'Creator'))

    assert_that(result, equal_to('23 0 obj\n' \
                                 '<<\n' \
                                 '  /Title (Title)\n' \
                                 '  /Creator (Creator)\n' \
                                 '  /Producer (PyPdf)\n' \
                                 '  /CreationDate (D: D20101008000000Z)\n' \
                                 '>>\n' \
                                 'endobj'))


@patch('pdf_maker.pdf.Metadata.get_time_stamp')
def test_metadata_bytes(mock):
    mock.return_value = datetime(2010, 10, 8)

    result = bytes(Metadata(23, 'Title', 'Creator'))

    assert_that(result, equal_to(b'23 0 obj\n' \
                                 b'<<\n' \
                                 b'  /Title (\xFE\xFF\x00T\x00i\x00t\x00l\x00e)\n' \
                                 b'  /Creator (\xFE\xFF\x00C\x00r\x00e\x00a\x00t\x00o\x00r)\n' \
                                 b'  /Producer (\xFE\xFF\x00P\x00y\x00P\x00d\x00f)\n' \
                                 b'  /CreationDate (D: D20101008000000Z)\n' \
                                 b'>>\n' \
                                 b'endobj'))