class Font():
    def __init__(self, object_id, base_font):
        self.object_id = object_id
        self.base_font = base_font
        self.encoding = 'MacRomanEncoding'

    def __str__(self):
        return '{object_id} 0 obj\n' \
               '<< /Type /Font\n' \
               '  /Subtype /Type1\n' \
               '  /Name /F{object_id}\n' \
               '  /BaseFont /{base_font}\n' \
               '  /Encoding /{encoding}\n' \
               '>>\n' \
               'endobj'.format(object_id=self.object_id, base_font=self.base_font, encoding=self.encoding)

    def __bytes__(self):
        return str(self).encode()
