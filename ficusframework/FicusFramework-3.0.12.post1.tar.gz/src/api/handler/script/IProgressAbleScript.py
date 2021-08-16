from api.handler.IProgressAble import IProgressAble
from api.handler.script import ScriptHandlerHolder


class IProgressAbleScript(IProgressAble):

    def update_task_progress(self, progress: float):
        handler = ScriptHandlerHolder.cacheHandler()
        handler.update_task_progress(progress)
