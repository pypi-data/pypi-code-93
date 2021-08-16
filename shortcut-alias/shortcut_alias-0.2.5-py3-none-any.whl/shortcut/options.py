from .exceptions import RequiredValue

class Option:
    TYPES = dict(
        string=str,
        integer=int,
        float=float
    )

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.description = kwargs.get("description", None)
        self.short = kwargs.get("short", None)
        self.long = kwargs.get("long", None) 
        self.arg_type = kwargs.get("arg_type", "flag")

        self.default = kwargs.get("default", None)
        self.type = self.TYPES[kwargs.get("type", "string")]
        self.required = kwargs.get("required", False)

        self._verify()

    def _verify(self):
        if not self.name:
            raise RequiredValue("'name' is a required value of an option.")
        
    @staticmethod
    def new(name, conf):
        conf["name"] = name
        return Option(**conf)

    def add_option(self, parser=None):
        option_args = list()
        option_kwargs = dict()

        if self.short:
            if self.short[0] != "-":
                option_args = f"-{self.short}"
            else:
                option_args.append(self.short)
        
        if self.long:
            num_dash = self.long.count("-")
            if num_dash >= 2:
                option_args.append(self.long)
            elif num_dash == 1:
                option_args.append(f"-{self.long}")
            else:
                option_args.append(f"--{self.long}")

        option_kwargs["dest"] = self.name
        
        option_kwargs["required"] = self.required
        
        if self.description:
            option_kwargs["help"] = self.description

        if self.arg_type.lower() == "flag":
            option_kwargs["action"] = "store_true"

        elif self.arg_type.lower() == "data":
            option_kwargs["action"] = "store" 
            option_kwargs["default"] = self.default
            option_kwargs["type"] = self.type
        
        parser.add_argument(*option_args, **option_kwargs)
            
        return parser

    def __repr__(self):
        """ String representation of the class """
        items = []

        for k, v in self.__dict__.items():
            if "_" != k[0]:
                if "pass" in k:
                    v = '*' * len(v)
                
                if isinstance(v, str):
                    items.append(f"{k}='{v}'")
                else:
                    items.append(f"{k}={v}")

        items = ', '.join(items)

        return f"{self.__class__.__name__}({items})"