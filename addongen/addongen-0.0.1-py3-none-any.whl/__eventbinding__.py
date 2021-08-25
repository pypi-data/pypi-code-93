class __eventbinding__:
    def registerEventData(self, EventIdentifier: str, EventData: object) -> bool:
        return self.__js__.registerEventData(EventIdentifier, EventData)

    def createEventData(self, EventIdentifier: str) -> object:
        return self.__js__.createEventData(EventIdentifier)

    def listenForEvent(self, EventIdentifier: str, CallbackObject: function) -> bool:
        return self.__js__.listenForEvent(EventIdentifier, CallbackObject)

    def broadcastEvent(self, EventIdentifier: str, EventData: object) -> bool:
        return self.__js__.broadcastEvent(EventIdentifier, EventData)
