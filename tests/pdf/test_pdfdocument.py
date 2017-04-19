from datetime import datetime
from unittest.mock import patch

from hamcrest import *
from pdf_maker.pdf import Document


@patch('pdf_maker.pdf.Metadata.get_time_stamp')
def test_document_empty_document(mock):
    mock.return_value = datetime(2010, 10, 8)

    expected = b'%PDF-1.4\n' \
               b'1 0 obj\n' \
               b'<<\n' \
               b'  /Title (\xfe\xff)\n' \
               b'  /Creator (\xfe\xff)\n' \
               b'  /Producer (\xfe\xff\x00P\x00y\x00P\x00d\x00f)\n' \
               b'  /CreationDate (D: D20101008000000Z)\n' \
               b'>>\n' \
               b'endobj\n' \
               b'2 0 obj\n' \
               b'<< /Type /Catalog\n' \
               b'   /Outlines 3 0 R\n' \
               b'   /Pages 4 0 R\n' \
               b'>>\n' \
               b'endobj\n' \
               b'3 0 obj\n' \
               b'<< /Type /Outlines\n' \
               b'   /Count 0\n' \
               b'>>\n' \
               b'endobj\n' \
               b'4 0 obj\n' \
               b'<< /Type /Pages\n' \
               b'   /Count 0\n' \
               b'>>\n' \
               b'endobj\n' \
               b'xref\n' \
               b'0 5\n' \
               b'0000000000 65535 f \n' \
               b'0000000009 00000 n \n' \
               b'0000000125 00000 n \n' \
               b'0000000196 00000 n \n' \
               b'0000000245 00000 n \n' \
               b'trailer\n' \
               b'<< /Size 5\n' \
               b'   /Info 1 0 R\n' \
               b'   /Root 2 0 R\n' \
               b'>>\n' \
               b'startxref\n' \
               b'291\n' \
               b'%%EOF'

    document = Document()

    result = bytes(document)

    assert_that(result, equal_to(expected))
