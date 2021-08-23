from os import path
import pkg_resources

# List of compatible firmware builds
compat_fw = [548]

# Official release name
distribution = pkg_resources.get_distribution("moku")
release = distribution.version
location = path.join(distribution.location, "moku")
