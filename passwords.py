import os
import sys


# program requires two filepaths as command line arguments:
# first: ldap filepath
# second: lrc filepath
def main():
    cli_arguments = sys.argv[1:]
    # check that user provided 2 cli arguments
    if len(cli_arguments) != 2:
        print("must provide two filepath arguments: ldap file and lrc file")
        return 1

    # check that the ldap filepath exists
    ldap_filepath = cli_arguments[0]
    if not os.path.isfile(ldap_filepath):
        print('the ldap file does not exist: "%s"' % ldap_filepath)
        return 1

    # check that the lrc filepath exists
    lrc_filepath = cli_arguments[1]
    if not os.path.isfile(lrc_filepath):
        print('the lrc file does not exist: "%s"' % lrc_filepath)
        return 1

    print('Received ldap filepath: "%s", lrc filepath: "%s"' % (ldap_filepath, lrc_filepath))

    # read in data from lrc file into a dictionary,
    # dictionary has keys as UID and values as the line items.
    lrc_dict = {}
    with open(lrc_filepath, 'r') as lrc_file:
        for line in lrc_file:
            # strip out the newline character from the line
            line = line.replace('\n', '')
            # split the line by ":" into a list
            items = line.split(":")
            # { uid: [items] }
            # e.g { 55555 : [ "foobar", "x", "55555", "454", "Foobar Baz,Bar@example.com", ... ] }
            uid = items[2]
            lrc_dict[uid] = items


    # read in data from ldap file into a dictionary,
    # dictionary has keys as UID and values as the line items.
    ldap_dict = {}
    with open(ldap_filepath, 'r') as ldap_file:
        for line in ldap_file:
            # strip out the newline character from the line
            line = line.replace('\n', '')
            # split the line by ":", returns list
            line_columns = line.split(":")
            # { uid: [items] }
            # e.g { "55555" : [ "foobar", "x", "55555", "454", "Foobar Baz,Bar@example.com", ... ] }
            uid = line_columns[2]
            ldap_dict[uid] = line_columns


    # find ldap filepath's directory
    ldap_filepath_dir = os.path.dirname(ldap_filepath)

    # create an output.csv filepath under the same directory as the ldap file
    output_filepath = os.path.join(ldap_filepath_dir, 'output.csv')
    with open(output_filepath, 'w') as output_file:

        # iterate through the lrc dictionary, checking if it exists in ldap dictionary
        for uid, items in lrc_dict.items():
            exists_in_ldap = '0'
            if uid in ldap_dict.keys():
                exists_in_ldap = '1'
                print('there is a match (lrc -> ldap) via UID="%s" in both files' % uid)
            # output_items is original items plus 2 new columns which indicates if it exists in ldap and lrc
            output_items = items + [exists_in_ldap, '1']
            output = ','.join(output_items)
            output_file.write('%s\n' % output)
    print ('read contents from "%s" and "%s". wrote results to "%s"' % (lrc_filepath, ldap_filepath, output_filepath))


if __name__ == '__main__':
    main()
