from deepmerge import always_merger
from flask import current_app


def try_name(nlist,record, default=None):
    for name in nlist:
        try:
            return record[name]
        except:
            continue
    else:
        return default

def schema_mapping(record, pid_type, test_mode = False):

    prefix = current_app.config.get("DOI_DATACITE_PREFIX")
    url = record.canonical_url
    for_test_array = url.split('/')

    test_url_prefix = current_app.config.get("DOI_DATACITE_TEST_URL")
    test_url = test_url_prefix + for_test_array[-3] + '/' + for_test_array[-2] + '/' + for_test_array[-1]

    id_data = {}
    id = record['id']
    always_merger.merge(id_data, {"id": id})
    always_merger.merge(id_data, {"type": pid_type})


    attributes = {"event" :"publish", "prefix": prefix}

    #creators
    creators = try_name(nlist = ['creators', 'authors', 'contributors'], record =record)
    if creators is None:
        always_merger.merge(attributes, {"creators": [{"name" : "Various authors"}]})
    else:
        creators_data = []
        for creator in creators:
            if 'person_or_org' in creator: #dataset type
                creator_data = {"name": creator['person_or_org']['name']}
            elif 'full_name' in creator: #article type:
                creator_data = {"name": creator['full_name']}
            else:
                creator_data = {"name": 'unknown'}
            creators_data.append(creator_data)
        always_merger.merge(attributes, {'creators': creators_data})

    #title
    titles = try_name(nlist=['titles', 'title'], record=record)
    if titles == None:
        always_merger.merge(attributes, {"titles": [{"_" : "Unknown"}]})
    else:
        always_merger.merge(attributes, {"titles": titles})

    #publication year
    if 'publication_year' in record:
        always_merger.merge(attributes, {"publicationYear": record['publication_year']})
    elif 'publication_date' in record:
        date = record['publication_date']
        date_array = date.split('-')
        always_merger.merge(attributes, {"publicationYear": date_array[0]})

    #types
    datatype = try_name(nlist = ['document_type', 'resource_type' ], record =record)
    if datatype == None:
        new_type = "Dataset"  # defaul value
    elif type(datatype) is str:
        new_type = datatype_mapping(datatype)
    elif "type" in datatype:
        type_array = datatype["type"]
        for t in type_array:
            if "title" in t:
                new_type = datatype_mapping(t["title"]["en"])
                break
    always_merger.merge(attributes, {"types": {"resourceTypeGeneral": new_type}})

    #url
    if test_mode:
        always_merger.merge(attributes, {"url": test_url})
    else:
        always_merger.merge(attributes, {"url": record.canonical_url})

    #schemaVersion
    always_merger.merge(attributes, {"schemaVersion": "http://datacite.org/schema/kernel-4"})
    #publisher
    publisher  = try_name(nlist=['publisher'], record=record)

    if publisher != None and (type(publisher) is str):
        always_merger.merge(attributes, {"publisher": publisher})
    else:
        always_merger.merge(attributes, {"publisher": current_app.config.get("DOI_DATACITE_PUBLISHER")}) #default: CESNET

    attributes = {"attributes" : attributes}


    always_merger.merge(id_data, attributes)
    data = {"data" : id_data}


    return data
def datatype_mapping(type):
    datatypes = ["Audiovisual", "Book", "BookChapter", "ComputationalNotebook",
                 "ConferencePaper", "ConferenceProceeding", "Dissertation",
                 "Journal", "JournalArticle", "OutputsManagementPlan",
                 "PeerReview", "Preprint", "Report", "Standard",
                 "Collection", "DataPaper", "Dataset", "Event",
                 "Image", "InteractiveResource", "Model", "PhysicalObject",
                 "Service", "Software", "Sound", "Text", "Workflow", "Other"
                 ]
    type_in_singular = type[:-1]
    for datatype in datatypes:
        if type.upper() == datatype.upper() or type_in_singular.upper() == datatype.upper():
            return(datatype)

    return "Dataset" #default value





