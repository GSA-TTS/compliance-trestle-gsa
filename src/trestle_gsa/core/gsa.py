import logging

from trestle.oscal.common import Metadata
from trestle.oscal.ssp import SystemSecurityPlan, SystemCharacteristics, SystemImplementation
from trestle.common.list_utils import as_list

logger = logging.getLogger(__name__)


class GsaValidator:
    def __init__(self, ssp: SystemSecurityPlan) -> None:
        self._ssp = ssp
        self._system_characteristics = ssp.system_characteristics

    @property
    def metadata(self) -> Metadata:
        return self._ssp.metadata

    @property
    def system_characteristics(self) -> SystemCharacteristics:
        return self._ssp.system_characteristics

    @property
    def system_implementation(self) -> SystemImplementation:
        return self._ssp.system_implementation

    def validate(self) -> bool:
        valid = True
        # validate metadata fields
        valid = valid and self._validate_minimum_roles()

        # validate system-characteristics fields
        if not self.system_characteristics.system_name_short:
            logger.error('Missing system-name-short')
            valid = False
        valid = valid and self._validate_info_types()

        return valid

    def _validate_minimum_roles(self) -> bool:
        valid = True

        roles = as_list(self.metadata.roles)
        if roles:
            role_ids = set(map(lambda r: r.id, roles))
            minimum_role_ids = set([
                'prepared-by',
                'system-owner',
                'information-system-security-officer',
                'information-system-security-manager',
                'authorizing-official',
                'system-poc-technical',
            ])
            if not minimum_role_ids.issubset(role_ids):
                logger.error(
                    f'metadata.roles is missing the following role ids: {minimum_role_ids.difference(role_ids)}'
                )
                valid = False
        else:
            logger.error('Missing metadata.roles entries')
            valid = False

        for role in roles:
            if not role.title:
                logger.error(f'role.title is blank for role.id: {role.id}')
                valid = False

        return valid

    def _validate_info_types(self) -> bool:
        valid = True
        info_types = as_list(self.system_characteristics.system_information.information_types)
        if not info_types:
            logger.error('Missing system_information.information_types entries')
            valid = False
        for info_type in info_types:
            if not info_type.confidentiality_impact or not info_type.confidentiality_impact.selected:
                logger.error(f'Missing confidentiality_impact.selected for info_type {info_type.title}')
                valid = False
            if not info_type.integrity_impact or not info_type.integrity_impact.selected:
                logger.error(f'Missing integrity_impact.selected for info_type {info_type.title}')
                valid = False
            if not info_type.availability_impact or not info_type.availability_impact.selected:
                logger.error(f'Missing availability_impact.selected for info_type {info_type.title}')
                valid = False
        return valid
