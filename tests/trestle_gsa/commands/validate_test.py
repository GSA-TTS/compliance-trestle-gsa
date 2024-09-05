import pytest
from argparse import Namespace
from pathlib import Path

from trestle.core.commands.common.return_codes import CmdReturnCodes

from trestle_gsa.commands.validate import ValidateCmd

from tests import const


def test_valid_ssp(tmp_trestle_dir: Path) -> None:
    args = Namespace(
        type='system-security-plan',
        name=const.VALID_SSP_NAME,
        all=False,
        trestle_root=tmp_trestle_dir,
        verbose=1,
        quiet=False)
    rc = ValidateCmd()._run(args)
    assert rc == CmdReturnCodes.SUCCESS.value


@pytest.mark.skip(reason="Duplicative test for most of the logic, re-enable after iterations are done")
def test_valid_ssp_file(tmp_trestle_dir: Path) -> None:
    file_path = f'system-security-plans/{const.VALID_SSP_NAME}/system-security-plan.json'
    args = Namespace(
        file=file_path,
        type=None,
        name=None,
        all=False,
        trestle_root=tmp_trestle_dir,
        verbose=1,
        quiet=False)
    rc = ValidateCmd()._run(args)
    assert rc == CmdReturnCodes.SUCCESS.value


@pytest.mark.skip()
def test_invalid_ssp(tmp_trestle_dir: Path) -> None:
    args = Namespace(
        type='system-security-plan',
        name=const.VALID_BASE_SSP_NAME,
        all=False,
        trestle_root=tmp_trestle_dir,
        verbose=1,
        quiet=False)
    rc = ValidateCmd()._run(args)
    assert rc == CmdReturnCodes.OSCAL_VALIDATION_ERROR.value
