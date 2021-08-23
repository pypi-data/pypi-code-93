from typing import Optional

from power_cogs.callbacks.class_method_callback import ClassMethodCallback


class SaveCheckpointCallback(ClassMethodCallback):
    def __init__(self, checkpoint_interval: Optional[int] = None):
        super(SaveCheckpointCallback, self).__init__("save")
        self.checkpoint_interval = checkpoint_interval

    def before(self, wrapped_obj, f, *args, **kwargs) -> None:
        pass

    def after(self, prev_output, wrapped_obj, f, *args, **kwargs):
        checkpoint_interval = getattr(
            wrapped_obj, "checkpoint_interval", self.checkpoint_interval
        )
        if checkpoint_interval is not None:
            epoch = prev_output["epoch"]
            if epoch % checkpoint_interval == 0:
                self.run_function(wrapped_obj)
        return prev_output
