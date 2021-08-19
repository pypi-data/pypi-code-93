class ROParser():
    def __init__(self, doc) -> None:
        #     "conformsTo": {
        #     "@id": "https://w3id.org/ro/crate/1.1"
        #   },
        if "@graph" not in doc:
            raise ValueError("Not a valid ROCrate file")

        self.__version = "https://w3id.org/ro/crate/1.1"
        self.__doc = doc
        self.__rootId = self.__getRootIdentifier()
        self.__root = self.getElement(self.__rootId)

    def __getRootIdentifier(self):
        for elem in self.__doc["@graph"]:

            if elem["@id"] == "ro-crate-metadata.json":
                version = elem["conformsTo"]["@id"]
                if version != self.__version:
                    raise ValueError(
                        "Valid ROCrate file, but wrong version.\nWanted `https://w3id.org/ro/crate/1.1`, given `{}`".format(version))

                return elem["about"]["@id"]

    @property
    def root(self):
        return self.__root

    @property
    def rootIdentifier(self):
        return self.__rootId

    def getElement(self, id: str, doc: dict = None, expand: bool = False, clean: bool = False, clamps: int = None):
        """Gets the element with given id

        Args:
            id (str): The id you are searching for
            doc (dict, optional): The json dict, you want to search for id. If None, it searches the given dict at this object. Defaults to None.
            expand (bool, optional): Resolves all @id lookups in dicts. Defaults to False.
            clean (bool, optional): Cleans up, all lists with only one element pulls the elements in first layer, all dicts with one element will be accessable directly. Defaults to False.
            clamps (int, optional): All lists only returns this amount of elements. If none, returns all. Defaults to None.

        Returns:
            [type]: [description]
        """
        if doc is None:
            doc = self.__doc["@graph"]

        temp = {}

        for elem in doc:
            if "@id" in elem and elem["@id"] == id:
                temp = elem

        result = {}
        for key, value in temp.items():
            if not "@" in key[0] and expand and isinstance(value, list):
                result[key] = []

                for elem in value:
                    try:
                        tmpRes = self.getElement(
                            elem["@id"], doc=doc, expand=expand, clean=clean, clamps=clamps)
                    except:
                        tmpRes = elem

                    result[key].append(tmpRes)

        temp.update(result)

        if clean:
            return self.__clean(temp, clamps=clamps)

        return temp

    def __clean(self, docs, clamps):
        if not isinstance(docs, (dict, list)):
            return docs

        if not isinstance(docs, list):
            docs = [docs]

        result = []

        try:
            for doc in docs:
                temp = {}

                for key, value in doc.items():
                    if not "@" in key[0]:
                        temp[key] = self.__clean(value, clamps)

                result.append(temp)

        except:
            result = docs

        if clamps is not None and isinstance(result, list) and len(result) >= clamps:
            result = result[:clamps]

        while len(result) == 1:  # pull single values out of lists
            try:
                key, value = list(result.items())[0]
                if not "@" in key[0]:
                    result = value
                else:
                    raise ValueError
            except Exception as e:
                result = result[0]

        return result
