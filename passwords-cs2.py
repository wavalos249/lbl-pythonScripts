import argparse
import collections
import os
import sys

import ldap


COLUMNS = ['USERNAME','PASSWD','UID','GID','MISCELLANY','HOME-DIR','SHELL','LDAP','USRDATA']
SEPARATOR = '\t'


# program requires two filepaths as command line arguments:
# first: cs2 filepath
def main():
    cli_arg_parser = argparse.ArgumentParser()
    cli_arg_parser.add_argument('--cs2', required=True, help='The cs2 filepath')
    cli_arg_parser.add_argument('--ux8', required=True, help='The ux8 filepath')
    # parse arguments provided via the cli
    cli_arguments = cli_arg_parser.parse_args()

    # check that the --cs2 filepath exists
    cs2_filepath = cli_arguments.cs2
    if not os.path.isfile(cs2_filepath):
        print('the cs2 file does not exist: "%s"' % cs2_filepath)
        return 1

    # check that the --ux8 filepath exists
    ux8_filepath = cli_arguments.ux8
    if not os.path.isfile(ux8_filepath):
        print('the ux8 file does not exist: "%s"' % ux8_filepath)
        return 1

    print('Received cs2 filepath: "%s", ux8 filepath: "%s"\n\n' % (cs2_filepath, ux8_filepath))

    # read in data from ux8 and lrc files, store content
    # in a dictionary, keyed by Username, with the etc/passwd entries as values
    # e.g { VinDiesel : [ "VinDiesel", "x", "55555", "454", "Foobar Baz,Bar@example.com", ... ] }

    cs2_dict = {}
    with open(cs2_filepath, 'r') as cs2_file:
        for line in cs2_file:
            line = line.replace('\n', '')
            # lines end with a : then it has no dates, include them
            if line.endswith(':'):
                etc_passwd_entries = line.split(':')
                username = "%s %s" % (etc_passwd_entries[3], etc_passwd_entries[2])
                username = username.lower()
                cs2_dict[username] = etc_passwd_entries

    # need to preserve order of ux8 entries
    # so later we can output them in the same order
    ux8_dict = collections.OrderedDict()
    with open(ux8_filepath, 'r') as ux8_file:
        for line in ux8_file:
            # strip out the newline character from the line
            line = line.replace('\n', '')
            # split the line by ":" into a list
            etc_passwd_entries = line.split(":")
            # { username: [etc_passwd_entries] }
            username = etc_passwd_entries[4].split(',')[0].lower()
            ux8_dict[username] = etc_passwd_entries

    # find ux8 filepath's directory
    ux8_filepath_dir = os.path.dirname(ux8_filepath)

    # create an output-cs2.csv filepath under the same directory as the ux8 file
    output_filepath = os.path.join(ux8_filepath_dir, 'output-cs2.txt')
    with open(output_filepath, 'w') as output_file:
        output_file.write('%s\n' % SEPARATOR.join(COLUMNS))

        # iterate through the ux8 dictionary (remember that order :) ),
        # checking if it exists in lrc dict and ldap (call tin's function)
        for username, etc_passwd_entries in ux8_dict.items():
            exists_in_ldap = "no"
            ldap_username = etc_passwd_entries[0]
            if found_in_ldap(ldap_username):
                exists_in_ldap = "yes"

            exists_in_cs2 = "no"
            #if "kurtzer" in username:
            #    import pdb; pdb.set_trace()

            if username in cs2_dict.keys():
                exists_in_cs2 = "yes"

            print('user: "%s" - exists in ldap? "%s", exists in cs2? "%s"' % (username, exists_in_ldap, exists_in_cs2))
            # output_items is original items plus 2 new columns which indicates if it exists in ldap and cs2
            output_etc_passwd_entries = etc_passwd_entries + [exists_in_ldap, exists_in_cs2]
            output_file.write('%s\n' % SEPARATOR.join(output_etc_passwd_entries))

    print ('read contents from ux8: "%s" and lrc: "%s". wrote results to "%s"' % (ux8_filepath, cs2_filepath, output_filepath))


def found_in_ldap( user ):
    #print ldap.__file__
    con = ldap.initialize('ldap://identity:389')
    ldap_base = "ou=people,dc=lbl,dc=gov"
    #searchAttribute = ["uid","cn","mail"]
    searchAttribute = ["mail"]
    #query = "(uid=wavalos)"
    query = "(uid=%s)" % user		# uid is loginname eg "wavalos"
    #query = "(sn=%s)" % user		# sn is "surname"
    #query = "(givenname=%s)" % user
    #result_set = con.search_s(ldap_base, ldap.SCOPE_SUBTREE, query)    # unfiltered results
    result_set = con.search_s(ldap_base, ldap.SCOPE_SUBTREE, query, searchAttribute)

    #print("ldap server response for user: %s" % user)
    #print( result_set )
    #print( len(result_set) ) # number of matches
    #print("\n")
    if len(result_set) == 0:
        return False
    else:
        return True


if __name__ == '__main__':
    main()
