import urllib
import ssl
import re
import webbrowser
from casatools import ctsys

from casashell import extra_task_modules as __extra_mods

def toolhelp( ):
    import casatools
    from casashell.private.stack_manip import find_frame
    glbl = find_frame( )
    groups = { }     
    for tname in sorted(dir(casatools)):
        if not tname.startswith('_') and tname != 'ctsys' and all( x in dir(getattr(casatools,tname)) for x in ['_info_group_','_info_desc_'] ):
            group = getattr(getattr(casatools,tname),'_info_group_')
            if group in groups:
                groups[group].append((tname,getattr(getattr(casatools,tname),'_info_group_'),getattr(getattr(casatools,tname),'_info_desc_'),getattr(casatools,tname)))
            else:
                groups[group] = [(tname,getattr(getattr(casatools,tname),'_info_group_'),getattr(getattr(casatools,tname),'_info_desc_'),getattr(casatools,tname))]

    toolnames = sorted(groups.keys())
    label_width = max(map(lambda x: len(x),toolnames)) + 1
    print("=" * (label_width + 52))
    print("CASA tools")
    for i in [t for t in toolnames]:
        last_group = ''
        for t in groups[i]:
            if t[1] != last_group:
                last_group = t[1]
                print('-' * (label_width + 52))
                print("> %s" % t[1])
                print('-' * (label_width) + '-' * 52)
            print(("%%%ds : %%s" % label_width) % (t[0].replace('\n',''),t[2].replace('\n','')))
            glbl = find_frame( )
            ctor = [x for x in glbl.keys( ) if x != 'ctsys' and glbl[x] == t[3]]
            if len(ctor) > 0:
                print(("%%%ds |    create: %%s" % label_width) % ('',", ".join(ctor)))
            inst = [x for x in glbl.keys( ) if x != 'ctsys' and isinstance(glbl[x],t[3])]
            if len(inst) > 0:
                print(("%%%ds | instances: %%s" % label_width) % ('',", ".join(inst)))
    print("-" * (label_width + 52))
    print("> singleton objects (used directly)")
    print("-" * (label_width + 52))
    print(("%%%ds : %%s" % label_width) % ('ctsys','set/get casa state'))
    print("=" * (label_width + 52))

def taskhelp( ):

    def collect(groups,module):
        for tname in sorted(dir(module)):
            if not tname.startswith('_') and tname != 'ctsys' and all( x in dir(getattr(module,tname)) for x in ['_info_group_','_info_desc_'] ):
                # split group up by group name separated by misc space and a comma
                for group in ''.join(getattr(getattr(module,tname),'_info_group_').split( )).split(','):
                    if group in groups:
                        groups[group].append((tname,group,getattr(getattr(module,tname),'_info_desc_'),getattr(module,tname)))
                    else:
                        groups[group] = [(tname,group,getattr(getattr(module,tname),'_info_desc_'),getattr(module,tname))]

    import casatasks
    groups = { }
    collect( groups, casatasks )

    try:
        import casaviewer
        collect( groups, casaviewer )
    except: pass

    try:
        import casaplotms
        collect( groups, casaplotms )
    except: pass

    try:
        import casalith
        collect( groups, casalith )
    except: pass

    extra_groups = { }
    for m in __extra_mods:
        try:
            collect( extra_groups, m )
        except: pass

    tasknames = sorted(groups.keys())
    label_width = max(map(lambda x: len(x),tasknames)) + 1
    print("=" * (label_width + 52))
    print("CASA tasks")
    for i in tasknames:
        last_group = ''
        for t in groups[i]:
            if t[1] != last_group:
                last_group = t[1]
                print('-' * (label_width + 52))
                print("> %s" % t[1])
                print('-' * (label_width) + '-' * 52)
            print(("%%%ds : %%s" % label_width) % (t[0].replace('\n',''),t[2].replace('\n','')))
    print("-" * (label_width + 52))
    print("> singleton objects (used directly)")
    print("-" * (label_width + 52))
    print(("%%%ds : %%s" % label_width) % ('casalog','add messages to the CASA log'))
    print("=" * (label_width + 52))
    if len(extra_groups) > 0:
        tasknames = sorted(extra_groups.keys())
        label_width = max(map(lambda x: len(x),tasknames)) + 1
        print("Extra tasks")
        for i in tasknames:
            last_group = ''
            for t in extra_groups[i]:
                if t[1] != last_group:
                    last_group = t[1]
                    print('-' * (label_width + 52))
                    print("> %s" % t[1])
                    print('-' * (label_width) + '-' * 52)
                print(("%%%ds : %%s" % label_width) % (t[0].replace('\n',''),t[2].replace('\n','')))
        print("=" * (label_width + 52))


