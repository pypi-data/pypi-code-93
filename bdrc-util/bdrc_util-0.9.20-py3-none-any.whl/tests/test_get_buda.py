from util_lib.GetFromBUDA import get_disk_volumes_in_work
def test_fetch():
    v_n = get_disk_volumes_in_work('W00EGS1016733')
    assert len(v_n) == 50
    for v in v_n:
        assert(str(v['vol_label']).startswith("I8LS"))