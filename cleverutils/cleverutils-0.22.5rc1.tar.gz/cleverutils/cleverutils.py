
"""
A collection of high level functions, classes, and methods tailored to the author's current level and style of Python coding.
"""
import time
import json
from pathlib import Path
import inspect
from itertools import islice
import datetime
from pprint import pprint
try:
    from cleverdict import CleverDict
except:
    # When cleverdict isn't installed but is on PYTHONPATH:
    from cleverdict.cleverdict import CleverDict
from cleverdict.cleverdict import get_app_dir
import os
# import logging
import re
from random import choice
import requests
import json
import functools
import pyperclip
from lxml import etree
import webbrowser

class Snapshot:
    save_file_path = Path("webpage_snapshots.json").absolute()
    """
    Time-coded copy of a scraped webpage with methods for comparing diffs.
    .latest stores the most recent fetch results
    .snapshots stores all fetch results which are store in Snapshot.save_file_path

    ARGS:

        label: Human readable short label; can include spaces
        url: Web address of the entry point, usually a search results page
        root: The top level domain name of the website being processed
        filter: Mandatory text snippet for a link to appear in self.links
    """
    def __init__(self, label="rightmove land", url="", root="https://www.rightmove.co.uk", filter="/properties/"):
        self.fetch_file()
        self.label = label
        self.url = url or list(self.all_snapshots[self.label].keys())[0]
        self.root = root
        self.filter = filter
        self.fetch_links()
        self.save_file()

    # TODO: delete_by_id, delete_by_label, delete_by_url, delete_by_date, filter_by_date

    @property
    def snapshots(self):
        """ Returns a list of all snapshots for the current label """
        return list(self.all_snapshots[self.label][self.url].values())

    def fetch_file(self):
        """Creates .all_snapshots based on JSON file"""
        if Snapshot.save_file_path.is_file():
            with open(Snapshot.save_file_path, "r") as file:
                self.all_snapshots = json.load(file)
        else:
            self.all_snapshots = {self.label: {self.url: {}}}

    def compare(self, a=-2, b=-1):
        """
        Sets attribute .a for snapshot a and .b snapshot b
        Prints (set) comparisons for A-B and B-A
        Compares the most recent two snapshots by default
        """
        try:
            self.a = set(self.snapshots[a])
        except IndexError:
            self.a = set()
        self.b = set(self.snapshots[b])
        print(f"\nComparing snapshot indexes {a} and {b} for {self.label}:")
        print(f"\nIn Set A but not in Set B: {self.a-self.b or 'No difference'}")
        print(f"\nIn Set B but not in Set A: {self.b-self.a or 'No difference'}\n")

    def open(self, keyword = "url"):
        if keyword.lower() == "url":
            open_list = {self.url}
        if keyword.lower() == "all":
            open_list = self.all_snapshots[self.label][self.url].values()
            open_list = {x for x in open_list for x in x}
        if keyword.lower() == "ab":
            if not hasattr(self, "a") or not hasattr(self, "b"):
                self.compare()
            open_list = self.a-self.b
        if keyword.lower() == "ba":
            if not hasattr(self, "a") or not hasattr(self, "b"):
                self.compare()
            open_list = self.b-self.a
        if keyword.lower() == "a":
            if not hasattr(self, "a"):
                self.compare()
            open_list = self.a
        if keyword.lower() == "b":
            if not hasattr(self, "b"):
                self.compare()
            open_list = self.b
        if "-" in keyword:
            # Open a range of snapshots based on numeric ID
            first, last = keyword.split("-")
            open_list = self.snapshots
            open_list = {x for x in open_list[int(first):int(last)] for x in x}
        for link in open_list:
            webbrowser.open(link)

    def fetch_links(self):
        html = etree.HTML(requests.get(self.url).content)
        links = {x.get('href') for x in html.findall(".//a") if self.filter in str(x.get('href'))}
        links = [x for x in links]
        self.latest = {self.label: {self.url: {str(datetime.datetime.now()): [self.root+x for x in links]}}}
        if self.all_snapshots.get(self.label):
            try:
                self.all_snapshots[self.label][self.url].update(self.latest[self.label][self.url])
            except Exception as E:
                print("oh!", E)
        else:
            self.all_snapshots.update(self.latest)

    def save_file(self):
        with open(Snapshot.save_file_path, "w") as file:
            json.dump(self.all_snapshots, file, indent=4)
            print(f"{Snapshot.save_file_path} updated.")


