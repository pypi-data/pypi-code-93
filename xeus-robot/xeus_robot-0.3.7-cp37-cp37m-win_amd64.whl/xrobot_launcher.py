if __name__ == '__main__':
    def _xrobot_get_connection_filename():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', help='Jupyter kernel connection filename')
        args, unknown = parser.parse_known_args()
        return args.f

    from xrobot import launch as _xrobot_launch
    _xrobot_launch(_xrobot_get_connection_filename() or '')
