from django.utils.module_loading import import_string
from cms.exceptions import PluginAlreadyRegistered

import_list = [
    "content_width_video",
    "content_width_image",
    "page_card",
    "pullquote",
    "rich_text",
    "hero_image",
    "donate",
    "featured_cta",
    "logo_grid",
    "share_this_page",
]

for plugin in import_list:
    try:
        import_string(f"giant_plugins.{plugin}.cms_plugins.__all__")
    except PluginAlreadyRegistered:
        pass
