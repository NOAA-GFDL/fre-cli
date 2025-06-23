from fre.pp import make_workflow_name

def test_make_workflow_name():
    assert "FOO__BAR__BAZ" == make_workflow_name( experiment = "FOO",
                                                  platform = "BAR",
                                                  target = "BAZ" )
