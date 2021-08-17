# __path__ manipulation added by rules_python_external to support namespace pkgs.
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
