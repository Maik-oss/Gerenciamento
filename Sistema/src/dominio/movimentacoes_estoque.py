from dataclasses import dataclass
from typing import Optional


@dataclass
class Movimentacoes_estoque:

    id_movimentacao: Optional[int]
    id_produto: Optional[int]

    tipo_movimentacao: str
    quantidade: int

    data_movimentacao: str