def scrape_images(url=None, path = None, suffixes = ".png .jpg .gif"):
    """NB does not prevent ovewriting or select max size image"""
    from pathlib import Path
    import requests
    import concurrent.futures
    import pyperclip
    import zipfile
    from lxml import etree

    if url is None:
        url = pyperclip.paste()
    if path is None:
        path = Path().cwd() / "Downloaded Images"
        if not path.is_dir():
            path.mkdir()
    def get_image_name(image_url):
            for suffix in suffixes.split():
                name = ""
                if suffix in image_url:
                    name = image_url.split(suffix)[0]
                    if "//" in name:
                        name = name.split("//")[1]
                    for char in "//\\&%=?+;,":
                        name = name.replace(char, "_")
                    return name+suffix
    def download_image(image_url):
        try:
            response = requests.get(image_url)
            image_name = get_image_name(image_url)
            if not image_name:
                print(f"\n !  Unsupported image suffix:\n    {image_url}\n")
                return
            file_path = path / image_name
            with open(file_path, "wb") as file:
                file.write(response.content)
            return file_path
        except Exception as E:
            print(f"\n{E}\n")
    def get_url(image_element):
        if image_element.get('href'):
            return image_element.get('href')
        if image_element.get('srcset'):
            return image_element.get('srcset').split(",")[-1].split(" ")[1]
        else:
            return image_element.get('src')
    ## So simple!
    html = etree.HTML(requests.get(url).content)
    images = html.findall(".//img")
    galleries = [x for x in html.findall(".//a") if "/galler" in str(x.get('href'))]
    # d = [scrape_images(get_url(x)) for x in galleries]
    ## TODO: Recognise and loop through galleries, recursively
    for suffix in suffixes.split():
        images += [x for x in html.findall(".//a") if suffix in x.get('href')]
    images = [x for x in images if "base64" not in str(etree.tostring(x)).lower()]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(download_image, param) for param in {get_url(x) for x in images}]
        results = {f.result() for f in futures}
    downloads = [x for x in results if x]
    print(f"\n >  Downloaded {len(downloads)} images out of {len(results)} to:\n    {path}\n")
    return downloads

INSTALL_PATH = Path(__file__).parent.parent
ICON_PATH = (Path(__file__).parent).with_name("cleverutils.ico")

def get_quote(category=None):
  """
  Returns a nicely formatted Quote of the Day from theysaidso.com.
  If no category is specified, pick one at random.

  For unregistered use there is a limit of 10 requests per hour.
  """
  if category is None:
      category = choice(["management", "inspire", "life", "funny", "love", "sports",])
  url = f"http://quotes.rest/qod.json?category={category}"
  try:
    quote = json.loads(requests.get(url).text)['contents']['quotes'][0]
    text = f"\"{quote['quote']}\" ({quote['author']})"
    image_link = quote['background']
    tags = quote['tags']
  except KeyError:
    text = "Error - probably exceeded 10 requests per hour"
    image_link="https://media.giphy.com/media/KHKGN7BUO3zsaQWC46/giphy.gif"
    tags=["ratelimited"]
  return text, image_link, tags