class __doc(object):
    "command-line Plone help"

    def __init__( self ):

        try:
            import casalith as _casalith
            self.__version = "v%d.%d.%d" % tuple(_casalith.version( )[:3])
        except:
            from casashell import version as _version
            self.__version = "v%d.%d.%d" % tuple(_version( )[:3])

        self.__root_url = "https://casadocs.readthedocs.io/en/"
        self.__top_url =  None
        self.__toc_url = None

        self.__task_dict = { }
        self.__tool_dict = { }
        self.__index_text = None

    def __call__( self, topic=None ):
        "open browser with documentation, try \"doc('toc')\""

        if self.__index_text is None:
            # try the version first
            index_url = self.__root_url + self.__version + "/genindex.html"
            req = urllib.request.Request(index_url,headers={'User-Agent': 'Mozilla/5.0'})
            try:
                with urllib.request.urlopen(req,context=ssl._create_unverified_context()) as url:
                    self.__index_text = url.read().decode('ISO-8859-1')
                if self.__index_text.find('casa') < 0:
                    # not the actual casa index - try again
                    self.__index_text = None
            # except urllib.error.HTTPError as e:
            #    print(e.read())
            #    print(e.code)
            except:
                pass
                
        if self.__index_text is None:
            # it's still None
            print("WARN: online documentation not found corresponding to this version.")
            try:
                # try using latest
                self.__version = "latest"
                index_url = self.__root_url + "latest/genindex.html"
                req = urllib.request.Request(index_url,headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req,context=ssl._create_unverified_context()) as url:
                    self.__index_text = url.read().decode('ISO-8859-1')
                if self.__index_text.find('casa') < 0:
                    # still not found, give up
                    self.__index_text = ""
                else:
                    print("WARN: using the latest documentation, which may not be appropriate for this version.")
            #except urllib.error.HTTPError as e:
            #    print(e.read())
            #    print(e.code)
            #    self.__index_text = ""
            except:
                self.__index_text = ""

            if len(self.__index_text) == 0:
                print("No online documentation appears to be available at the expected locations")              

        if len(self.__index_text) > 0:
            # the urls for this version
            self.__top_url = self.__root_url + self.__version + "/"
            self.__toc_url = self.__top_url + "api/casatasks.html"

            # tools
            try:
                tools_hrefs = re.findall('<a href="(.*)">.*\(class in casatools\).*</a>',self.__index_text)
                toolname_re = re.compile('casatools\.(.*)\.html')
                for href in tools_hrefs:
                    try:
                        this_tool = toolname_re.findall(href)[0]
                        self.__tool_dict[this_tool] = href
                    except:
                        pass
            except:
                pass

            # tasks
            try:
                tasks_hrefs = re.findall('<a href="(.*)">.*\(in module casatasks\..*\).*</a>',self.__index_text)
                taskname_re = re.compile('casatasks\..*\.(.*)\.html')
                for href in tasks_hrefs:
                    try:
                        this_task = taskname_re.findall(href)[0]
                        self.__task_dict[this_task] = href
                    except:
                        pass
            except:
                pass

        else:
            # nothing found, ultimate fallback is the main casa documentation page
            self.__toc_url = "https://casa.nrao.edu/index_docs.shtml"
            self.__top_url = self.__toc_url

        if type(topic) != str or topic == "toc":
             webbrowser.open_new_tab(self.__toc_url)
        elif topic == "start":
             webbrowser.open_new_tab(self.__top_url)
        elif topic in self.__task_dict:
             webbrowser.open_new_tab(self.__top_url+self.__task_dict[topic])
        elif topic in self.__tool_dict:
             webbrowser.open_new_tab(self.__top_url+self.__tool_dict[topic])
        else:
             webbrowser.open_new_tab(self.__top_url if len(self.__task_dict) == 0 else self.__toc_url)

doc = __doc( )
del __doc
