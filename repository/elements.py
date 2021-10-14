from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class Author:
    name: str
    aff_ids: list


@dataclass
class Affiliation:
    organization: str
    aff_id: Optional[Union[int, str]]


@dataclass
class AuthorAffiliations:
    name: str
    affiliations: list
