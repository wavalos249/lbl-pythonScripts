import os
import sys


def main():
    # read command line arguments, strip out the name of this source code file.
    # cli - command line interface
    cli_arguments = sys.argv[1:]
    if len(cli_arguments) != 1:
        print "Must provide a filepath argument"
        return 1

    filepath = cli_arguments[0]
    print "received %s filepath" % filepath

    if os.path.exists(filepath) == False:
        print "the file does not exists"
        return 1

    with open(filepath, 'r') as of:
        dirname = os.path.dirname(filepath)
        output_filepath = os.path.join(dirname, 'output.csv')


    with open(output_filepath, 'w') as f:
        for line in f:
             line = line.replace('\n', '')
             sanitized = line.replace(':', ',')
             of.write(sanitized)



if __name__ == '__main__':
    main()