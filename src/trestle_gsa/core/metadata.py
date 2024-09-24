from typing import List

from trestle.oscal.common import Metadata as MetadataBase
from trestle.oscal.common import Role as RoleBase
from trestle.oscal.common import Party as PartyBase
from trestle.oscal.common import ResponsibleParty

from pydantic.v1 import Field, validator


class Role(RoleBase):
    title: str = Field("REPLACE_ME", min_length=1)


class Party(PartyBase):
    name: str = Field("REPLACE_ME")


MINIMUM_ROLE_IDS = [
    'prepared-by',
    'system-owner',
    'information-system-security-officer',
    'information-system-security-manager',
    'authorizing-official',
    'system-poc-technical',
]


def _create_default_roles() -> List[Role]:
    return list(Role(id=id) for id in MINIMUM_ROLE_IDS)


def _create_default_responsible_parties() -> List[ResponsibleParty]:
    return [ResponsibleParty(role_id='prepared-by', party_uuids=[])]


class Metadata(MetadataBase):
    roles: List[Role] = Field(default_factory=_create_default_roles)
    parties: List[Party]
    responsible_parties: List[ResponsibleParty] = Field(
        default_factory=_create_default_responsible_parties, alias='responsible-parties')

    @validator('roles')
    def has_minimum_role_ids(cls, roles: List[Role]) -> List[Role]:
        role_ids = set(map(lambda r: r.id, roles))
        minimum_role_ids = set(MINIMUM_ROLE_IDS)
        if not minimum_role_ids.issubset(role_ids):
            raise ValueError(
                f'metadata.roles is missing the following role ids: {minimum_role_ids.difference(role_ids)}')
        return roles

    @validator('responsible_parties')
    def has_at_least_prepared_by(cls, responsible_parties: List[ResponsibleParty]) -> List[ResponsibleParty]:
        has_prepared_by = False
        for rp in responsible_parties:
            if rp.role_id == 'prepared-by':
                has_prepared_by = True
                break
        assert has_prepared_by, 'metadata.responsible-parties must include an entry for the prepared-by role'
        return responsible_parties
