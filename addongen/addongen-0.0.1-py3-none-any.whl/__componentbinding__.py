class __componentbinding__:
    # Component Binding
    def registerComponent(self, ComponentIdentifier: str, ComponentData: object) -> bool:
        return self.__js__.registerComponent(ComponentIdentifier, ComponentData)

    def createComponent(self, EntityObject: object, ComponentIdentifier: str) -> object:
        return self.__js__.createComponent(EntityObject, ComponentIdentifier)

    def hasComponent(self, EntityObject: object, ComponentIdentifier: str) -> bool:
        return self.__js__.hasComponent(EntityObject, ComponentIdentifier)

    # https://bedrock.dev/docs/stable/Scripting#getComponent(EntityObject%2C%20ComponentIdentifier)
    def getComponent(self, EntityObject: object, ComponentIdentifier: str) -> object:
        return self.__js__.getComponent(EntityObject, ComponentIdentifier)

    # https://bedrock.dev/docs/stable/Scripting#applyComponentChanges(EntityObject%2C%20ComponentObject)
    def applyComponentChanges(self, EntityObject: object, ComponentObject: object) -> bool:
        return self.__js__.applyComponentChanges(EntityObject, ComponentObject)

    def destroyComponent(self, EntityObject: object, ComponentIdentifier: str) -> bool:
        return self.__js__.destroyComponent(EntityObject, ComponentIdentifier)
