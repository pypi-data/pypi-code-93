import sys
sys.path.append('../')
import getopt
from yt_concate.pipeline.pipeline import Pipeline
from yt_concate.pipeline.steps.preflight import Preflight
from yt_concate.pipeline.steps.get_video_links import GetVideoLinks
from yt_concate.pipeline.steps.initialize_yt import InitializeYt
from yt_concate.pipeline.steps.get_video_captions import GetVideoCaption
from yt_concate.pipeline.steps.search_term import Search
from yt_concate.pipeline.steps.download_video import DownloadVideo
from yt_concate.pipeline.steps.edit_video import EditVideo
from yt_concate.pipeline.steps.postflight import Postflight
from yt_concate.utils import Utils
from distutils.util import strtobool
from yt_concate.log import set_logger

#"UCV0qA-eDDICsRR9rPcnG7tw"


def print_usage():
    print('Options:')
    print('{:<6s} {:<12s}  channel id of searching youtube video(must input)'.format('-c','--channelid'))
    print('{:<6s} {:<12s}  search term of youtube video(must input)'.format('-s', '--searchterm'))
    print('{:<6s} {:<12s}  limit of clips to be edited into final video'.format('-l', '--limit'))
    print('{:<6s} {:<12s}  remove downloading files produced in program process'.format('', '--cleanup'))

def main():
    inputs = {
        "channel_id": None,
        "search_term": None,
        "limit": 20,
        "cleanup": False,

    }

    steps = [
        Preflight(),
        GetVideoLinks(),
        InitializeYt(),
        GetVideoCaption(),
        Search(),
        DownloadVideo(),
        EditVideo(),
        Postflight(),
    ]

    shortopt = 'hc:s:l:'
    longopt = 'channelid= searchterm= limit= cleanup='.split()

    try:
        opts, args = getopt.getopt(sys.argv[1:], shortopts=shortopt, longopts=longopt )
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_usage()
            sys.exit(0)
        elif opt in ("-c", "--channelid"):
            inputs['channel_id'] = arg
        elif opt in ("-s", "--searchterm"):
            inputs['search_term'] = arg
        elif opt in ("-l", "--limit"):
            inputs['limit'] = arg
        elif opt == "--cleanup":
            inputs['cleanup'] = bool(strtobool(arg))

    if not inputs['channel_id'] or not inputs['search_term']:
        print('Must input channelid and searchterm.')
        print_usage()
        sys.exit(0)
    try:
        inputs['limit'] = int(inputs['limit'])
    except:
        print('Please input integer value for limit.')
        print_usage()
        sys.exit(0)

    set_logger()
    utils = Utils()
    factory = Pipeline(steps)
    factory.run(inputs, utils)


if __name__ == '__main__':
    main()








