import glob
import os
import re
import sys
import tempfile
import time


def expand_jar(tmpdirname, jarpath):
    command = "tar -C " + tmpdirname + " -xf " + jarpath
    os.system(command)


def get_all_class_files(tmpdirname):
    files = glob.glob(tmpdirname + '/**/*.class', recursive=True)
    return files

signature_mapping = {
    # Primitive Types
    "B": "byte",
    "C": "char",
    "D": "double",
    "F": "float",
    "I": "int",
    "J": "long",
    "S": "short",
    "Z": "boolean"
}

METHOD_DEF_RE = re.compile(r"^[^/\d]*?([\w\.]*\(.*\)).*;")
METHOD_CALL_RE = re.compile(r"\s*\d+:\s+invoke.*// Method\s+(.+)")


def extract_calls(contents):
    for line in contents.split('\n'):
        #print(line)
        match = METHOD_DEF_RE.match(line)
        if match is not None:
            current_method_sig = match.group(1)
            print("current_method_sig:", current_method_sig)
        else:
            match = METHOD_CALL_RE.match(line)
            if match is not None:
                called_method_sig = match.group(1)
                try:
                    print(called_method_sig)
                    print(current_method_sig, "CALLS",called_method_sig)
                except:
                    print("IN EXCEPTION")
                    while 1:
                        time.sleep(1)

if __name__ == '__main__':

    with tempfile.TemporaryDirectory() as tmpdirname:
        expand_jar(tmpdirname, sys.argv[1])
        class_files = get_all_class_files(tmpdirname)
        for class_file in class_files:
            print("######", class_file)
            cmd = "javap -p -c " + class_file + " > /tmp/disassembled"
            os.system(cmd)
            contents = open("/tmp/disassembled").read()
            extract_calls(contents)

        while True:
            print('created temporary directory', tmpdirname)
            time.sleep(20)
