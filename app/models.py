from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class EndpointStatus(Enum):
    HEALTHY = "healthy"
    DEAD = "dead"
    DEPRECATED = "deprecated"
    UNDOCUMENTED = "undocumented"
    BREAKING = "breaking"

@dataclass
class Endpoint:
    method: str                          # GET, POST, PUT, DELETE
    path: str                            # /api/users/{id}
    source_file: str                     # where in the codebase
    line_number: int                     # which line
    has_docstring: bool = False          # does it have comments/docs?
    has_openapi_annotation: bool = False # does it have @ApiOperation etc?
    has_postman_entry: bool = False      # is it in a Postman collection?
    is_deprecated: bool = False          # marked @Deprecated or similar?
    call_count: int = 0                  # how many times seen in logs
    status: EndpointStatus = EndpointStatus.HEALTHY
    generated_docs: Optional[str] = None # LLM-generated docs go here