import logging

from pydantic.v1 import ValidationError

from trestle_gsa.core.metadata import Metadata
from trestle_gsa.core.system_characteristics import SystemCharacteristics
from trestle.oscal.ssp import SystemSecurityPlan

logger = logging.getLogger(f'trestle.{__name__}')


class GsaValidator:
    def __init__(self, ssp: SystemSecurityPlan) -> None:
        self._ssp = ssp

    def validate(self) -> bool:
        valid = True

        # validate metadata fields
        try:
            Metadata.parse_obj(self._ssp.metadata)
        except ValidationError as error:
            logger.error(error)
            valid = False

        # validate system-characteristics fields
        try:
            SystemCharacteristics.parse_obj(self._ssp.system_characteristics)
        except ValidationError as error:
            logger.error(error)
            valid = False

        return valid
