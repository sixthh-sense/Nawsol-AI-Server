from typing import Dict, Literal

from pydantic import BaseModel


class InsertDocumentRequest(BaseModel):
    document_type: Literal["income", "expense"]
    data: Dict[str, str]