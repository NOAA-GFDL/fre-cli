''' fre run outputstager '''

import logging

import click

fre_logger = logging.getLogger(__name__)


@click.command()
@click.option('--exit-status',            is_flag=True, default=False, required=False,
              help='Set to indicate a non-zero exit status from the model run.')
@click.option('--combine',                is_flag=True, default=False, required=False,
              help='Enable the combine step for history output files.')
@click.option('--check',                  is_flag=True, default=False, required=False,
              help='Enable the check step to verify output files.')
@click.option('--save-on',                is_flag=True, default=False, required=False,
              help='Enable saving of history output files.')
@click.option('--fill-grid-on',           is_flag=True, default=False, required=False,
              help='Enable the fill-grid step.')
@click.option('--combine-ok',             is_flag=True, default=False, required=False,
              help='Indicate that the combine step completed successfully.')
@click.option('--check-ok',               is_flag=True, default=False, required=False,
              help='Indicate that the check step completed successfully.')
@click.option('--save-ok',                is_flag=True, default=False, required=False,
              help='Indicate that the save step completed successfully.')
@click.option('--fill-grid-ok',           is_flag=True, default=False, required=False,
              help='Indicate that the fill-grid step completed successfully.')
@click.option('--archive-on',             is_flag=True, default=False, required=False,
              help='Enable archiving of history output files.')
@click.option('--ptmp-on',                is_flag=True, default=False, required=False,
              help='Enable staging of output files to the ptmp directory.')
@click.option('--check-sum-on',           is_flag=True, default=False, required=False,
              help='Enable checksum verification of output files.')
@click.option('--compress-on',            is_flag=True, default=False, required=False,
              help='Enable compression of output files.')
@click.option('--verbose',                is_flag=True, default=False, required=False,
              help='Enable verbose output.')
@click.argument('exp_name')
@click.argument('_type')
@click.argument('work_dir')
@click.argument('ptmp_dir')
@click.argument('arch_dir')
@click.argument('mppnccombine_opt_string')
@click.argument('ardiff_tmpdir')
def stageHistory(exit_status, combine, check, save_on, fill_grid_on,  # pylint: disable=invalid-name
                 combine_ok, check_ok, save_ok, fill_grid_ok, archive_on,
                 ptmp_on, check_sum_on, compress_on, verbose,
                 exp_name, _type, work_dir, ptmp_dir, arch_dir,
                 mppnccombine_opt_string, ardiff_tmpdir):
    """
    Stage history output files for post-processing.

    EXP_NAME is the experiment name.

    _TYPE is the type/category of history output files to stage.

    WORK_DIR is the working directory containing model output.

    PTMP_DIR is the ptmp scratch directory path.

    ARCH_DIR is the archive directory path.

    MPPNCCOMBINE_OPT_STRING is the options string passed to mppnccombine.

    ARDIFF_TMPDIR is the temporary directory used by ardiff.

    :param exit_status: Set to indicate a non-zero exit status from the model run, default False
    :type exit_status: bool
    :param combine: Enable the combine step for history output files, default False
    :type combine: bool
    :param check: Enable the check step to verify output files, default False
    :type check: bool
    :param save_on: Enable saving of history output files, default False
    :type save_on: bool
    :param fill_grid_on: Enable the fill-grid step, default False
    :type fill_grid_on: bool
    :param combine_ok: Indicate that the combine step completed successfully, default False
    :type combine_ok: bool
    :param check_ok: Indicate that the check step completed successfully, default False
    :type check_ok: bool
    :param save_ok: Indicate that the save step completed successfully, default False
    :type save_ok: bool
    :param fill_grid_ok: Indicate that the fill-grid step completed successfully, default False
    :type fill_grid_ok: bool
    :param archive_on: Enable archiving of history output files, default False
    :type archive_on: bool
    :param ptmp_on: Enable staging of output files to the ptmp directory, default False
    :type ptmp_on: bool
    :param check_sum_on: Enable checksum verification of output files, default False
    :type check_sum_on: bool
    :param compress_on: Enable compression of output files, default False
    :type compress_on: bool
    :param verbose: Enable verbose output, default False
    :type verbose: bool
    :param exp_name: Experiment name, default None
    :type exp_name: str
    :param _type: Type/category of history output files to stage, default None
    :type _type: str
    :param work_dir: Working directory containing model output, default None
    :type work_dir: str
    :param ptmp_dir: Ptmp scratch directory path, default None
    :type ptmp_dir: str
    :param arch_dir: Archive directory path, default None
    :type arch_dir: str
    :param mppnccombine_opt_string: Options string passed to mppnccombine, default None
    :type mppnccombine_opt_string: str
    :param ardiff_tmpdir: Temporary directory used by ardiff, default None
    :type ardiff_tmpdir: str
    """
    raise NotImplementedError('fre run stageHistory has not been implemented yet!')
