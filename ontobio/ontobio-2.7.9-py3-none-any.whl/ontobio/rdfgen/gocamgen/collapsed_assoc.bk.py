import logging
from typing import List, Dict
from ontobio.ontol_factory import OntologyFactory
from ontobio.io.gpadparser import GpadParser
from ontobio.io.assocparser import SplitLine
from ontobio.model.association import GoAssociation, ymd_str
from ontobio.rdfgen.gocamgen import errors

logger = logging.getLogger(__name__)

GPAD_PARSER = GpadParser()
BINDING_ROOT = "GO:0005488"  # binding
IPI_ECO_CODE = "ECO:0000353"


class CollapsedAssociationSet:
    def __init__(self, associations: List[GoAssociation], ontology, gpi_entities):
        self.associations = associations
        self.collapsed_associations = []
        self.assoc_dict = {}
        self.go_ontology = ontology
        self.gpi_entities = gpi_entities
    #
    # def setup_ontologies(self):
    #     if self.go_ontology is None:
    #         self.go_ontology = OntologyFactory().create("go")

    # def collapse_annotations(self):
        # Here we shall decide the distinct assertion instances going into the model
        # This will reduce/eliminate need to SPARQL model graph
        # Group by:
        # 		1. ID
        # 		2. qualifiers (normalize order; any array gotta do this)
        # 		3. primary term
        # 		4. With/From (if primary term is BINDING_ROOT or descendant)
        # 		5. Extensions
        # 	Collapse multiple:
        # 		1. Reference
        # 		2. Evidence Code
        #       3. With/From (if primary term is not BINDING_ROOT or descendant)
        # 		4. Source line
        # 		5. Date
        # 		6. Assigned by
        # 		7. Properties
        # self.setup_ontologies()

        for a in self.associations:
            # Header
            header_with_froms, line_with_froms = self.get_with_froms(a)  # Handle pipe separation according to import requirements
            cas = []
            for wf in header_with_froms:
                ca = self.find_or_create_collapsed_association(a, wf)
                association_line = CollapsedAssociationLine(a, line_with_froms)
                ca.lines.append(association_line)
                cas.append(ca)

    def find_or_create_collapsed_association(self, association: GoAssociation, with_from):
        query_header = {
            'subject': {
                'id': association.subject.id
            },
            'qualifiers': sorted(association.qualifiers),
            'object': {
                'id': association.object.id
            },
            'object_extensions': get_annot_extensions(association),
            'negated': association.negated
        }
        if with_from and "header" in with_from:
            query_header['evidence'] = {'with_support_from': sorted(with_from['header'])}
        # for ca in self.collapsed_associations:
        #     if ca.header == query_header:
        #         return ca
        ca = self.find_by_go_association(association)
        if ca:
            return ca
        else:
            ca = CollapsedAssociation(association)
            self.collapsed_associations.append(ca)
            return ca

    def find_by_go_association(self, association: GoAssociation):
        for ca in self.collapsed_associations:
            if ca.header_data_matches(association, self.gpi_entities):
                return ca
            # if ca.header == query_header:
            #     return ca

    def __iter__(self):
        return iter(self.collapsed_associations)

    def get_with_froms(self, annot: GoAssociation) -> List:
        header_with_froms, line_with_froms = [], []

        # The craziest example:
        # MGI:1  GO:0005515  IPI  PR:1,PR:2|WEIRD:1,PR:3|MGI:2
        source_line = annot.source_line
        vals = source_line.split("\t")
        with_from_col = vals[6]
        # Parse into array (by "|") of arrays (by ",")
        with_from_ds = []  # The list of lists
        for piped_with_from in with_from_col.split("|"):
            # Will be bypassing ontobio ID validation? Let's try teaming up with ontobio functions!
            split_line = SplitLine(line=source_line, values=vals, taxon="")  # req'd for error reporting in ontobio?
            validated_comma_with_froms = GPAD_PARSER.validate_pipe_separated_ids(piped_with_from, split_line,
                                                                                 empty_allowed=True, extra_delims=",")
            with_from_ds.append(validated_comma_with_froms)

        # Now arrange these into "header" and "line" values
        eco_code = str(annot.evidence.type)
        term = str(annot.object.id)
        is_binding = eco_code == IPI_ECO_CODE and BINDING_ROOT in self.go_ontology.ancestors(term, reflexive=True)
        if is_binding:
            # Using GPI, check with_froms for taxon equivalency to subj_id
            if self.gpi_entities:
                subject_id = str(annot.subject.id)
                if subject_id in self.gpi_entities:
                    subject_entity = self.gpi_entities[subject_id]
                else:
                    error_message = "Annotation Object ID '{}' missing from provided GPI. Skipping annotation translation.".format(subject_id)
                    logger.warning(error_message)
                    # Throw Exception and except-skip in model builder
                    raise errors.GocamgenException(error_message)
                values_separated = []
                for wf in with_from_ds:
                    wf_separated = {
                        "header": [],
                        "line": []
                    }
                    for wf_id in wf:
                        wf_entity = self.gpi_entities.get(wf_id)
                        if wf_entity and wf_entity.get("taxon") == subject_entity["taxon"]:
                            wf_separated['header'].append(wf_id)
                        else:
                            wf_separated['line'].append(wf_id)
                    values_separated.append(wf_separated)
                return values_separated
            else:
                # Everything is defaulted to header if no GPI available
                return [{"header": wf} for wf in with_from_ds]
        else:
            # Everything is defaulted to line if not binding
            return [{"line": wf} for wf in with_from_ds]

    def header_with_froms(self, association: GoAssociation):
        # Returns with_froms that should be header-level
        pass

    def line_with_froms(self, association: GoAssociation):
        # Returns with_froms that should be line-level
        pass


