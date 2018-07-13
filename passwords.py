import argparse
import collections
import os
import sys

import ldap


# program requires two filepaths as command line arguments:
# first: ux8 filepath
def main():
    cli_arg_parser = argparse.ArgumentParser()
    cli_arg_parser.add_argument('--ux8', required=True, help='The ux8 filepath')
    cli_arg_parser.add_argument('--lrc', required=True, help='The lrc filepath')
    # parse arguments provided via the cli
    cli_arguments = cli_arg_parser.parse_args()

    # check that the --ux8 filepath exists
    ux8_filepath = cli_arguments.ux8
    if not os.path.isfile(ux8_filepath):
        print('the ux8 file does not exist: "%s"' % ux8_filepath)
        return 1

    # check that the --lrc filepath exists
    lrc_filepath = cli_arguments.lrc
    if not os.path.isfile(lrc_filepath):
        print('the lrc file does not exist: "%s"' % lrc_filepath)
        return 1

    print('Received ux8 filepath: "%s", lrc filepath: "%s"\n\n' % (ux8_filepath, lrc_filepath))

    # read in data from ux8 and lrc files, store content
    # in a dictionary, keyed by Username, with the etc/passwd entries as values
    # e.g { VinDiesel : [ "VinDiesel", "x", "55555", "454", "Foobar Baz,Bar@example.com", ... ] }

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
            username = etc_passwd_entries[0]
            ux8_dict[username] = etc_passwd_entries

    lrc_dict = {}
    with open(lrc_filepath, 'r') as lrc_file:
        for line in lrc_file:
            line = line.replace('\n', '')
            etc_passwd_entries = line.split(":")
            username = etc_passwd_entries[0]
            lrc_dict[username] = etc_passwd_entries

    # find ux8 filepath's directory
    ux8_filepath_dir = os.path.dirname(ux8_filepath)

    # create an output.csv filepath under the same directory as the ux8 file
    output_filepath = os.path.join(ux8_filepath_dir, 'output.csv')
    with open(output_filepath, 'w') as output_file:
        output_file.write('USERNAME,PASSWD,UID,GID,MISCELLANY,HOME-DIR,SHELL,LDAP,LRC\n')

        # iterate through the ux8 dictionary (remember that order :) ),
        # checking if it exists in lrc dict and ldap (call tin's function)
        for username, etc_passwd_entries in ux8_dict.items():
            exists_in_ldap = "no"
            if found_in_ldap(username):
                exists_in_ldap = "yes"

            exists_in_lrc = "no"
            if username in lrc_dict.keys():
                exists_in_lrc = "yes"

            print('user: "%s" - exists in ldap? "%s", exists in lrc? "%s"' % (username, exists_in_ldap, exists_in_lrc))
            # output_items is original items plus 2 new columns which indicates if it exists in ldap and lrc
            output_etc_passwd_entries = etc_passwd_entries + [exists_in_ldap, exists_in_lrc]
            output = ','.join(output_etc_passwd_entries)
            output_file.write('%s\n' % output)

    print ('read contents from ux8: "%s" and lrc: "%s". wrote results to "%s"' % (ux8_filepath, lrc_filepath, output_filepath))


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


def test_ldap():
    found_in_ldap("wendy")
    result_set = found_in_ldap("tin")
    print( result_set )
    print( "===" )
    found_in_ldap("foobar")
    if found_in_ldap("wavalos") :
       print( "found wavalos" )
    return 0


if __name__ == '__main__':
    main()
