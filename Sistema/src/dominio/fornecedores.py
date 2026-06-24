from dataclasses import dataclass
from typing import Optional


@dataclass
class Fornecedores:
    """Representa a entidade de dominio Fornecedores."""

    id_fornecedor: Optional[int]
    nome: str
    tipo: str
    cnpj: str
    telefone_fornecedor: str
    cpf: str
    email: str
    cidade: str
    estado: str
    data_cadastro: str