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

CLASS_OR_IF_DEF_RE = re.compile(r"^\s*(.*)?\s+(class|interface)\s+([\w\.]+)\s+(extends|implements)?\s*([\w\.\<\>\s,\$]+)?.*{")
#INTERFACE_DEF_RE = re.compile(r"^.*?interface\s+([\w\.]+)\s.*{")
METHOD_DEF_RE = re.compile(r"^[^/\d]*?([\w\.]*\(.*\)).*;")
METHOD_CALL_RE = re.compile(r"\s*\d+:\s+invoke.*// Method\s+(.+)")


def extract_calls(contents):
    current_class = None
    try:
        for line in contents.split('\n'):
            #print(line)
            match = CLASS_OR_IF_DEF_RE.match(line)
            if match is not None:
                print(line)
                p = match.group(1)
                ci = match.group(2)
                current_class = match.group(3)
                ei = match.group(4)
                ext_list = match.group(5)
                ext_list = ext_list and ext_list.strip().split(',') or []
                print("P", p)
                print("ci:", ci)
                print("current_class:", current_class)
                print("ei:", ei)
                print("ext_list:", ext_list)
                continue

            if current_class is None:
                # Skip all lines until we have a current class
                continue

            match = METHOD_DEF_RE.match(line)
            if match is not None:
                current_method_sig = match.group(1)
                if '.' not in current_method_sig:
                    # current method is local, prefix namespace (class)
                    current_method_sig = current_class + '.' + current_method_sig
                #print("current_method_sig:", current_method_sig)
                continue

            match = METHOD_CALL_RE.match(line)
            if match is not None:
                called_method_sig = match.group(1)
                if '/' not in called_method_sig:
                    called_method_sig = current_class + '.' + called_method_sig
                #print("called_method_sig:", called_method_sig)
                longform_called_method_sig = expand_shorthand_sig(called_method_sig)
                #print("longform_called_method_sig:", longform_called_method_sig)
                    # print(current_method_sig, "CALLS", longform_called_method_sig)
    except Exception:
        print("IN EXCEPTION")
        raise
        while 1:
            time.sleep(1)


def expand_shorthand_sig(shorthand):
    dots_instead_of_slashes = shorthand.replace('/', '.')
    return dots_instead_of_slashes


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
