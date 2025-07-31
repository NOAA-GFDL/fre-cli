'''This test ensures that the catalog builder module can be imported'''
def test_fre_catalog_import():
    from fre import catalog
    assert catalog is not None