def get_time(time_format="standard"):
    """
    Returns the current local time in a given format.

    Kwargs:
        time_format='standard' -> returns format: '2021-03-21 06:24:14'
        time_format='numeric'  -> returns format: '202103210624'

    """
    if time_format == "numeric":
        # 12 digit, all numeric.  Useful as a concise timestamp
        return time.strftime("%Y%m%d%H%M", time.localtime())
    else:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def timer(func):
    """
    Wrapper to start the clock, run func(), then stop the clock. Simples.
    Designed to work as a decorator... just put @timer in the line above the
    original function.
    """
    def wrapper(*args, **kwargs):
        file_path = Path(get_app_dir("cleverutils"))
        file_path.mkdir(exist_ok=True)
        file_path /= "timer_logs.txt"
        if not file_path.is_file():
            file_path.touch()
        # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s|%(levelname)s|%(message)s', filename=file_path,)
        # List of available options here:
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        print(f"\n ⓘ  Timings logged to:\n    {file_path}")
        start = time.perf_counter()
        data = func(*args, **kwargs)
        # logging.info(f"Function {func.__name__!r} took {round(time.perf_counter()-start,2)} seconds to complete.")
        return (data)
    return wrapper


def any_args(func):
    """
    Wrapper to allow (most) functions that expect iterable(s) as argument(s)
    to also accept a single value argument or no argument at all, without
    having to code that conversion inside the function itself.

    In such cases, functions like the following would fail otherwise:

    def test(iterable, *args):
        for item in iterable:
            print(item)

    >>> test()
    TypeError: test() missing 1 required positional argument: 'data_list'

    >>> test(1)
    TypeError: 'int' object is not iterable

    >>> test(None)
    TypeError: 'NoneType' object is not iterable

    This wrapper also has the effect of treating a string as a single
    object instead of a sequence of character objects.

    >>> test("xyz")
    x
    y
    z

    To use this wrapper on other functions from the command line, type:
    >>> any_args(func)(args)

    This wrapper is mainly intended to work as a decorator though...
    Just put '@any_args' in the line above the function you want to modify.

    TESTS:

    >>> any_args(test)()
    ()
    >>> any_args(test)([])
    []
    >>> any_args(test)({})
    {}
    >>> any_args(test)(None)
    None
    >>> any_args(test)(False)
    False
    >>> any_args(test)((1,2,3))
    (1, 2, 3)
    >>> any_args(test)([1,2,3])
    [1, 2, 3]
    >>> any_args(test)({1,2,3})
    {1, 2, 3}
    >>> any_args(test)([1],1,{1},(1), "x")
    1
    >>> any_args(test)("x")
    x
    >>> any_args(test)("abcxyz")
    abcxyz
    >>> any_args(test)("x", "y", "z")
    x
    >>> any_args(test)(1)
    1
    >>> any_args(test)("x", 1)
    x
    >>> any_args(test)(1,"x")
    1

    See also cleverutils.args_kwargs_to_list() and cleverutils.make_list
    """
    def wrapper(*args, **kwargs):
        if len(args) == 0:
            args =[()]
        if len(args) == 1:
            args = [args]
        if len(args) > 1 and not hasattr(args[0], "__iter__"):
            args = list(args)
            args[0] = [args[0]]
        data = func(*args, **kwargs)
        return (data)
    return wrapper

def make_list(func):
    """
    Increases the tolerance of any wrapped function which previously could
    only process a [list] type argument of (0..n) items.  The wrapped function
    should now be able to handle single and multiple (non-list) values, tuples,
    sets, (additional) arguments (*args), keyword arguments (**kwargs),
    booleans, None type, mixes of all these things, or no arguments at all.

    Remember to 'import functools' and then just place the decorator
    '@make_list' in the line above the definition of the function you want
    to make more tolerant e.g. 'def wrapped_func(a_list):'

    For an alternative approach see also @singledispatch:
    https://www.python.org/dev/peps/pep-0443/#id15

    and also cleverutils.any_args()
    and also cleverutils.args_kwargs_to_list()
    """
    @functools.wraps(func)  # preserve __doc__, __name__ etc. of func
    def wrapper(*args, **kwargs):
        a_list = []
        for arg in args:
            a_list.extend(arg if isinstance(arg, (tuple, list, set)) else [arg])
        for kwarg, arg in kwargs.items():
            a_list.append({kwarg: arg})
        return func(a_list)
    return wrapper

