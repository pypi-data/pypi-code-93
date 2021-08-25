class __entityquery__:
    # can omit
    def registerQuery(self, Component: str, *ComponentField: str) -> object:
        if Component == None and ComponentField == None:
            return self.__js__.registerQuery()
        return self.__js__.registerQuery(Component, *ComponentField)

    def addFilterToQuery(self, Query: object, ComponentIdentifier: str):
        self.__js__.addFilterToQuery(Query, ComponentIdentifier)

    def getEntitiesFromQuery(self, Query, *MinMaxComponentField) -> list:
        if MinMaxComponentField == None:
            return self.__js__.getEntitiesFromQuery(Query)
        return self.__js__.getEntitiesFromQuery(Query, *MinMaxComponentField)
    # def :
    #     self.__js__.
