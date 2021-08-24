
def __add_attribs(data, attribs):
    attribs = dict(attribs)
    attribs.pop("id", "")
    data.update(attribs)


def __add_fields(data, root, fields):
    for field in fields:
        elem = root.find(field)
        data[field] = ("".join(elem.itertext()) if elem is not None else "").strip()


def parse_class(dir, data):
    croot = etree.parse(dir + "/" + data['refid'] + '.xml')
    compd_def = croot.find('compounddef')

    for mem in compd_def.iter('memberdef'):
        refid = mem.attrib['id']
        name = mem.find('name').text.strip()
        assert name in data["members"]
        assert refid in data["members"][name]
        mem_data = data["members"][name][refid]
        __add_attribs(mem_data, mem.attrib)
        __add_fields(mem_data, mem,
                     ("type", "definition", "argsstring", "name", "briefdescription", "detaileddescription"))

    __add_attribs(data, compd_def.attrib)
    __add_fields(data, compd_def, ("briefdescription", "detaileddescription"))
    data['includes'] = [e.text for e in compd_def.findall('includes')]
    data['innerclasses'] = [(e.text, e.attrib['refid']) for e in compd_def.findall('innerclass')]
    data['source_file'] = compd_def.find('location').attrib['file']
    data['classname'] = compd_def.find('compoundname').text.strip()
    ns = '::'.join(data['classname'].split('::')[:-1])
    data['namespace'] = ns

    return data

