from argparse import Namespace
from pathlib import Path

from trestle.core.commands.common.return_codes import CmdReturnCodes

from trestle_gsa.commands.defaults import DefaultsCmd
from trestle_gsa.commands.validate import ValidateCmd

from tests import const


def test_adding_defaults(tmp_trestle_dir: Path) -> None:
    file_path = f'system-security-plans/{const.VALID_BASE_SSP_NAME}/system-security-plan.json'
    args = Namespace(
        file=file_path,
        trestle_root=tmp_trestle_dir,
        verbose=2)
    rc = DefaultsCmd()._run(args)
    assert rc == CmdReturnCodes.SUCCESS.value

    valdidate_args = Namespace(
        file=file_path,
        name=None,
        type=None,
        all=False,
        trestle_root=tmp_trestle_dir,
        verbose=0,
        quiet=True)
    assert ValidateCmd()._run(valdidate_args) == CmdReturnCodes.SUCCESS.value, 'Resulting file should pass validation'
