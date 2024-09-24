from argparse import Namespace
from pathlib import Path
from datetime import datetime

from trestle.core.commands.common.return_codes import CmdReturnCodes

from trestle_gsa.commands.tag_revision import TagRevisionCmd

from tests.const import VALID_SSP_NAME


def test_tagging_revision(split_ssp_model: str, tmp_trestle_dir: Path) -> None:
    args = Namespace(
        file=f'system-security-plans/{split_ssp_model}/system-security-plan/metadata.json',
        changes='Publish 1.0.0',
        author=None,
        version=None,
        last_modified=None,
        trestle_root=tmp_trestle_dir,
        verbose=2)
    rc = TagRevisionCmd()._run(args)
    assert rc == CmdReturnCodes.SUCCESS.value


def test_all_args(split_ssp_model: str, tmp_trestle_dir: Path) -> None:
    args = Namespace(
        file=f'system-security-plans/{split_ssp_model}/system-security-plan/metadata.json',
        changes='Publish 1.0.0',
        author='7fef97d9-4398-4600-9960-f23d7d61d8cd',
        version='1.0.1',
        last_modified=str(datetime.now().astimezone()),
        trestle_root=tmp_trestle_dir,
        verbose=2)
    rc = TagRevisionCmd()._run(args)
    assert rc == CmdReturnCodes.SUCCESS.value


def test_unsplit_ssp(tmp_trestle_dir: Path) -> None:
    args = Namespace(
        file=f'system-security-plans/{VALID_SSP_NAME}/system-security-plan.json',
        changes='Publish 1.0.0',
        author=None,
        version=None,
        last_modified=None,
        trestle_root=tmp_trestle_dir,
        verbose=2)
    rc = TagRevisionCmd()._run(args)
    assert rc == CmdReturnCodes.INCORRECT_ARGS.value


def test_split_metadata(metadata_split_ssp: str, tmp_trestle_dir: Path) -> None:
    args = Namespace(
        file=f'system-security-plans/{metadata_split_ssp}/system-security-plan/metadata.json',
        changes='Publish 1.0.0',
        author=None,
        version=None,
        last_modified=None,
        trestle_root=tmp_trestle_dir,
        verbose=2)
    rc = TagRevisionCmd()._run(args)
    assert rc == CmdReturnCodes.COMMAND_ERROR.value
