import argparse
import logging
from pathlib import Path

import trestle.common.log as log
from trestle.common.err import TrestleError
from trestle.core.commands.command_docs import CommandPlusDocs
from trestle.core.commands.common.return_codes import CmdReturnCodes
from trestle.core.models.actions import CreatePathAction, UpdateAction, WriteFileAction
from trestle.core.models.elements import Element, ElementPath
from trestle.core.models.plans import Plan
from trestle.core.models.file_content_type import FileContentType
from trestle.oscal.common import Revision, Property

from trestle_gsa.core.metadata import Metadata

logger = logging.getLogger(f'trestle.{__name__}')


class TagRevisionCmd(CommandPlusDocs):
    name = 'tag-revision'

    def _init_arguments(self) -> None:
        self.add_argument(
            '-f', '--file', required=True,
            help='Existing OSCAL metadata file to update.', type=str
        )
        self.add_argument(
            '-c', '--changes', required=True,
            help='Summary of changes in this revision of the SSP', type=str
        )
        self.add_argument(
            '-a', '--author', type=str, default=None,
            help='UUID of party who authored this revision. Optional',
        )
        self.add_argument(
            '-vn', '--version', type=str, default=None,
            help='Version to set for this revision. Defaults to main metadata.version'
        )
        self.add_argument(
            '-l', '--last-modified', type=str, default=None,
            help='last-modified to set for this revision. Defaults to main metadata.last-modified'
        )

    def _run(self, args: argparse.Namespace) -> int:
        log.set_log_level_from_args(args)
        logger.debug('Entering trestle tag-revision')

        file_path = Path(args.trestle_root / args.file).resolve()
        # is model decomposed?
        decomposed_dir = file_path.with_name(file_path.stem)
        if decomposed_dir.exists():
            logger.error('tag-revision cannot operate on a split model, merge and try again')
            return CmdReturnCodes.COMMAND_ERROR.value

        update_plan = Plan()
        try:
            metadata = Metadata.oscal_read(file_path)
        except TrestleError as ex:
            logger.error(ex)
            return CmdReturnCodes.INCORRECT_ARGS.value

        parent_element = Element(metadata, 'metadata')

        revision = Revision(
            version=(args.version or metadata.version),
            oscal_version=metadata.oscal_version,
            last_modified=(args.last_modified or metadata.last_modified),
            title=args.changes
        )
        if args.author is not None:
            revision.props = [Property(name='prepared-by', value=args.author)]

        revisions_path = ElementPath('metadata.revisions')
        revisions = [revision]
        if parent_element.get_at(revisions_path) is not None:
            revisions = revisions + parent_element.get_at(revisions_path)
        update_plan.add_action(
            UpdateAction(sub_element=revisions, dest_element=parent_element, sub_element_path=revisions_path)
        )

        # write the updates out
        update_plan.add_action(CreatePathAction(file_path, True))
        update_plan.add_action(
            WriteFileAction(file_path, parent_element, FileContentType.to_content_type(file_path.suffix)))
        update_plan.execute()

        return CmdReturnCodes.SUCCESS.value
