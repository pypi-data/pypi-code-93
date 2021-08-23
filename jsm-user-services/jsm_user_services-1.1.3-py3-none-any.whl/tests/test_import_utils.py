from types import ModuleType

from jsm_user_services.support.import_utils import import_module_otherwise_none


def test_should_return_none_when_import_error_is_raised():
    assert import_module_otherwise_none("unknown_module") is None


def test_should_return_imported_module_when_it_is_possible():
    imported_module = import_module_otherwise_none("jsm_user_services")

    assert isinstance(imported_module, ModuleType)
