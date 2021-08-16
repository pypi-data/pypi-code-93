def about():
    """Provide a simple description of the package."""
    msg = f"""
# ===== ou_tm351_py, version: {__version__} =====
The `ou_tm351_py` package is an "empty" package that installs Python package requirements 
for the Open University module "Data management and analysis (TM351)" [http://www.open.ac.uk/courses/modules/tm351].
You can test that key required packages are installed by running the command: ou_tm351_py.test_install()
    """
    print(msg)


def test_install(key_packages=None):
    """Test the install of key packages."""
    import importlib

    if key_packages is None:
        key_packages = [
            "pandas",
            "schemadisplay_magic"
        ]
    for p in key_packages:
        try:
            importlib.import_module(p.strip())
            print(f"{p} loaded correctly")
        except:
            print(f"{p} appears to be missing")
