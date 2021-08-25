import json

import iota_client


def check_installation():
    '''Getting Started
    https://client-lib.docs.iota.org/docs/libraries/python/getting_started
    '''
    print('\n[ Installation ]')
    print(iota_client.__doc__)
    print(dir(iota_client))


def check_network():
    print('\n[ Network ]')
    # client will connect to testnet by default
    client = iota_client.Client()
    print(json.dumps(client.get_info(), indent=4))


def main():
    check_installation()
    check_network()


if __name__ == '__main__':
    main()
