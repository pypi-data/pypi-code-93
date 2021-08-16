from inspector.windows.base import Bridge, traceback


class DatabaseMixin(Bridge):
    @traceback
    def load(self):
        try:
            super().load()
        except AttributeError:
            pass

        name = self.ctx.selected
        if name is None:
            return []

        locator = self.ctx.load_locator(name)
        if locator is None:
            self.logger.error("No locator with name: %s", name)
            return []

        return name, locator

    @traceback
    def save(self, name, locator, add=False):
        try:
            super().save()
        except AttributeError:
            pass

        with self.ctx.database.lock:
            # Ensure name is unique
            if add:
                basename = name
                idx = 0
                while name in self.ctx.database.names:
                    idx += 1
                    name = f"{basename}{idx}"

            self.ctx.database.update(name, locator)

        # Force manager view to update even if save happens
        # from another window
        self.ctx.force_update()
        self.window.close()
