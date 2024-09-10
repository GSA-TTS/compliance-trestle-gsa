import argparse
import logging

import trestle.common.log as log
import trestle.core.validator_factory as vfact
from trestle.common.const import VAL_MODE_ALL, MODEL_TYPE_SSP
from trestle.common.err import TrestleError
from trestle.common.model_utils import ModelUtils
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes

from trestle_gsa.core.gsa import GsaValidator

logger = logging.getLogger(f'trestle.{__name__}')


class ValidateCmd(CommandPlusDocs):
    name = 'gsa-validate'

    def _init_arguments(self) -> None:
        logger.debug('Init arguments')
        vfact.init_arguments(self)

    def _validate_arguments(self, args: argparse.ArgumentParser) -> int:
        if args.all:
            logger.error(f'--all is not supported for {self.name}')
            return CmdReturnCodes.INCORRECT_ARGS.value
        if args.type:
            if args.type != MODEL_TYPE_SSP:
                logger.error(f'{self.name} only supports SSP models')
                return CmdReturnCodes.INCORRECT_ARGS.value
            if not args.name:
                logger.error('You must supply --name when using --type')
                return CmdReturnCodes.INCORRECT_ARGS.value
        return super()._validate_arguments(args)

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        logger.debug('Entering trestle gsa-validate')

        valid = False

        mode_args = argparse.Namespace(mode=VAL_MODE_ALL)
        validator = vfact.validator_factory.get(mode_args)
        try:
            status = validator.validate(args)
            if status != CmdReturnCodes.SUCCESS.value:
                logger.error(f'SSP {self._get_input_debug(args)} does not pass base validation')
                return status
        except TrestleError as ex:
            logger.error(f'Base validation error {ex.msg}')
            return CmdReturnCodes.OSCAL_VALIDATION_ERROR.value

        try:
            tr = args.trestle_root
            if self._using_file_arg(args):
                model_file = tr / args.file
                _, model_alias, model = ModelUtils.load_distributed(model_file, tr)
                if model_alias != MODEL_TYPE_SSP:
                    logger.warning(f'Validation for {model_alias} is not supported.')
                    return CmdReturnCodes.INCORRECT_ARGS.value
            else:
                model, _ = ModelUtils.load_model_for_type(tr, args.type, args.name)
            validator = GsaValidator(model)
            valid = validator.validate()
        except Exception as error:
            logger.error(f'Unexpected error: {error}')
            return CmdReturnCodes.UNKNOWN_ERROR.value

        return CmdReturnCodes.SUCCESS.value if valid else CmdReturnCodes.OSCAL_VALIDATION_ERROR.value

    def _using_file_arg(self, args) -> bool:
        return hasattr(args, 'file') and args.file

    def _get_input_debug(self, args) -> str:
        if self._using_file_arg(args):
            return args.file
        else:
            return args.name
