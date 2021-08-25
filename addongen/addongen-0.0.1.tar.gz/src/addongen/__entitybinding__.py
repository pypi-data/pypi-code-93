class __entitybinding__:
    # Entity Bindings
    # can omit
    def createEntity(self, Type: str, TemplateIdentifier: str) -> object:
        if Type == None and TemplateIdentifier == None:
            return self.__js__.createEntity()
        return self.__js__.createEntity(Type, TemplateIdentifier)

    def destroyEntity(self, EntityObject: object) -> bool:
        return self.__js__.destroyEntity(EntityObject)

    def isValidEntity(self, EntityObject: object) -> bool:
        return self.__js__.isValidEntity(EntityObject)
