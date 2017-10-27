from datetime import datetime
from enum import Enum
import zlib
import base64

from pdf_maker.font import Font


def decode_base64_and_inflate( b64string ):
    decoded_data = base64.b64decode( b64string )
    return zlib.decompress( decoded_data , -15)


def deflate_and_base64_encode( string_val ):
    zlibbed_str = zlib.compress( string_val )
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode( compressed_string )


class PageSize(Enum):
    """Standard page size width and height in pixels"""
    A0 = (2384, 3370)
    A1 = (1684, 2384)
    A2 = (1191, 1684)
    A3 = (842, 1191)
    A4 = (595, 842)
    A5 = (420, 595)
    A6 = (297, 420)
    A7 = (210, 297)
    A8 = (148, 210)
    A9 = (105, 148)


class Metadata():
    def __init__(self, object_id, title='', creator=''):
        self.object_id = object_id
        self.title = title
        self.creator = creator

    def __str__(self):
        return '{object_id} 0 obj\n' \
               '<<\n' \
               '  /Title ({title})\n' \
               '  /Creator ({creator})\n' \
               '  /Producer ({producer})\n' \
               '  /CreationDate (D: {date}Z)\n' \
               '>>\n' \
               'endobj'.format(object_id=self.object_id,
                               title=self.title,
                               creator=self.creator,
                               producer='PyPdf',
                               date=self.get_time_stamp().strftime('D%Y%m%d%H%M%S')
                               )

    def __bytes__(self):
        return str(self.object_id).encode() + b' 0 obj\n' \
                                              b'<<\n' \
                                              b'  /Title ' + Metadata.encode_metadata(self.title) + b'\n' \
                                                                                                    b'  /Creator ' + Metadata.encode_metadata(
            self.creator) + b'\n' \
                            b'  /Producer ' + Metadata.encode_metadata('PyPdf') + b'\n' \
                                                                                  b'  /CreationDate (D: ' + self.get_time_stamp().strftime(
            'D%Y%m%d%H%M%S').encode() + b'Z)\n' \
                                        b'>>\n' \
                                        b'endobj'

    @staticmethod
    def encode_metadata(s):
        return b'(\xFE\xFF' + s.encode("utf-16-be") + b')'

    def get_time_stamp(self):
        return datetime.now()


class GraphicsState():
    def __init__(self, object_id):
        self.object_id = object_id

    def __str__(self):
        return '{object_id} 0 obj\n' \
               '<< /Type /ExtGState\n' \
               '  /SA true\n' \
               '  /SM 0.02\n' \
               '  /ca 1.0\n' \
               '  /CA 1.0\n' \
               '  /AIS false\n' \
               '  /SMask /None' \
               '>>\n' \
               'endobj\n'.format(object_id=self.object_id)

    def __bytes__(self):
        return str(self).encode()


class PatternColorSpace():
    def __init__(self, object_id):
        self.object_id = object_id

    def __str__(self):
        return '{object_id} 0 obj\n' \
               '[/Pattern /DeviceRGB]\n' \
               'endobj\n'.format(object_id=self.object_id)

    def __bytes__(self):
        return str(self).encode()


class Text():
    def __init__(self, text, font, font_size):
        self.text = text
        self.font = font
        self.font_size = font_size
        self.position = (0, 0)

    def __str__(self):
        return '  BT\n' \
               '    /F{font_id} {font_size} Tf\n' \
               '    {x} {y} Td\n' \
               '    ({text}) Tj\n' \
               '  ET\n'.format(font_id=self.font.object_id,
                               font_size=self.font_size,
                               x=self.position[0],
                               y=self.position[1],
                               text=self.text)


class Content():
    class Encoding(Enum):
        PLAIN_TEXT = 1,
        FLATE = 2

    def __init__(self, object_id):
        self.object_id = object_id
        self.instructions = []
        self.encoding = Content.Encoding.FLATE

    def __str__(self):
        instruction_text = ''

        for i in self.instructions:
            instruction_text += str(i)

        return '{object_id} 0 obj\n' \
               '  << /Length {length} >>\n' \
               '  stream\n' \
               '{text}' \
               '  endstream\n' \
               'endobj\n'.format(object_id=self.object_id, length=len(instruction_text), text=instruction_text)

    def __bytes__(self):
        if(self.encoding == Content.Encoding.PLAIN_TEXT):
            return str(self).encode()
        else:
            instruction_text = ''

            for i in self.instructions:
                instruction_text += str(i)

            res = zlib.compress(instruction_text.encode())

            return '{object_id} 0 obj\n' \
                   '  << /Length {length} \n' \
                   '/Filter /FlateDecode \n' \
                   '>>\n' \
                   '  stream\n'.format(object_id=self.object_id, length=len(res)).encode() + \
                   res + \
                   '  endstream\n' \
                   'endobj\n'.encode()


