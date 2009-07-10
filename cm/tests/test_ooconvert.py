import unittest
from cm.utils.ooconvert import convert,fix_img_path,extract_css_body, convert_html,combine_css_body

class OOConvertTestCase(unittest.TestCase):

    def xtestConversionDocHTML1(self):
        content = open("cm/tests/data/sample_doc_1img.doc").read()
        html,images = convert(content, 'html', unicode = True)
        self.assertEquals(len(images),1)
        xhtml,images = convert(content, 'xhtml', unicode = True)
        self.assertEquals(len(images),0)
        
    def xtestConversionDocHTML2(self):
        content = open("cm/tests/data/doc_2_img.odt").read()        
        html,images = convert(content, 'html', unicode = True)
        xhtml,images = convert(content, 'xhtml', unicode = True)
        imgs = {'outfile__6a89df02.png' : 'test'}
        fix_img_path(html,xhtml,imgs)
        
    def xtestConversionDocPDF(self):
        """
        Simply tests converter works
        """
        content = open("cm/tests/data/doc_2_img.odt").read()
        pdf,_ = convert(content, 'pdf')
        
    def testConversionFromHTML(self):
        #content = open("cm/tests/data/lb.html").read()
        content = open("cm/tests/data/res_span_simple.html").read()        
        data = combine_css_body(content,'')
        res = convert_html(data,'doc',images = None)     

    def xtestCssExtraction(self):
        doc = """<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"><head>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<title> </title>
<meta name="generator" content="StarOffice/OpenOffice.org XSLT (http://xml.openoffice.org/sx2ml)" />
<meta name="author" content="zz" /><meta name="created" content="2007-02-12T10:53:00" />
<base href="." /><style type="text/css">
    @page { size: 20.999cm 29.699cm; margin-top: 1.27cm; margin-bottom: 1.27cm; margin-left: 2.501cm; margin-right: 2.501cm }
    table { border-collapse:collapse; border-spacing:0; empty-cells:show }
    td, th { vertical-align:top; }
    h1, h2, h3, h4, h5, h6 { clear:both }            
    </style></head><body dir="ltr"><div style="text-align:left">
    qsdqsdsqd
    </div>
    </body>
    </html>
        """
        css,body = extract_css_body(doc)