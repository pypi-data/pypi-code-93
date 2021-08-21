def test_import():
    import senasopt

    assert isinstance(senasopt.__version__, str)
