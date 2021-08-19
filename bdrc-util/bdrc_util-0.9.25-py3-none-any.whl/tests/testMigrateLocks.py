from migrate_works.MigrateLocks import lock_work, unlock_work, is_work_locked



test_name: str = "UNITTESTONLY"

def test_locking():
    lock_work(test_name)
    assert is_work_locked(test_name)

def test_unlocking():
    test_locking()
    unlock_work(test_name)
    assert not is_work_locked(test_name)

def test_is_work_locked():
    """
    Test a work that should not be in the database, even from testing.
    Superman fans will get this reference, for the rest of you there's always
    wikipedia
    """
    assert not is_work_locked("KLTPZYXM")
