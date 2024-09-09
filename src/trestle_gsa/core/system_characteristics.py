from typing import List

from trestle.oscal.ssp import AuthorizationBoundary as AuthorizationBoundaryBase
from trestle.oscal.ssp import DataFlow as DataFlowBase
from trestle.oscal.ssp import Diagram as DiagramBase
from trestle.oscal.ssp import Impact as ImpactBase
from trestle.oscal.ssp import InformationType as InformationTypeBase
from trestle.oscal.ssp import SystemCharacteristics as SystemCharacteristicsBase
from trestle.oscal.ssp import SystemInformation as SystemInformationBase
from trestle.oscal.ssp import Selected, SecurityImpactLevel
from trestle.oscal.common import ResponsibleParty, Property, Link

from pydantic.v1 import Field, validator


def _create_default_diagram_link() -> List[Link]:
    return [Link(rel="diagram", href="REPLACE_ME")]


class Diagram(DiagramBase):
    caption: str = Field("REPLACE_ME", min_length=1)
    links: List[Link] = Field(default_factory=_create_default_diagram_link)

    @validator('links')
    def has_diagram_link(cls, links: List[Link]) -> List[Link]:
        rels = list(x.rel for x in links if x.rel == "diagram")
        assert len(rels) == 1, 'Diagram must have exactly one link with rel=diagram'
        return links


class DataFlow(DataFlowBase):
    diagrams: List[Diagram]


class AuthorizationBoundary(AuthorizationBoundaryBase):
    diagrams: List[Diagram]


class Impact(ImpactBase):
    selected: Selected


class InformationType(InformationTypeBase):
    confidentiality_impact: Impact
    integrity_impact: Impact
    availability_impact: Impact


class SystemInformation(SystemInformationBase):
    information_types: List[InformationType]


def _create_default_props() -> List[Property]:
    return [
        Property(name="identity-assurance-level", value="REPLACE_ME"),
        Property(name="authenticator-assurance-level", value="REPLACE_ME"),
        Property(name="federation-assurance-level", value="REPLACE_ME")
    ]


def _create_default_responsible_parties() -> List[ResponsibleParty]:
    return [
        ResponsibleParty(role_id='system-owner', party_uuids=[]),
        ResponsibleParty(role_id='authorizing-official', party_uuids=[])
    ]


class SystemCharacteristics(SystemCharacteristicsBase):
    system_name_short: str = Field("REPLACE_ME")
    system_information: SystemInformation
    responsible_parties: List[ResponsibleParty] = Field(default_factory=_create_default_responsible_parties)
    security_sensitivity_level: str = Field("REPLACE_ME")
    security_impact_level: SecurityImpactLevel
    props: List[Property] = Field(default_factory=_create_default_props)
    authorization_boundary: AuthorizationBoundary
    data_flow: DataFlow

    @validator('responsible_parties')
    def has_minimum_responsible_parties(cls, responsible_parties: List[ResponsibleParty]) -> List[ResponsibleParty]:
        minimum_role_ids = set((
            'system-owner',
            'authorizing-official',
        ))
        role_ids = set(map(lambda rp: rp.role_id, responsible_parties))
        if not minimum_role_ids.issubset(role_ids):
            raise ValueError(
                'responsible_parties must list at least system-owner and authorizing-official roles'
            )
        return responsible_parties

    @validator('props')
    def has_xal_properties(cls, props: List[Property]) -> List[Property]:
        minimum_prop_names = set((
            'identity-assurance-level',
            'authenticator-assurance-level',
            'federation-assurance-level',
        ))
        prop_names = set(map(lambda p: p.name, props))
        if not minimum_prop_names.issubset(prop_names):
            raise ValueError(
                f'props is missing the following names: {minimum_prop_names.difference(prop_names)}'
            )
        return props
