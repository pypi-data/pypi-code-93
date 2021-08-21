import os
from wafer.settings import *

INSTALLED_APPS = (
    'django_countries',
    'compressor',
    'debconf.themes.empty',
) + INSTALLED_APPS

try:
    import django_extensions
    INSTALLED_APPS += ('django_extensions',)
except ImportError:
    pass

ALLOWED_HOSTS = ["*"]

TEMPLATES[0]['OPTIONS']['context_processors'] += (
    'debconf.context_processors.expose_settings',
    'debconf.context_processors.is_it_debconf',
)

BAKERY_VIEWS += (
    'debconf.views.RobotsView',
    'debconf.views.IndexView',
    'debconf.views.DebConfScheduleView',
    'debconf.views.StatisticsView',
    'debconf.views.ContentStatisticsView',
    'register.views.statistics.StatisticsView',
    'volunteers.views.VolunteerStatisticsView',
)

SANDBOX = False
DEBCONF_ONLINE = False
DEBCONF_LOCAL_CURRENCY = 'USD'

markdown_kwargs = {
    'extensions': [
        'markdown.extensions.smarty',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'mdx_linkify.mdx_linkify',
        'mdx_staticfiles',
    ],
    'output_format': 'html5',
}
MARKITUP_FILTER = ('wafer.markdown.bleached_markdown', markdown_kwargs)
WAFER_PAGE_MARKITUP_FILTER = ('markdown.markdown', markdown_kwargs)
MARKITUP_SET = 'markitup/sets/markdown/'
JQUERY_URL = 'vendor/jquery/jquery.js'

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

STATICFILES_FINDERS = (
    'compressor.finders.CompressorFinder',
) + STATICFILES_FINDERS

SITE_DESCRIPTION = os.getenv("SITE_DESCRIPTION")
SITE_AUTHOR = os.getenv("SITE_AUTHOR")

WAFER_SSO = ('gitlab',)
WAFER_GITLAB_HOSTNAME = 'salsa.debian.org'
WAFER_GITLAB_CLIENT_ID = os.getenv('WAFER_GITLAB_CLIENT_ID')
WAFER_GITLAB_CLIENT_SECRET = os.getenv('WAFER_GITLAB_CLIENT_SECRET')

WAFER_VIDEO_REVIEWER = False

DEBCONF_VENUE_STREAM_HLS_URL = "https://onsite.live.debconf.org/redir/live/main.m3u8"
DEBCONF_VENUE_STREAM_RTMP_URL = "rtmp://onsite.live.debconf.org/redir/front/main_{quality}"
DEBCONF_VENUE_IRC_CHANNELS = ["#debconf"]
