"""Generate a GraphQL type definition from a model class
"""
from itertools import chain

from pentaquark.exceptions import PentaQuarkConfigurationError
from pentaquark.properties import CypherProperty


class GraphQLTypeBuilder:
    def __init__(self, model):
        self.model = model

    def _get_type_name(self, model=None):
        if model:
            return model.get_label()
        return self.model.get_label()

    def _get_properties_list(self, include_id=True, include_relationships=True, include_non_id_properties=True,
                             include_cypher_properties=False, include_graphql_properties=True):
        properties = ""
        if include_relationships:
            it = chain(self.model._properties.items(), self.model._relationships.items())
        else:
            it = self.model._properties.items()
        for pn, p in it:
            if not p.exposed:
                continue
            if not include_id and (pn == self.model.get_id_property_name()):
                continue
            if (pn != self.model.get_id_property_name()) and not include_non_id_properties:
                continue
            if isinstance(p, CypherProperty) and not include_cypher_properties:
                continue
            gtype = p.get_graphql_type() or p.get_dyn_graphql_type()
            if gtype is None:
                raise PentaQuarkConfigurationError(f"graphql_type is not defined for property "
                                                   f"{self.model.__name__}.{pn}, exclude it")
            if p.help_text:
                properties += f'"{p.help_text}"' + "\n"
            properties += f"{pn}: {gtype}"
            if p.required:
                properties += "!"
            properties += "\n  "
        if include_graphql_properties:
            for pn, p in self.model._graphql_properties.items():
                t = p._graphql_type
                if p._many:
                    t = f"[{t}]"
                properties += f"{pn}: {t}\n  "
        return properties

    def _get_relationship_ids_list(self):
        rels = {}
        for rn, rel in self.model._relationships.items():
            related_obj = rel.get_target_node_class()
            graphql_type = related_obj.get_property_graphql_type()
            rels[rn] = graphql_type
        return "\n  ".join([f"{rel_name}_id: {rel_type}" for rel_name, rel_type in rels.items()])

    def to_graphql_type(self):
        type_name = self._get_type_name()
        properties = "\n  " + self._get_properties_list(include_id=True, include_relationships=True)
        type_def = f"type {type_name} {{{properties}}} \n"
        if self.model._meta.help_text:
            type_def = f'"{self.model._meta.help_text}"\n{type_def}'
        return type_def

    def _get_input_type_name(self, model=None):
        if model is None:
            model = self.model
        return self._get_type_name(model) + "Input"

    def _get_id_input_type_name(self, model=None):
        if model is None:
            model = self.model
        return self._get_type_name(model) + "InputID"

    def _get_filter_input_type_name(self, model=None):
        if model is None:
            model = self.model
        return self._get_type_name(model) + "InputFilter"

    def to_graphql_input_type(self):
        type_name = self._get_input_type_name()
        # FIXME: list of properties to include in the input type should be configurable
        properties = "\n  " + self._get_properties_list(
            include_id=True,
            include_relationships=False,
            include_cypher_properties=False,
            include_graphql_properties=False,
        )
        properties += self._get_relationship_ids_list() + "\n"
        return f"input {type_name} {{{properties}}}\n"

    def to_graphql_id_input_type(self):
        type_name = self._get_id_input_type_name()
        properties = "\n  " + self._get_properties_list(
            include_id=True,
            include_relationships=False,
            include_non_id_properties=False,
            include_cypher_properties=False,
            include_graphql_properties=False)
        return f"input {type_name} {{{properties}}} \n"

    def to_graphql_filter_input_type(self):
        type_name = self._get_filter_input_type_name()
        properties = self._get_properties_list(
            include_id=False,
            include_relationships=False,
            include_non_id_properties=True,
            include_cypher_properties=False,
            include_graphql_properties=False
        )
        if properties:
            properties = "\n  " + properties
            return f"input {type_name} {{{properties}}} \n"
        return f"input {type_name} {{_: Boolean}} \n"  # FIXME: create empty graphql type when possible

    def to_graphql_queries(self):
        """
        Adds two queries:
            - get all
            - get by ID
        :return:
        """
        name = self.model._meta.label.lower()
        id_property = self.model.get_id_property_name()
        if not id_property:
            return ""
        return f'"Retrive all {name} matching filters"\n'\
               f"{name}s(" \
               f"filters: {self._get_filter_input_type_name()}, " \
               f"limit: Int, " \
               f"skip: Int, " \
               f"orderBy: String" \
               f"): [{self._get_type_name()}]\n  " \
               f"{name} ({id_property}: {self.model.get_id_property_graphql_type()}!): {self._get_type_name()}\n  "
        # f"{name}sf (filter: String): [{self._get_type_name()}]\n  "

    def to_graphql_connection_mutations(self):
        connections = {}
        for rn, rel in self.model._relationships.items():
            related_obj = rel.get_target_node_class()
            # if rel.direction == RelationshipDirection.OUTGOING:
            source_name = self._get_type_name(self.model)
            source_input = self._get_id_input_type_name(self.model)
            target_name = rn.title()
            target_input = self._get_id_input_type_name(related_obj)
            # else:
            #     target_name = self._get_type_name(self.model)
            #     target_input = self._get_id_input_type_name(self.model)
            #     source_name = rn.title()
            #     source_input = self._get_id_input_type_name(related_obj)
            key = f"{source_name}To{target_name}"
            connections[key] = f"connect{key} " \
                               f"(start: {source_input}!, end: {target_input}!): SuccessOutput\n"
        return connections

    def _create_mutation(self):
        return f"create{self.model.get_label()} (input: {self._get_input_type_name()}): {self._get_type_name()}\n"

    def _update_mutation(self):
        return f"update{self.model.get_label()} " \
               f"(id: {self.model.get_id_property_graphql_type()}!, " \
               f"input: {self._get_input_type_name()}): {self._get_type_name()}\n"

    def _create_or_update_mutation(self):
        return f"createOrUpdate{self.model.get_label()} " \
               f"(id: {self.model.get_id_property_graphql_type()}, " \
               f"input: {self._get_input_type_name()}): {self._get_type_name()}\n"

    def _delete_mutation(self):
        return [
            f"delete{self.model.get_label()}(id: {self.model.get_id_property_graphql_type()}): SuccessOutput\n",
        ]

    def to_graphql_mutations(self):
        return "".join(
            [
                self._create_mutation(),
                self._update_mutation(),
                self._create_or_update_mutation(),
                *self._delete_mutation(),
            ]
        )
