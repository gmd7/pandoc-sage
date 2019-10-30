#!/usr/bin/env python3

"""
Pandoc filter to process code blocks
-sagesilent
-sageblock
-sageprint
and replace sage-command with the results in inline math
- \sage{}
"""

import hashlib
import os
import sys
import re
import panflute as pf
from subprocess import Popen, PIPE, call

IMAGE_DIR = "sage-images"
SAGE_SESSION_FILENAME = 'sage_session'
SAGE_SESSION = """# -*- coding: utf-8 -*-
try:
    load_session(\'{filename}\')
except:
    pass
%s
save_session(\'{filename}\')
""".format(filename=SAGE_SESSION_FILENAME)

classes = ['sageblock','sagesilent','sageplot']

def writeFile(mode, code, outfile):
    'write a file, return if success'
    if not code:
        sys.stderr.write('skipped writing 0 bytes to', outfile)
        return False
    try:
        with open(outfile, mode, encoding="utf-8") as f:
            f.write(code)
            sys.stderr.write('wrote ' + str(len(code)) + ' bytes to ' +  outfile)
    except (OSError, IOError) as e:
        sys.stderr.write('fail: could not write', len(code), 'bytes to', outfile)
        sys.stderr.write('>>: exception', e)
        return False
    return True


def sha1(x):
    return hashlib.sha1(x.encode(sys.getfilesystemencoding())).hexdigest()

def get_sage_filename(code):
    outfile = os.path.join(IMAGE_DIR, sha1(code))
    return outfile + '.sage'

def get_image_output_filename(code):
    outfile = os.path.join(IMAGE_DIR, sha1(code))
    return outfile + '.svg'


def run_sage(code):

    infile = get_sage_filename(code)

    if not os.path.isfile(infile):
        try:
            os.mkdir(IMAGE_DIR)
            sys.stderr.write('Created directory ' + IMAGE_DIR + '\n')
        except OSError:
            pass

    if not os.path.isfile(infile):
        code = SAGE_SESSION % code
        writeFile('w', code, infile)

    pipes = {'stdin': None,
             'stdout': PIPE,
             'stderr': PIPE}
    p = Popen(["sage", infile], **pipes)

    out, err = p.communicate()
    out = out.decode('utf8')
    return out,err

def run_tex(code):
    infile = os.path.join(IMAGE_DIR, sha1(code) + '.tex')

    pipes = {'stdin': None,
             'stdout': PIPE,
             'stderr': PIPE}

    if not os.path.isfile(infile):
        try:
            os.mkdir(IMAGE_DIR)
            sys.stderr.write('Created directory ' + IMAGE_DIR + '\n')
        except OSError:
            pass

    if not os.path.isfile(infile):
        writeFile('w', code, infile)

    p = Popen(["pdflatex",'-output-directory',IMAGE_DIR, infile], **pipes)
    out, err = p.communicate()

    basename = infile[:-4]
    #args = ['convert','-trim', '-quality', '100', '-flatten', '-sharpen', '0x1.0', '-density', '600', basename + '.pdf', basename + '.svg']
    args = ['pdftocairo', '-svg' , basename + '.pdf', basename + '.svg']
    p = Popen(args, **pipes)
    out, err = p.communicate()
    return out, err, basename + '.svg'


def replace_sagecommand(text):
    contents = text
    m = re.findall('\\\\sage\{[^}]*\}', text)
    if m:
        for found in m:
            sage_cmd = found[6:-1]
            if sage_cmd[:5] == 'print':
                res, err = run_sage(sage_cmd)
            elif sage_cmd[:5] == 'latex':
                res, err = run_sage("print(%s)" % sage_cmd)
            else:
                res, err = run_sage("print(latex(%s))" % sage_cmd)
            res = res.rstrip()
            try:
                contents = contents.replace(found, res)
            except:
                pass
    return contents


def sage(elem, doc):
    elemtype = type(elem)

    if elemtype in [ pf.Math, pf.RawInline]:
        contents = replace_sagecommand(elem.text)

        if elemtype == pf.Math:
            return pf.Math(contents,format=elem.format)
        else:
            return pf.RawInline(contents,format=elem.format)


    
    if elemtype == pf.CodeBlock:

        isSageSilent = 'sagesilent' in elem.classes
        isSageBlock = 'sageblock' in elem.classes
        isSagePlot = 'sageplot' in elem.classes

        code = elem.text
        if isSageBlock or isSagePlot or isSageSilent:
            img_file = get_image_output_filename(code)
            sage_file = get_sage_filename(code)

            if isSagePlot:
                code = code.strip("\n")
                codelist = code.split("\n")
                plot_cmd = codelist.pop()
                code = "\n".join(codelist)
                m = re.search(r"sageplot\[(?P<first_name>.*)\]\((.*)\)", plot_cmd)
                if m == None:
                    para, cmd = "", plot_cmd
                else:
                    para, cmd = m.group(1), m.group(2)
                if len(para) > 0:
                    para = ',' + para
                code += "\n(%s).save(\"%s\"%s)" % (cmd, img_file , para)

            out,err = run_sage(code)

            if isSageSilent:
                return pf.Plain(pf.RawInline("", "tex"))
            elif isSageBlock:
                sys.stderr.write('\n convert markdown \n')
                return pf.convert_text(out)
            else:
                return pf.Para(pf.Image(url=img_file,attributes=elem.attributes))
        if 'latex' in elem.classes:
            out, err, img_file = run_tex(code)

            return pf.Para(pf.Image(url=img_file,attributes=elem.attributes))

if __name__ == "__main__":
    # Reset sage session
    try:
        os.remove(SAGE_SESSION_FILENAME + '.sobj')
    except:
        pass

    pf.toJSONFilter(action=sage)