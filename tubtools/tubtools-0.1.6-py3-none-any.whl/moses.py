import getpass
import sys
import argparse

MOSES_SHIB_URL = MOSES_URL + '/moses/shibboleth/login'





def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user')
    parser.add_argument('-p', '--password')
    parser.add_argument('emails')
    parser.add_argument('outfile')

    args = parser.parse_args()

    if not args.user:
        args.user = input('Username:')

    if not args.password:
        args.password = getpass.getpass('Password:')

    user, pw, infile, outfile = (args.user, args.password, args.emails, args.outfile)

    session = login(user, pw)

    if session is None:
        print('Login failed :(')
        sys.exit(1)

    print('Login successful!')

    with open(infile, 'r') as fi:
        with open(outfile, 'w') as fo:
            for email in map(lambda l: l.strip(), fi.readlines()):
                ppl = search_people(session, email=email)

                if ppl:
                    fo.write(f'{ppl[0].id}, {email}\n')
                else:
                    fo.write(f'  N/A , {email}\n')
                    print(f'Could not find "{email}"!')


if __name__ == '__main__':
    main()


