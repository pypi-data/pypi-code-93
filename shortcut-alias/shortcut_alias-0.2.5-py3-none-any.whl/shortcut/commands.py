from .exceptions import RequiredValue
from . import SETTINGS
from termcolor import colored
from colorama import Style
import shlex
import subprocess

class Command:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.description = kwargs.get("description", None)
        self.cmd = kwargs.get("cmd", None)
        self.conditionals = kwargs.get("if", [])

        self._verify()

    def _verify(self):
        if not self.name:
            raise RequiredValue("'name' is a required value of a command.")

        if not self.cmd:
            raise RequiredValue("'cmd' is a rrequired value of a command")

        if isinstance(self.cmd, str):
            self.cmd = shlex.split(self.cmd)

    def _replace_var(self, var, variables):
        if ":" in var:
            pre, post = var.split(":")

            if post in variables[pre]:
                return variables[pre][post]

        return var

    def _process_conditional(self, name, value, conditional):
        
        if "eq" in conditional.keys():
            if value == conditional["eq"]:
                return ( True, f"{value} ({name}) equal to {conditional['eq']}")
            else:
                return ( False, f"{value} ({name}) not equal to {conditional['eq']}")
        
        if "neq" in conditional.keys():
            if value != conditional["neq"]:
                return ( True, f"{value} ({name}) not equal to {conditional['neq']}")
            else:
                return ( False, f"{value} ({name}) equal to {conditional['neq']}")
        
        
        if isinstance(value, (int, float)):
            if "gt" in conditional.keys():
                if value > conditional["gt"]:
                    return ( True, f"{value} ({name}) greater than {conditional['gt']}")
                else:
                    return ( False, f"{value} ({name}) less than or equal to {conditional['gt']}")

            if "ge" in conditional.keys():
                if value >= conditional["ge"]:
                    return ( True, f"{value} ({name}) greater than or equal to {conditional['ge']}")
                else:
                    return ( False, f"{value} ({name}) less than {conditional['ge']}")
            
            if "lt" in conditional.keys():
                if value < conditional["lt"]:
                    return ( True, f"{value} ({name}) less than {conditional['lt']}")
                else:
                    return ( False, f"{value} ({name}) greater than or equal to {conditional['lt']}")

            if "le" in conditional.keys():
                if value <= conditional["le"]:
                    return ( True, f"{value} ({name}) less than or equal to {conditional['le']}")
                else:
                    return ( False, f"{value} ({name}) greater than {conditional['le']}")

        if isinstance(value, dict):
            if "return" in conditional.keys():
                if value["return"] == conditional["return"]:
                    return ( True, f"{name} returned {conditional['return']}")
                else:
                    return ( False, f"{name} returned {conditional['return']}")

            if "includes" in conditional.keys():
                if f"{conditional['includes']}\n" in value["output"]:
                    return ( True, f"{value['includes']} in output of {name}")
                else:
                    return ( False, f"{value['includes']} in output of {name}")

        return ( False, f"{value} ({name}) is an unsupported type")
        

    def can_run(self, variables):
        if len(self.conditionals) == 0:
            return ( True, [ "No Conditionals" ] )
        else:
            success = []
            failure = []
            for name, conditional in self.conditionals.items():
                val = self._replace_var(name, variables)
                
                des, message = self._process_conditional(name, val, conditional)
                
                if des:
                    success.append(message)
                else:
                    failure.append(message)

            if len(failure) > 0:
                return ( False, failure )
            else:
                return ( True, success )
        
    
    def run_command(self, variables):
        run, messages = self.can_run(variables)

        if run:
            if SETTINGS["show_command"]:
                self.output_to_term(f"----------------------\nRunning {self.name}")
            
            if SETTINGS["show_reason"]:
                if not SETTINGS["show_command"]:
                    self.output_to_term("----------------------\nReason: {}".format(", ".join(messages)))
                else:
                    self.output_to_term("Reason: {}".format(", ".join(messages)))
            
            for c, pt in enumerate(self.cmd):
                self.cmd[c] = self._replace_var(pt, variables)
            
            data = []
            if SETTINGS["show_output"]:
                if ( not SETTINGS["show_command"] ) and ( not SETTINGS["show_reason"] ):
                    self.output_to_term(f"----------------------\nOutput\n----------------------")
                else:
                    self.output_to_term(f"Output\n----------------------")

            sp = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE)

            with sp as out:
                data.append(out.stdout.read().decode("utf-8").strip())
                if SETTINGS["show_output"]:
                    print(data[-1])
            
            if SETTINGS["show_output"]:
                print()
            
            return ( sp.returncode, "\n".join(data) )

        else:
            if SETTINGS["show_command"]:
                self.output_to_term(f"----------------------\nSkipping {self.name}")
            
            if SETTINGS["show_command"]:
                self.output_to_term("Reason: {}".format(", ".join(messages)))
            
            if SETTINGS["show_output"]:
                self.output_to_term("----------------------\n")

            return ( 999, "" )

    def output_to_term(self, message):
        if SETTINGS["colour"]:
            print(colored(message, "green"))
            Style.RESET_ALL
        else:
            print(message)
    
    @staticmethod
    def new(name, conf):
        conf["name"] = name
        return Command(**conf)

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