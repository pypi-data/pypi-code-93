#!/usr/bin/env python3
import subprocess
import os
from os import path
from pathlib import Path


class Compile():
    """Compile class for compiling code and returning output

        Attributes:
        code  (string): code to be compiled
        lang (string): p
        programming language used
        input (string): user input
        id (integer): user id
        output (string): output of code
        compile status (string): compilation status code
    """

    def __init__(self, code="", lang="", input="", id=0):
        """
            This function intialises the class variables with values passed by the user.
        """
        self.code = code
        self.lang = lang
        self.input = input
        self.id = str(id)
        self.output = ""
        self.status = ""
        self.create_file()
        if(self.lang == "PYTHON"):
            self.compile_python()
        elif(self.lang == "C"):
            self.compile_c()
        elif(self.lang == "CPP"):
            self.compile_cpp()
        self.delete_file()

    def create_file(self):
        """Function to create the code and input files.
        Args:
            None
        Returns:
            None
        """
        dir = os.path.join(str(Path.home()), ".data")
        if(path.isdir(dir)):
            pass
        else:
            os.mkdir(dir)
        os.chdir(dir)

        if(self.lang == "PYTHON"):
            file = open(self.id+".py", "w")
            file.write(self.code)
            file.close()
        elif(self.lang == "C"):
            file = open(self.id+".c", "w")
            file.write(self.code)
            file.close()
        elif(self.lang == 'CPP'):
            file = open(self.id+".cpp", "w")
            file.write(self.code)
            file.close()
        file = open(self.id+"-input.txt", "w")
        file.write(self.input)
        file.close()

    def delete_file(self):
        """Function to delete the code and input files.
        Args:
            None
        Returns:
            None
        """
        os.remove(self.id+"-input.txt")
        if(self.lang == "PYTHON"):
            os.remove(self.id+".py")
        elif(self.lang == "C"):
            os.remove(self.id+".c")
            if(self.status == 1):
                os.remove(self.id+"_c")
        elif(self.lang == 'CPP'):
            os.remove(self.id+".cpp")
            if(self.status == 1):
                os.remove(self.id+"_cpp")

    def compile_python(self):
        """Function to compile python code and return output.
        Args:
            None
        Returns:
            None
        """
        if(self.input == ""):
            stdout = subprocess.run(
                ["python", self.id+".py"], stdout=subprocess.PIPE).stdout.decode('utf-8')
            self.output = stdout
            if(len(stdout) == 0):
                self.output = subprocess.run(
                    ["python", self.id+".py"], stderr=subprocess.PIPE).stderr.decode('utf-8')
                self.status = 0  # error
            else:
                self.status = 1  # success
        else:
            pass

    def compile_c(self):
        """Function to compile C code and return output.
        Args:
            None
        Returns:
            None
        """
        if(self.input == ""):
            stderr = subprocess.run(
                ["gcc", self.id+".c", "-o", self.id+"_c"], stderr=subprocess.PIPE).stderr.decode('utf-8')
            if(len(stderr) == 0):
                self.status = 1
                stdout = subprocess.run(
                    ["./"+self.id+"_c"], stdout=subprocess.PIPE).stdout.decode('utf-8')
                self.output = stdout
            else:
                self.status = 0
                self.output = stderr
        else:
            pass

    def compile_cpp(self):
        """Function to compile C++ code and return output.
        Args:
            None
        Returns:
            None
        """
        if(self.input == ""):
            stderr = subprocess.run(
                ["g++", self.id+".cpp", "-o", self.id+"_cpp"], stderr=subprocess.PIPE).stderr.decode('utf-8')
            if(len(stderr) == 0):
                self.status = 1
                stdout = subprocess.run(
                    ["./"+self.id+"_cpp"], stdout=subprocess.PIPE).stdout.decode('utf-8')
                self.output = stdout
            else:
                self.status = 0
                self.output = stderr
        else:
            pass

    def get_output(self):
        """Function to return output of the code
        Args:
            None
        Returns:
            Output of the compiled code
        """
        return self.output

    def get_status(self):
        """Function to return compilation status code
        Args:
            None
        Returns:
            Compilation status code
        """
        return self.status