class CollapsedAssociation:
    def __init__(self, association: GoAssociation):
        # TODO: Refactor out complex dictionary structure - reuse GoAssociation
        # header = {
        #     'subject': {
        #         'id': association.subject.id
        #     },
        #     'qualifiers': sorted(association.qualifiers),
        #     'object': {
        #         'id': association.object.id
        #     },
        #     'object_extensions': get_annot_extensions(association),
        #     'negated': association.negated
        # }
        # self.header = header
        self.subject = association.subject
        self.object = association.object
        self.negated = association.negated
        self.qualifiers = sorted(association.qualifiers, key=lambda q: str(q))
        self.with_froms = []
        self.object_extensions = association.object_extensions
        self.lines: List[CollapsedAssociationLine] = []

    def header_data_matches(self, association: GoAssociation, gpi_entities):
        # Needs access to gpi_entities, which is currently only on CollapsedAssociationSet
        # self.with_froms == header_with_froms(association) and
        if self.subject_id() == str(association.subject.id) and \
           self.object_id() == str(association.object.id) and \
           self.negated == association.negated and \
           self.qualifiers == sorted(association.qualifiers, key=lambda q: str(q)) and \
           self.object_extensions == association.object_extensions:
            return True
        return False

    def subject_id(self):
        # if "subject" in self.header and "id" in self.header["subject"]:
        #     return self.header["subject"]["id"]
        return str(self.subject.id)

    def object_id(self):
        # if "object" in self.header and "id" in self.header["object"]:
        #     return self.header["object"]["id"]
        return str(self.object.id)

    def annot_extensions(self):
        # if "object_extensions" in self.header:
        #     return self.header["object_extensions"]
        return self.object_extensions

    def with_from(self):
        # if "evidence" in self.header and "with_support_from" in self.header["evidence"]:
        #     return self.header["evidence"]["with_support_from"]
        return self.with_froms

    def __str__(self):
        # TODO: Reconstruct GPAD format or original line - could mean multiple lines for each evidence
        return "{} - {}".format(self.subject_id(), self.object_id())

    def __iter__(self):
        return iter(self.lines)


def dedupe_extensions(extensions):
    new_extensions = []
    for i in extensions:
        if i not in new_extensions:
            new_extensions.append(i)
    return new_extensions


class CollapsedAssociationLine:
    def __init__(self, assoc: GoAssociation, with_from=None):
        self.source_line = assoc.source_line
        self.references = [str(ref) for ref in sorted(assoc.evidence.has_supporting_reference, key=lambda x: str(x))]
        self.evidence_code = str(assoc.evidence.type)
        self.date = assoc.date
        self.assigned_by = assoc.provided_by
        self.with_from = with_from
        self.annotation_properties = assoc.properties
        # self.annotation_properties = {}
        # for prop, vals in assoc.properties.items():
        #     self.annotation_properties[str(prop)] = vals

        # if "annotation_properties" in assoc:
        #     self.annotation_properties = assoc["annotation_properties"]

    def as_dict(self):
        ds = {
            "source_line": self.source_line,
            "evidence": {
                "type": self.evidence_code,
                "has_supporting_reference": self.references
            },
            "date": self.date,
            "provided_by": self.assigned_by,
        }
        if self.annotation_properties:
            ds["annotation_properties"] = self.annotation_properties
        if self.with_from:
            ds["evidence"]["with_support_from"] = self.with_from
        return ds


def get_annot_extensions(annot: GoAssociation):
    return annot.object_extensions


def extract_properties_from_string(prop_col):
    props = prop_col.split("|")
    props_dict = {}
    for p in props:
        k, v = p.split("=")
        if k in props_dict:
            props_dict[k].append(v)
        else:
            props_dict[k] = [v]
    return props_dict


def extract_properties(annot):
    cols = annot["source_line"].rstrip().split("\t")
    if len(cols) >= 12:
        prop_col = cols[11]
        annot["annotation_properties"] = extract_properties_from_string(prop_col)
    return annot
