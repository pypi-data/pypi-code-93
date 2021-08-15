
class Images(dict):
    def get_free_drive(self):
        for d in range(0, 10):
            if d not in self:
                return d
        return None

    def all_drives(self):
        return sorted(self.keys())

    def cleanup(self):
        for image in self.values():
            image.close()