class Page():
    def __init__(self, document, parent=None):
        self.document = document

        self.document.pages.append(self)

        # use document if no parent specified
        self.parent = document if parent is None else parent

        self.object_id = self.document.get_next_object_id()
        self.page_size = None

        self.content = Content(self.get_next_object_id())

    def __str__(self):
        page_size = self.get_page_size()

        # Get a list of unique font ids used by the content
        unique_font_ids = []

        for instruction in self.content.instructions:
            if type(instruction) is Text:
                if instruction.font.object_id not in unique_font_ids:
                    unique_font_ids.append(instruction.font.object_id)

        result = '{object_id} 0 obj\n' \
                 '<< /Type /Page\n' \
                 '   /Parent {parent_id} 0 R\n' \
                 '   /MediaBox [0 0 {page_width} {page_height}]\n' \
                 '   /Contents {contents_id} 0 R\n' \
                 '   /Resources\n' \
                 '   <<\n'.format(object_id=self.object_id,
                                  parent_id=self.parent._page_root_id,
                                  page_width=page_size[0],
                                  page_height=page_size[1],
                                  contents_id=self.content.object_id)

        for font_id in unique_font_ids:
            result += '      /Font << /F{font_id} {font_id} 0 R >>\n'.format(font_id=font_id)

        result += '   >>\n' \
                  '>>\n' \
                  'endobj\n'

        return result

    def __bytes__(self):
        return str(self).encode()

    def get_next_object_id(self):
        return self.parent.get_next_object_id()

    def get_page_size(self):
        if self.page_size is not None:
            return self.page_size
        else:
            return self.parent.get_page_size()

    def add_text(self, text, font_name='Arial', font_size=12, position=(0, 0)):
        font = self.document.get_font(font_name)

        instruction = Text(text, font, font_size)
        instruction.text = text
        instruction.position = position
        instruction.encoding = encoding

        self.content.instructions.append(instruction)


class Document():
    """The top level PDF object"""

    def __init__(self):
        # Rendering settings
        self.resolution = 72
        self.page_size = PageSize.A4.value

        # Counter for setting object IDs
        self._object_counter = 0

        # Document objects
        self.metadata = Metadata(self.get_next_object_id())
        self._catalog_id = self.get_next_object_id()
        self._outlines_id = self.get_next_object_id()
        self._page_root_id = self.get_next_object_id()
        self.outlines = []
        self.pages = []
        self.fonts = {}

    def __bytes__(self):
        self.xrefs = []

        self.bytes_output = b'%PDF-1.4\n'

        self._write_object(self.metadata)
        self._write_object(self.get_catalog().encode())
        self._write_object(self.get_outlines().encode())
        self._write_object(self.get_page_root().encode())

        for page in self.pages:
            self._write_object(page)
            self._write_object(page.content)

        for font in self.fonts.values():
            self._write_object(font)

        xref_position = len(self.bytes_output)
        self._write_xref_table()

        self._write_trailer(xref_position)

        return self.bytes_output

    def get_next_object_id(self):
        self._object_counter += 1
        return self._object_counter

    def get_catalog(self):
        return '{0} 0 obj\n' \
               '<< /Type /Catalog\n' \
               '   /Outlines {1} 0 R\n' \
               '   /Pages {2} 0 R\n' \
               '>>\n' \
               'endobj'.format(self._catalog_id, self._outlines_id, self._page_root_id)

    def get_outlines(self):
        return '{0} 0 obj\n' \
               '<< /Type /Outlines\n' \
               '   /Count 0\n' \
               '>>\n' \
               'endobj'.format(self._outlines_id)

    def get_page_root(self):
        result = str(self._page_root_id) + ' 0 obj\n' \
                                           '<< /Type /Pages\n'

        for page in self.pages:
            result += '   /Kids [{0} 0 R]\n'.format(page.object_id)

        result += '   /Count {0}\n' \
                  '>>\n' \
                  'endobj'.format(len(self.pages))

        return result

    def get_page_size(self):
        return self.page_size

    def get_font(self, font_name):
        font = self.fonts.get(font_name)

        if font is None:
            font = Font(self.get_next_object_id(), font_name)
            self.fonts[font_name] = font

        return font

    def _write_object(self, object):
        self.xrefs.append(len(self.bytes_output))
        self.bytes_output += bytes(object)
        self.bytes_output += b'\n'

    def _write_xref_table(self):
        # Write xref opening line and first object
        result = 'xref\n0 {0}\n' \
                 '0000000000 65535 f \n'.format(len(self.xrefs) + 1)

        for xref in self.xrefs:
            result += '{:0=10}'.format(xref) + ' 00000 n \n'

        self.bytes_output += result.encode()

    def _write_trailer(self, xref_position):
        self.bytes_output += 'trailer\n' \
                             '<< /Size {object_count}\n' \
                             '   /Info {metadata_id} 0 R\n' \
                             '   /Root {root_id} 0 R\n' \
                             '>>\n' \
                             'startxref\n' \
                             '{xref_position}\n' \
                             '%%EOF'.format(object_count=len(self.xrefs) + 1,
                                            metadata_id=self.metadata.object_id,
                                            root_id=self._catalog_id,
                                            xref_position=xref_position).encode()
