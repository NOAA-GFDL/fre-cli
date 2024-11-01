''' test "fre make" calls '''

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

## assumes you're running pytest from repo root dir
def test_fre_make_run_fremake_null_model():
    ''' run fre make with run-fremake subcommand and build the null model experiment with gnu'''
    result = runner.invoke(fre.fre, args=["make", "run-fremake", "-y", "fre/make/tests/null_example/null_model.yaml", "-p", "ci.gnu", "-t", "debug"])
    assert result.exit_code == 0
