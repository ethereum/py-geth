def test_import_and_version():
    import geth

    assert isinstance(geth.__version__, str)
