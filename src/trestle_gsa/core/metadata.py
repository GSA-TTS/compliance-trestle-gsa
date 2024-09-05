from typing import List

from trestle.oscal.common import Metadata as MetadataBase
from trestle.oscal.common import Role as RoleBase

from pydantic.v1 import Field, validator


class Role(RoleBase):
    title: str = Field(..., min_length=1)


class Metadata(MetadataBase):
    roles: List[Role] = Field(..., min_items=6)

    @validator('roles')
    def has_minimum_role_ids(cls, roles: List[Role]) -> List[Role]:
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
            raise ValueError(
                f'metadata.roles is missing the following role ids: {minimum_role_ids.difference(role_ids)}')
        return roles