def args_kwargs_to_list(*args, **kwargs):
    """ Helper function to convert args and kwargs to a single list e.g.
    for functions which are only expecting a list as an argument.

    Alternative to cleverutils.make_list and cleverutils.any_args
    """
    a_list = []
    for arg in args:
        a_list.extend(arg if isinstance(arg, (tuple, list, set)) else [arg])
    for kw, arg in kwargs.items():
        a_list.append({kw: arg})
    return a_list


def list_batches(data, batch_size=10):
    """ Yields a sublist with batch_size values.

    kwargs:
    batch_size : Maximum size of any sublist returned; last sublist may be less.
    browsers: Number of browers, to run; Calculate batch_size accordingly

    x = list_batches(data)
    try:
        while True:
            sublist = next(x)
            do_stuff(sublist)
    except StopIteration:
        pass
    finally:
        del iterator

    Returns
    -------
    A generator object of lists.
    """
    # it = iter(data)
    # for i in range(0, len(data), batch_size):
    #     yield [x for x in islice(it, batch_size)]
    for i in range(0, len(data), batch_size):
        yield(data[i:i + batch_size])


def dict_batches(data, batch_size=10):
    """ Yields a subdictionary with batch_size keys.

    x = dict_batches(data)
    try:
        while True:
            subdict = next(x)
            do_stuff(subdict)
    except StopIteration:
        pass
    finally:
        del iterator

    Returns
    -------
    A generator object of dicts.
    """
    it = iter(data)
    for i in range(0, len(data), batch_size):
        yield {k:data[k] for k in islice(it, batch_size)}

def to_batches(data, batch_size):
    """
    Calls dict_batches or list_batches respectively to return a generator object
    containing a batches of a given size or less.

    Parameters
    ----------

    data: dict | list | set | tuple
        The source data to be divided into batches.
    batch_size: int
        The maximum number of items for each batch to contain.
        NB the final batch size may be less than batch_size if not divisible.

    Returns
    -------
    A generator object of dicts or iterables respectively.
    """
    if not isinstance(batch_size, int):
        raise TypeError("batch_size must be an integer")
    if not batch_size > 0:
        raise ValueError("batch_size must be positive")
    if batch_size > len(data):
        raise ValueError(f"batch_size must be <= len(data) i.e. {len(data)}")
    function_dispatch = {dict: dict_batches,
                            CleverDict: dict_batches,
                            list: list_batches,
                            tuple: list_batches}
    return function_dispatch[type(data)](data, batch_size)


def convert_to_dict(obj):
    """
    A function takes in a custom object and returns a dictionary representation of the object.
    This dict representation includes meta data such as the object's module and class names required for serialisation to/from JSON.
    """

    #  Populate the dictionary with object meta data
    obj_dict = {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__
    }

    #  Populate the dictionary with object properties
    obj_dict.update(obj.__dict__)
    return obj_dict


def convert_to_json(obj):
    """
    Converts a non-serialisable custom object into JSON by creating a simple
    dict with metadata that IS serialisable, and then using default= argument.
    """
    json.dumps(obj, default=convert_to_dict,indent=4, sort_keys=True)



def dict_to_obj(our_dict):
    """
    Function that takes in a dict and returns a custom object associated with the dict.
    This function makes use of the "__module__" and "__class__" metadata in the dictionary
    to know which object type to create.

    Use object_hook= keyword to run this function with json.loads:

    json.loads(our_dict, object_hook=dict_to_obj)
    """
    if "__class__" in our_dict:
        # Pop ensures we remove metadata from the dict to leave only the instance arguments
        class_name = our_dict.pop("__class__")

        # Get the module name from the dict and import it
        module_name = our_dict.pop("__module__")

        # We use the built in __import__ function since the module name is not yet known at runtime
        module = __import__(module_name)

        # Get the class from the module
        class_ = getattr(module,class_name)

        # Use dictionary unpacking to initialize the object
        obj = class_(**our_dict)
    else:
        obj = our_dict
    return obj

