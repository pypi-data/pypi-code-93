from discordbot import error
from discordbot.cache import cached
import time, json

class Snowflake:
    def __init__(self, v):
        self.valid = True
        self.v = v
        
        try:
            if not isinstance(self.v, int):
                self.v = int(self.v)
            
            self.timestamp = ((self.v >> 22) & 0x3ffffffffff + 1420070400000) / 1000.0
        except:
            self.valid = False
        
        if not self.valid:
            self.timestamp = time.time() - 3600.0
    
    def __str__(self):
        return str(self.v)

def check_requirements(obj):
    for f in obj.__class__.required_fields:
        if not f in obj.raw:
            raise error.InvalidAPIObject("'%s' object did not contain required field: %s" % (obj.__class__.__name__, f))

def set_partials(obj):
    obj.partial = False
    for f in obj.__class__.partial_fields:
        if f in obj.raw:
            obj.__dict__[f] = obj.raw[f]
        else:
            obj.__dict__[f] = None
            obj.partial = True

def merge_partials(new, old):
    partial = False
    for f in new.__class__.partial_fields:
        if new.__dict__[f] is None:
            new.__dict__[f] = old.__dict__[f]
        else:
            old.__dict__[f] = new.__dict__[f]
        
        if new.__dict__[f] is None:
            partial = True
    
    new.partial = partial
    old.partial = partial

class APIObject:
    required_fields = []
    partial_fields = []
    cache_id = "default"
    
    def cache_dump(self):
        #d = {}
        #for f in self.required_fields + self.partial_fields:
        #    d[f] = self.__dict__[f]
        #return json.dumps(d)
        return json.dumps(self.raw)
    
    def cache_load(self, d):
        #d = json.loads(d)
        #for f in d:
        #    self.__dict__[f] = d[f]
        self.__init__(json.loads(d))
    
    def update_cache(self):
        if self.cache_id in self.cache:
            merge_partials(self, self.cache[self.cache_id])
        else:
            self.cache[self.cache_id] = self

@cached
class Guild(APIObject):
    required_fields = ['id']
    partial_fields = []
    
    #def update_cache(new_object):
    #    if new_object.id in Guild.cache:
    #        old_object = Guild.cache[new_object.id]
    #        merge_partials(new_object, old_object)
    #    else:
    #        Guild.cache[new_object.id] = new_object
    
    
    def __init__(self, raw):
        self.raw = raw
        
        check_requirements(self)
        try:
            self.snowflake = Snowflake(self.raw['id'])
            self.id = str(self.snowflake)
        except BaseException as e:
            raise error.InvalidAPIObject("'%s' could not be parsed w/ error: %s" % (self.__class__.__name__, e))
        
        set_partials(self)
        #self.__class__.update_cache(self)
        self.cache_id = self.id
        self.update_cache()

@cached
class Channel(APIObject):
    required_fields = ['id']
    partial_fields = []
    
    #def update_cache(new_object):
    #    if new_object.id in Channel.cache:
    #        old_object = Channel.cache[new_object.id]
    #        merge_partials(new_object, old_object)
    #    else:
    #        Channel.cache[new_object.id] = new_object
    
    def __init__(self, raw):
        self.raw = raw
        
        check_requirements(self)
        try:
            self.snowflake = Snowflake(self.raw['id'])
            self.id = str(self.snowflake)
        except BaseException as e:
            raise error.InvalidAPIObject("'%s' could not be parsed w/ error: %s" % (self.__class__.__name__, e))
        
        set_partials(self)
        self.cache_id = self.id
        self.update_cache()
    
    def __str__(self):
        return "<#%s>" % self.id

@cached
class User(APIObject):
    required_fields = ['id']
    partial_fields = ['username', 'discriminator']
    
    #def update_cache(new_object):
    #    if new_object.id in User.cache:
    #        old_object = User.cache[new_object.id]
    #        merge_partials(new_object, old_object)
    #    else:
    #        User.cache[new_object.id] = new_object
    
    def __init__(self, raw):
        self.raw = raw
        
        check_requirements(self)
        try:
            self.snowflake = Snowflake(self.raw['id'])
            self.id = str(self.snowflake)
        except BaseException as e:
            raise error.InvalidAPIObject("'%s' could not be parsed w/ error: %s" % (self.__class__.__name__, e))
        
        set_partials(self)
        self.cache_id = self.id
        self.update_cache()
    
    def __str__(self):
        return "<@%s>" % self.id

@cached
class Message(APIObject):
    required_fields = ['id', 'author', 'channel_id', 'content']
    partial_fields = ['guild_id']
    
    #def update_cache(new_object):
    #    if new_object.id in Message.cache:
    #        old_object = Message.cache[new_object.id]
    #        merge_partials(new_object, old_object)
    #    else:
    #        Message.cache[new_object.id] = new_object
    
    def __init__(self, raw):
        self.raw = raw
        
        check_requirements(self)
        try:
            self.snowflake = Snowflake(self.raw['id'])
            self.id = str(self.snowflake)
            
            self.content = str(self.raw['content'])
        except BaseException as e:
            raise error.InvalidAPIObject("'%s' could not be parsed w/ error: %s" % (self.__class__.__name__, e))
        
        self.channel = Channel({'id': self.raw['channel_id']})
        self.author = User(self.raw['author'])
        
        set_partials(self)
        
        if self.guild_id is None:
            self.guild = None
        else:
            self.guild = Guild({'id': self.raw['guild_id']})
        
        self.cache_id = self.id
        self.update_cache()
    
    def get_url(self):
        return "https://discord.com/channels/%s/%s/%s" % (self.guild.id if not self.guild is None else "???", self.channel.id, self.id)
    
    def __str__(self):
        return "Message sent by %s in %s: %s" % (self.author, self.channel, self.content)



# default cache limits
Guild.cache.set_limit(50, 1_000) # rather small memory footprint
Channel.cache.set_limit(50, 1_000) # ditto
User.cache.set_limit(10, 1_000) # larger
Message.cache.set_limit(1_000, 100_000) # largest, but by far most important