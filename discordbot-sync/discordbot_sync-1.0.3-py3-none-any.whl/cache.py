import pathlib, os, shutil
file_root = pathlib.Path(__file__).parent / "_files"

class CacheError(Exception):
    pass

class FileDictionary:
    next_id = 0
    
    def __init__(self, _class):
        self.id = FileDictionary.next_id
        FileDictionary.next_id += 1
        self._class = _class
        
        self.path = file_root / "cache" / str(self.id)
        
        self._memory = {}
        self._keys = []
        self.set_limit(10, 100)
    
    def __del__(self):
        try:
            shutil.rmtree(self.path)
        except:
            pass
        
        try:
            if len(os.listdir(self.path.parent)) == 0:
                shutil.rmtree(self.path.parent)
        except:
            pass
    
    def __getitem__(self, key):
        if not key in self._keys:
            raise KeyError("Invalid Key: %s" % key)
        
        self._keys.remove(key)
        self._keys.append(key)
        
        if not key in self._memory:
            self._move_to_memory(key)
            go_to_file = len(self._keys) - self.limit_in_memory - 1
            if go_to_file >= 0:
                self._move_to_file(self._keys[go_to_file])
        
        return self._memory[key]

    def __setitem__(self, key, value):
        if key in self._keys:
            self._keys.remove(key)
            self._keys.append(key)
            
            if key in self._memory:
                self._memory[key] = value
            else:
                self._memory[key] = value
                try:
                    os.remove(self.path / str(key))
                except:
                    pass
                
                go_to_file = len(self._keys) - self.limit_in_memory - 1
                if go_to_file >= 0:
                    self._move_to_file(self._keys[go_to_file])
        else:
            self._keys.append(key)
            self._memory[key] = value
            
            go_to_file = len(self._keys) - self.limit_in_memory - 1
            if go_to_file >= 0:
                self._move_to_file(self._keys[go_to_file])
            
            self._remove_old_keys()

    def __delitem__(self, key):
        try:
            self._keys.remove(key)
        except:
            raise KeyError("Invalid key: %s" % key)
        
        if key in self._memory:
            del self._memory[key]
            take_place = len(self._keys) - self.limit_in_memory - 1
            if take_place >= 0:
                self._move_to_memory(self._keys[take_place])
        else:
            try:
                os.remove(self.path / str(key))
            except:
                pass
    
    def __contains__(self, key):
        return key in self._keys
    
    def set_limit(self, in_memory, on_file):
        assert isinstance(in_memory, int), "Must be an integer."
        assert isinstance(on_file, int), "Must be an integer."
        
        assert in_memory > 2, "Must be allowed to store at least 2 objects in memory."
        assert on_file >= 0, "on_file parameter must be >= 0."
        
        self.limit_in_memory = in_memory
        self.limit_on_file = on_file
        self._remove_old_keys()
        
        n_keys = len(self._keys)
        for i in range(n_keys):
            age = n_keys - i # 1 = most recent
            
            if age <= self.limit_in_memory:
                if not key in self._memory:
                    self._move_to_memory(key)
            else:
                if key in self._memory:
                    self._move_to_file(key)
    
    def _move_to_file(self, key):
        self.path.mkdir(parents = True, exist_ok = True)
        
        data = self._memory[key].cache_dump()
        with open(self.path / str(key), "w+") as f:
            f.write(data)
        
        del self._memory[key]
    
    def _move_to_memory(self, key):
        data = None
        with open(self.path / str(key), "r") as f:
            data = f.read()
        
        try:
            os.remove(self.path / str(key))
            if len(os.listdir(self.path)) == 0:
                shutil.rmtree(self.path)
        except:
            pass
        
        self._memory[key] = self._class.__new__(self._class)
        self._memory[key].cache_load(data)
    
    def _remove_old_keys(self):
        n_keys = len(self._keys)
        max_items_stored = self.limit_in_memory + self.limit_on_file
        to_delete = n_keys - max_items_stored
        for i in range(to_delete):
            key = self._keys[i]
            if key in self._memory:
                del self._memory[key]
            else:
                try:
                    os.remove(self.path / str(self._keys[i]))
                except:
                    pass
        if to_delete > 0:
            self._keys = self._keys[to_delete:]
    

def cached(_class):
    _class.cache = FileDictionary(_class)
    return _class


if __name__ == "__main__":
    import random, json, time
    
    @cached
    class Test:
        def __init__(self, id):
            self.id = id
            self.something = None
            
            if self.id in Test.cache:
                self.something = Test.cache[self.id].something
            else:
                self.something = random.random()
                Test.cache[self.id] = self
        
        def cache_dump(self):
            return json.dumps({"id": self.id, "something": self.something})
            
        def cache_load(self, data):
            d = json.loads(data)
            self.id = d['id']
            self.something = d['something']
        
        def __str__(self):
            return "%s/%.3f/%s" % (self.id, self.something, hex(id(self)))
    
    a = time.time()
    for i in range(1000):
        Test(random.randint(0, 100))
    print("it took %.1f seconds to cache 100 objects 1000 times" % (time.time() - a))