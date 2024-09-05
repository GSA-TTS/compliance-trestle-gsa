import logging

from pydantic.v1 import ValidationError

from trestle_gsa.core.metadata import Metadata
from trestle.oscal.ssp import SystemSecurityPlan, SystemCharacteristics, SystemImplementation
from trestle.common.list_utils import as_list

logger = logging.getLogger(__name__)


class GsaValidator:
    def __init__(self, ssp: SystemSecurityPlan) -> None:
        self._ssp = ssp
        self._system_characteristics = ssp.system_characteristics

    @property
    def system_characteristics(self) -> SystemCharacteristics:
        return self._ssp.system_characteristics

    @property
    def system_implementation(self) -> SystemImplementation:
        return self._ssp.system_implementation

    def validate(self) -> bool:
        valid = True
        try:
            Metadata.parse_obj(self._ssp.metadata)
        except ValidationError as error:
            logger.error(error)
            valid = False

        # validate system-characteristics fields
        if not self.system_characteristics.system_name_short:
            logger.error('Missing system-name-short')
            valid = False
        valid = self._validate_info_types() and valid

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
