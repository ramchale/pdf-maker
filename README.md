PDF Maker [![Build Status](https://travis-ci.org/ramchale/pdf-maker.svg?branch=master)](https://travis-ci.org/ramchale/pdf-maker)
=========

A python library for creating PDFs

Goals are to keep it simple to use and make it possible to create PDF/A compliant PDFs

**Note: This is a very early development version missing some core functionality**

Contributions welcome

Basic Example
--------------

```python
from pdf_maker.pdf import Document, Page
 
document = Document()
 
page = Page(document)
page.add_text('This is some text')
 
with open('Test.pdf', 'wb') as f:
    f.write(bytes(document))
```

Longer Example
--------------------

```python
from pdf_maker.pdf import Document, Page, PageSize
document = Document()
document.resolution = 72
document.page_size = PageSize.A3.value
 
page = Page(document)
page.add_text('This is some text')
page.add_text('As is this', font_name='Vivian', font_size=30, position=(100, 100))
 
with open('Test.pdf', 'wb') as f:
    f.write(bytes(document))
```
