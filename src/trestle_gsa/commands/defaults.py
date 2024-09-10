import argparse
import logging
from pathlib import Path

from pydantic.v1 import ValidationError

import trestle.common.log as log
from trestle.core import generators
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.models.actions import CreatePathAction, UpdateAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.plans import Plan
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.ssp import SystemSecurityPlan

from trestle_gsa.core.metadata import Metadata
from trestle_gsa.core.system_characteristics import SystemCharacteristics, InformationType
from trestle_gsa.core.merge import deep_merge

logger = logging.getLogger(f'trestle.{__name__}')


class DefaultsCmd(CommandPlusDocs):
    name = 'gsa-defaults'

    def _init_arguments(self) -> None:
        self.add_argument(
            '-f', '--file', required=True,
            help='Optional existing OSCAL file that will have elements created within it.', type=str
        )

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        logger.debug('Entering trestle gsa-defaults')

        file_path = Path(args.file).resolve()
        # is model decomposed?
        decomposed_dir = file_path.with_name(file_path.stem)
        if decomposed_dir.exists():
            logger.error('gsa-defaults cannot operate on a split model, merge and try again')
            return CmdReturnCodes.COMMAND_ERROR.value

        update_plan = Plan()
        model = SystemSecurityPlan.oscal_read(file_path)
        parent_element = Element(model, 'system-security-plan')

        # Update metadata
        metadata_defaults = generators.generate_sample_model(Metadata).dict()
        new_metadata = deep_merge(model.metadata.dict(), metadata_defaults)
        element_path = ElementPath('system-security-plan.metadata')
        update_plan.add_action(
            UpdateAction(sub_element=new_metadata, dest_element=parent_element, sub_element_path=element_path))

        # Update information types - this needs to be done separately because the
        # full system-characteristics merge will leave invalid entries in this list
        all_info_types = []
        for info_type in model.system_characteristics.system_information.information_types:
            try:
                InformationType.parse_obj(info_type)
                all_info_types.append(info_type)
            except ValidationError as error:
                logger.debug(error)
                new_type = deep_merge(info_type.dict(), generators.generate_sample_model(InformationType).dict())
                all_info_types.append(new_type)
        element_path = ElementPath('system-security-plan.system-characteristics.system-information.information-types')
        update_plan.add_action(
            UpdateAction(sub_element=all_info_types, dest_element=parent_element, sub_element_path=element_path))
        parent_element = parent_element.set_at(element_path, all_info_types)

        # Update the rest of system-characteristics
        characteristics_defaults = generators.generate_sample_model(SystemCharacteristics).dict()
        new_characteristics = deep_merge(model.system_characteristics.dict(), characteristics_defaults)
        element_path = ElementPath('system-security-plan.system-characteristics')
        update_plan.add_action(
            UpdateAction(sub_element=new_characteristics, dest_element=parent_element, sub_element_path=element_path))

        # write the updates out
        update_plan.add_action(CreatePathAction(file_path, True))
        update_plan.add_action(
            WriteFileAction(file_path, parent_element, FileContentType.to_content_type(file_path.suffix)))
        update_plan.execute()

        return CmdReturnCodes.SUCCESS.value