def yt_time(duration):
    """
    Converts YouTube duration (ISO 8061)
    into Seconds

    see http://en.wikipedia.org/wiki/ISO_8601#Durations
    """
    ISO_8601 = re.compile(
        r'P'   # designates a period
        r'(?:(?P<years>\d+)Y)?'   # years
        r'(?:(?P<months>\d+)M)?'  # months
        r'(?:(?P<weeks>\d+)W)?'   # weeks
        r'(?:(?P<days>\d+)D)?'    # days
        r'(?:T' # time part must begin with a T
        r'(?:(?P<hours>\d+)H)?'   # hours
        r'(?:(?P<minutes>\d+)M)?' # minutes
        r'(?:(?P<seconds>\d+)S)?' # seconds
        r')?')   # end of time part
    # Convert regex matches into a short list of time units
    units = list(ISO_8601.match(duration).groups()[-3:])
    # Put list in ascending order & remove 'None' types
    units = list(reversed([int(x) if x != None else 0 for x in units]))
    # Do the maths
    return sum([x*60**units.index(x) for x in units])

def get_path_size(path = Path('.'), recursive=False):
    """
    Gets file size, or total directory size

    Parameters
    ----------
    path: str | pathlib.Path
        File path or directory/folder path

    recursive: bool
        True -> use .rglob i.e. include nested files and directories
        False -> use .glob i.e. only process current directory/folder

    Returns
    -------
    int:
        File size or recursive directory size in bytes
        Use cleverutils.format_bytes to convert to other units e.g. MB
    """
    path = Path(path)
    if path.is_file():
        size = path.stat().st_size
    elif path.is_dir():
        path_glob = path.rglob('*.*') if recursive else path.glob('*.*')
        size = sum(file.stat().st_size for file in path_glob)
    return size

def format_bytes(bytes, unit, SI=False):
    """
    Converts bytes to common units such as kb, kib, KB, mb, mib, MB

    Parameters
    ---------
    bytes: int
        Number of bytes to be converted

    unit: str
        Desired unit of measure for output


    SI: bool
        True -> Use SI standard e.g. KB = 1000 bytes
        False -> Use JEDEC standard e.g. KB = 1024 bytes

    Returns
    -------
    str:
        E.g. "7 MiB" where MiB is the original unit abbreviation supplied
    """
    if unit.lower() in "b bit bits".split():
        return f"{bytes*8} {unit}"
    unitN = unit[0].upper()+unit[1:].replace("s","")  # Normalised
    reference = {"Kb Kib Kibibit Kilobit": (7, 1),
                 "KB KiB Kibibyte Kilobyte": (10, 1),
                 "Mb Mib Mebibit Megabit": (17, 2),
                 "MB MiB Mebibyte Megabyte": (20, 2),
                 "Gb Gib Gibibit Gigabit": (27, 3),
                 "GB GiB Gibibyte Gigabyte": (30, 3),
                 "Tb Tib Tebibit Terabit": (37, 4),
                 "TB TiB Tebibyte Terabyte": (40, 4),
                 "Pb Pib Pebibit Petabit": (47, 5),
                 "PB PiB Pebibyte Petabyte": (50, 5),
                 "Eb Eib Exbibit Exabit": (57, 6),
                 "EB EiB Exbibyte Exabyte": (60, 6),
                 "Zb Zib Zebibit Zettabit": (67, 7),
                 "ZB ZiB Zebibyte Zettabyte": (70, 7),
                 "Yb Yib Yobibit Yottabit": (77, 8),
                 "YB YiB Yobibyte Yottabyte": (80, 8),
                 }
    key_list = '\n'.join(["     b Bit"] + [x for x in reference.keys()]) +"\n"
    if unitN not in key_list:
        raise IndexError(f"\n\nConversion unit must be one of:\n\n{key_list}")
    units, divisors = [(k,v) for k,v in reference.items() if unitN in k][0]
    if SI:
        divisor = 1000**divisors[1]/8 if "bit" in units else 1000**divisors[1]
    else:
        divisor = float(1 << divisors[0])
    value = bytes / divisor
    # if value != 1 and len(unitN) > 3:
    #         unitN += "s" # Create plural unit of measure
    return f"{value:,.0f} {unitN}{(value != 1 and len(unitN) > 3)*'s'}"
