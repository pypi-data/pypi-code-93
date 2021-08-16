__version__ = "0.0.9"


def about():
    """Provide a simple description of the package."""
    msg = f"""
# ===== ou_tm129_py, version: {__version__} =====

The `ou_tm129_py` package is an "empty" package that installs Python package requirements 
for the Robotics block of the Open University module "Technologies in practice (TM129)" [http://www.open.ac.uk/courses/modules/tm129].

You can test that key required packages are installed by running the command: ou_tm129_py.test_install()
    """
    print(msg)


def test_install(key_packages=None):
    """Test the install of key packages."""
    import importlib

    if key_packages is None:
        key_packages = [
            "pandas",
            "nbev3devsim",
            "nn_tools",
            "tfjs_mnist",
            "nb_tensorflow_playground_serverproxy",
            "convnet_mnist",
            "nb_tensorspace_playground",
            "nb_handwritten_digit",
            "tflite_runtime"
        ]
    for p in key_packages:
        try:
            importlib.import_module(p.strip())
            print(f"{p} loaded correctly")
        except:
            print(f"{p} appears to be missing")

