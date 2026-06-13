from dataclasses import dataclass
from typing import Optional


@dataclass
class Produto:

    id_produto: Optional[int]
    id_fornecedor: Optional[int]

    nome: str
    preco: float
    quantidade: int

    data_cadastro: str
    data_validade: str
