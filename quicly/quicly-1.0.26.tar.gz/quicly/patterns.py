import re

PATTERN_NONE = re.compile(r'NONE|NULL|NIL|', re.I)
PATTERN_TRUE = re.compile(r'1|TRUE|T|YES|Y|ON', re.I)
PATTERN_FALSE = re.compile(r'0|FALSE|F|NO|N|OFF', re.I)
PATTERN_BOOL = re.compile(rf'({PATTERN_TRUE.pattern})|({PATTERN_FALSE.pattern})', re.I)
PATTERN_BIN = re.compile(r'[-+]?0?b[01]+', re.I)
PATTERN_OCT = re.compile(r'[-+]?0[0-7]+', re.I)
PATTERN_HEX = re.compile(r'[-+]?0x[\dA-F]+', re.I)
PATTERN_INT = re.compile(r'[-+]?(0|[1-9]\d*)(\.0*)?(e\d+)?', re.I)
PATTERN_UINT = re.compile(r'[+]?(0|[1-9]\d*)(\.0*)?(e\d+)?', re.I)
PATTERN_FLOAT = re.compile(r'[-+]?(0|[1-9]\d*)(\.\d*)?(e\d+)?', re.I)
PATTERN_BASE_ENC = re.compile(r'base(16|32|64|85),.*', re.I)
PATTERN_MD5 = re.compile(r'[\dA-F]{32}', re.I)
PATTERN_SHA1 = re.compile(r'[\dA-F]{40}', re.I)
PATTERN_SHA256 = re.compile(r'[\dA-F]{64}', re.I)
PATTERN_SHA512 = re.compile(r'[\dA-F]{128}', re.I)
PATTERN_UUID = re.compile(r'([\dA-F]{8})-?([\dA-F]{4})-?([\dA-F]{4})-?([\dA-F]{4})-?([\dA-F]{12})', re.I)
PATTERN_DATE = re.compile(r'([0-2]\d{3})[-._年]?(0?[1-9]|1[0-2])[-._月]?(0?[1-9]|[1-2]\d|3[01])[日]?', re.I)
PATTERN_TIME = re.compile(r'([01]\d|2[0-3])[-._:时]?([0-5]\d)[-._:分]?([0-5]\d)[秒]?', re.I)
PATTERN_DATETIME = re.compile(rf'({PATTERN_DATE.pattern})\s*({PATTERN_TIME.pattern})', re.I)
PATTERN_MAC = re.compile(r'[\dA-F]{2}([-:]?[\dA-F]{2}){5}', re.I)
PATTERN_IPV4 = re.compile(r'([01]\d\d|2[0-4]\d|25[0-5])(\.[01]\d\d|2[0-4]\d|25[0-5]){3}', re.I)
PATTERN_DOMAIN = re.compile(r'([\w-]+\.)+[\w-]+', re.I)
PATTERN_URL_USER = re.compile(r'[^:@.]+(:[^@.]+)?', re.I)
PATTERN_URL_HOST = re.compile(rf'(({PATTERN_IPV4.pattern})|({PATTERN_DOMAIN.pattern}))(:\d+)?', re.I)
PATTERN_URL_PATH = re.compile(r'/([^/?#]+/?)*', re.I)
PATTERN_URL_PATH_VARIABLE = re.compile(r'\{[^{}]*\}', re.I)
PATTERN_URL_QUERY = re.compile(r'\?[^=&#]+(=[^&#]+)?(&[^=&#]+(=[^&#]+)?)*', re.I)
PATTERN_URL_FRAGMENT = re.compile(r'#.*', re.I)
PATTERN_URL_NO_PROTO = re.compile(
  rf'({PATTERN_URL_USER.pattern}@)?{PATTERN_URL_HOST.pattern}({PATTERN_URL_PATH.pattern})?({PATTERN_URL_QUERY.pattern})?({PATTERN_URL_FRAGMENT.pattern})?',
  re.I
)
PATTERN_URL_HTTP = re.compile(rf'HTTPS?://{PATTERN_URL_NO_PROTO.pattern}', re.I)
PATTERN_URL_GIT = re.compile(rf'GIT@{PATTERN_URL_HOST.pattern}:([^/]+){PATTERN_URL_PATH.pattern}\.GIT', re.I)
PATTERN_EMAIL = re.compile(rf'[^@]+@{PATTERN_URL_HOST.pattern}', re.I)
PATTERN_PHONE = re.compile(r'([08]\d{2,4})?\d{3,8}', re.I)
PATTERN_MOBILE = re.compile(r'([+]?0{0,2}86[-.\s]?)?(1\d{10})', re.I)
PATTERN_POSTCODE = re.compile(r'\d{6}', re.I)
PATTERN_EMOJI = re.compile(r'(\ud83c[\udf00-\udfff])|(\ud83d[\udc00-\ude4f\ude80-\udeff])|[\u2600-\u2B55]', re.I)
PATTERN_EN = re.compile(r'[A-Z]', re.I)
PATTERN_CN = re.compile(r'[\u4E00-\u9FFF]', re.I)
PATTERN_JP = re.compile(r'[\u0800-\u4DFF]', re.I)
PATTERN_KR = re.compile(r'[\uAC00-\uD7FF]', re.I)
