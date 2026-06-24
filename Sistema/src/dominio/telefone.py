from dataclasses import dataclass
from typing import Optional


@dataclass
class TelefoneFornecedor:

    id_telefone: Optional[int]
    id_fornecedor: Optional[int]

    numero: str
