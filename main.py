import csv
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


CLASS_OR_IF_DEF_RE = re.compile(
    r"^\s*(.*)?\s*(class|interface)\s+([\w\.]+)\s+(extends|implements)?\s*([\w\.\<\>\s,\$]+)?.*{")
# INTERFACE_DEF_RE = re.compile(r"^.*?interface\s+([\w\.]+)\s.*{")
METHOD_DEF_RE = re.compile(
    r"^\s*(public|private|protected)?\s*((static\s*|final\s*|abstract\s*|transient\s*|synchronized\s*|volatile\s*)*)\s*([\w\.\<\>\$]+)?\s+([\w\.]*\(.*\)).*;")
METHOD_DEF_RE = re.compile(r"""^\s*(public|private|protected)?  # access
                                       \s*((static\s*|final\s*|abstract\s*|transient\s*|synchronized\s*|volatile\s*)*)\s* # all modifiers
                                       ([\w\.\<\>\$]+)?\s+  # return value
                                       ([\w\.]*\(.*\)).*;   # method name plus arguments
                                       """, re.VERBOSE)
METHOD_CALL_RE = re.compile(r"\s*\d+:\s+(invoke[^\s]+).*// Method\s+(.+)")


def extract_calls(contents, class_writer, method_writer):
    current_class_or_if = None
    try:
        for line in contents.split('\n'):
            # print(line)
            match = CLASS_OR_IF_DEF_RE.match(line)
            if match is not None:
                #print(line)
                access = match.group(1)
                type = match.group(2)
                current_class_or_if = match.group(3)
                ext_impl = match.group(4)
                ext_list = match.group(5)
                ext_list = ext_impl and ext_impl.strip().split(',') or []
                #print("access", access)
                #print("type:", type)
                #print("current_class_or_if:", current_class_or_if)
                #print("ext_impl:", ext_impl)
                #print("ext_list:", ext_list)
                continue

            if current_class_or_if is None:
                # Skip all lines until we have a current class
                continue

            match = METHOD_DEF_RE.match(line)
            if match is not None:
                #print(line)
                access = match.group(1)
                #print("access", access)
                modifiers = match.group(2).strip()
                #print("modifiers", modifiers)
                return_type = match.group(4)
                #print("return_type", return_type)
                current_method_sig = match.group(5)
                if '.' not in current_method_sig:
                    # current method is local, prefix namespace (class)
                    current_method_sig = current_class_or_if + '.' + current_method_sig
                #print("current_method_sig:", current_method_sig)
                continue

            # special case of static initializer block
            if line.strip() == "static {};":
                current_method_sig = current_class_or_if + '.' + "<static_initializer_block>"
                continue

            match = METHOD_CALL_RE.match(line)
            if match is not None:
                invoke_type = match.group(1)
                called_method_sig = match.group(2)
                if '/' not in called_method_sig:
                    called_method_sig = current_class_or_if + '.' + called_method_sig
                #print("called_method_sig:", called_method_sig)
                longform_called_method_sig = expand_shorthand_sig(called_method_sig)
                #print("longform_called_method_sig:", longform_called_method_sig)
                longform_called_method_sig = longform_called_method_sig.replace('."<init>"', '')  # Remove this substring designating constructors
                print(invoke_type, current_method_sig, "CALLS", longform_called_method_sig)
    except Exception:
        print("IN EXCEPTION")
        raise
        while 1:
            time.sleep(1)


short_to_long_mapping = {
    # Primitive Types
    "B": "byte",
    "C": "char",
    "D": "double",
    "F": "float",
    "I": "int",
    "J": "long",''
    "S": "short",
    "Z": "boolean"
}

SHORTHAND_ARGS_RE = re.compile(r":\((.*)\)")

def short_args_to_long(match):
    remaining_short_args = match.group(1)
    longform_args = []
    array_flag = False
    while remaining_short_args:
        short_type = remaining_short_args[0]
        remaining_short_args = remaining_short_args[1:]
        if short_type == '[':
            array_flag = True
            continue
        long_type = short_to_long_mapping.get(short_type)
        assert long_type or short_type == 'L', "Unknown short type"
        if short_type == 'L':
            end_type_index = remaining_short_args.index(';')
            long_type = remaining_short_args[:end_type_index]
            remaining_short_args = remaining_short_args[end_type_index + 1:]
        if array_flag:
            long_type = long_type + '[]'
            array_flag = False
        longform_args.append(long_type)
        continue
    return "(" + ", ".join(longform_args) + ")"


def expand_shorthand_sig(shorthand):
    shorthand = shorthand[:shorthand.index(')') + 1]  # truncate the return val that appears after first ')'
    dots_instead_of_slashes = shorthand.replace('/', '.')
    longform = re.sub(SHORTHAND_ARGS_RE, short_args_to_long, dots_instead_of_slashes)
    return longform


if __name__ == '__main__':

    with tempfile.TemporaryDirectory() as tmpdirname, open("classes_and_interfaces.csv", "w") as class_f, open("method_calls.csv", "w") as method_f:
        expand_jar(tmpdirname, sys.argv[1])
        class_files = get_all_class_files(tmpdirname)
        class_writer = csv.writer(class_f)
        method_writer = csv.writer(method_f)
        for class_file in class_files:
            #print("######", class_file)
            cmd = "javap -p -c " + class_file + " > /tmp/disassembled"
            os.system(cmd)
            contents = open("/tmp/disassembled").read()
            extract_calls(contents, class_writer, method_writer)

        while True:
            print('created temporary directory', tmpdirname)
            time.sleep(20)
