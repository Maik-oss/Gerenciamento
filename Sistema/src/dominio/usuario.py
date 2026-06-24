from dataclasses import dataclass
from typing import Optional


@dataclass
class Usuario:

    id_usuario: Optional[int]
    usuario: str
    senha: str
