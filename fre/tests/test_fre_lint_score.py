"""
- Ensure pylint command to set --fail-under score
  works as expected
- Ensure pylint score of fre/ is equal to or above
  70%
"""
from pylint import lint

def test_fre_score_threshold():
    """
    Retrive linter score for fre/ directory and check against
    min threshold set
    """
    # currently set: --fail-under 0.70 in pipeline
    min_score = 7.00

    # Mimic pyling command in pipeline
    # exit=False allows command to exit without failing
    lint_cmd = lint.Run(['fre/',
                         '--max-line-length=120',
                         '--max-args=6',
                         '-ry',
                         '--ignored-modules=netCDF4,cmor'],
                         exit=False)

    # global_note holds final score
    fre_score = lint_cmd.linter.stats.global_note

    assert fre_score >= min_score

    # If files are edited between runs, we need to clear pylint's cache
    lint.pylinter.MANAGER.clear_cache()
