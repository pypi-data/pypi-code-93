# See LICENSE for license details.

import pkg_resources

def get_resource_name(name):
    return pkg_resources.resource_filename(__name__, name)

mill_source = get_resource_name('assets/mill')
cache_source = get_resource_name('assets/cache.tar.gz')
