# -*- mode:python; coding:utf-8 -*-
#
# Copyright (c) 2021 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Common fixtures."""

import os
import pathlib
import sys
from typing import Iterator

import pytest
from pytest import MonkeyPatch

from trestle.cli import Trestle
from trestle.common.err import TrestleError

from tests import const


@pytest.fixture(scope='function')
def tmp_trestle_dir(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch) -> Iterator[pathlib.Path]:
    """Create and return a new trestle project directory using std tmp_path fixture.

    Note that this fixture relies on the 'trestle init' command and therefore may
    misbehave if there are errors in trestle init, perhaps in spite of the try block.
    """
    pytest_cwd = pathlib.Path.cwd()
    os.chdir(tmp_path)
    testargs = ['trestle', 'init']
    monkeypatch.setattr(sys, 'argv', testargs)
    try:
        Trestle().run()
        _import_ssp(pytest_cwd, const.VALID_SSP_NAME, monkeypatch)
        _import_ssp(pytest_cwd, const.VALID_BASE_SSP_NAME, monkeypatch)
    except BaseException as e:
        raise TrestleError(f'Initialization failed for temporary trestle directory: {e}.')
    else:
        yield tmp_path
    finally:
        os.chdir(pytest_cwd)


def _import_ssp(cwd: pathlib.Path, ssp_name: str, monkeypatch: MonkeyPatch) -> None:
    fixture_path = cwd / 'tests' / 'resources'
    testargs = ['trestle', 'import', '-f', str(fixture_path / f'{ssp_name}.json'), '-o', ssp_name]
    monkeypatch.setattr(sys, 'argv', testargs)
    Trestle().run()
