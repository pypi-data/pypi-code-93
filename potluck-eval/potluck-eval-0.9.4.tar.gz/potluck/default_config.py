BASE_DIR = "."
"""
Base directory to use to look for things like task info, task specs, and
submitted files.
"""

TEMPLATES_DIRECTORY = None
"""
Templates directory for Jinja2 templates. If it's not an absolute path,
it will be relative to the potluck package directory. If left as None,
templates will be loaded from the 'templates' directory in the 'potluck'
package (wherever that's installed).
"""

RESOURCES_DIRECTORY = None
"""
Resources directory for css and js files. If it's not an absolute path,
it will be relative to the potluck package directory. If left as None,
CSS and JS files will be loaded from the 'resources' directory in the
'potluck' package (wherever that's installed).
"""

TASKS_FILENAME = "tasks.json"
"""
The file name of the tasks meta-data file, relative to BASE_DIR. May be
an absolute path instead.
"""

SUBMISSIONS_DIR = "submissions"
"""
Directory to find submissions in, relative to BASE_DIR (or not, if an
absolute path is provided). The submissions directory must have a
directory for each username, within which must be directories for each
submitted task named by the task ID. Submitted files for each task should
be placed in these task directories.
"""

EXAMPLES_DIR = "examples"
"""
Directory to find example submissions in. These submissions are used
along with expectations established by specifications modules to check to
make sure that specifications are working. May be the same as
`SUBMISSIONS_DIR` if you're sure that real users won't ever share the
same username as your example submissions (hard to be sure of this...).
"""

REPORTS_DIR = "reports"
"""
Directory to write reports into, relative to BASE_DIR (or not, if an
absolute path is provided). Per-user sub-directories will be created,
where timestamped reports will be written.
"""

RUBRICS_DIRECTORY = "rubrics"
"""
Directory to write blank rubrics into, relative to BASE_DIR (or not, if
an absolute path is provided).
"""
