import glob
import os
import sys
import tempfile
import time


def expand_jar(tmpdirname, jarpath):
    command = "tar -C " + tmpdirname + " -xf " + jarpath
    os.system(command)


def get_all_class_files(tmpdirname):
    files = glob.glob(tmpdirname + '/**/*.class', recursive=True)
    return files


def extract_calls(contents):
    print(len(contents))


if __name__ == '__main__':

    with tempfile.TemporaryDirectory() as tmpdirname:
        expand_jar(tmpdirname, sys.argv[1])
        class_files = get_all_class_files(tmpdirname)
        for class_file in class_files:
            cmd = "javap -p -c " + class_file + " > /tmp/disassembled"
            os.system(cmd)
            contents = open("/tmp/disassembled").read()
            extract_calls(contents)

        while True:
            print('created temporary directory', tmpdirname)
            time.sleep(20)
