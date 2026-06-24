import re
from typing import Optional

from src.dados.telefones_fornecedor_repository import Telefone_fornecedor_Repository
from src.dominio.telefone import TelefoneFornecedor



def _somente_numeros_e_pontuacao(valor: str) -> bool:
    return bool(re.fullmatch(r'[\d.\-/()\s]+', valor))

class TelefoneService:
    """Camada de negócio: aplica validações e regras simples."""

    def __init__(self, repositorio: Telefone_fornecedor_Repository) -> None:
        self.repositorio = repositorio

    def cadastrar_telefone(self, id_fornecedor: Optional[int], numero: str) -> TelefoneFornecedor:

        numero_limpo = numero.strip()

        if not numero_limpo:
            raise ValueError("O numero do fornecedor nao pode ficar vazio.")

        if not _somente_numeros_e_pontuacao(numero_limpo):
            raise ValueError("O número deve conter apenas dígitos, pontos, barras ou traços.")

        telefone = TelefoneFornecedor(
            id_telefone=None,
            id_fornecedor=id_fornecedor,
            numero=numero_limpo,
        )

        novo_id = self.repositorio.adicionar(telefone)
        telefone.id_telefone = novo_id

        return telefone

    def listar_telefones(self) -> list[TelefoneFornecedor]:

        telefones = self.repositorio.listar_todos()

        if not telefones:
            raise ValueError("Não existem telefones cadastrados.")

        return telefones

    def buscar_telefone_por_nome_fornecedor(self, nome: str) -> list[TelefoneFornecedor]:

        nome_limpo = nome.strip()

        if not nome_limpo:
            raise ValueError("Digite um nome para buscar.")

        resultados = self.repositorio.buscar_por_nome_fornecedor(nome_limpo)

        if not resultados:
            raise ValueError("Nenhum telefone encontrado para esse fornecedor.")

        return resultados

    def atualizar_telefone(self, id_telefone: int, id_fornecedor: Optional[int], numero: str) -> bool:

        if not id_telefone:
            raise ValueError("Não foi fornecido um ID.")

        if id_telefone <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

        numero_limpo = numero.strip()

        if not numero_limpo:
            raise ValueError("O numero do fornecedor nao pode ficar vazio.")

        if not _somente_numeros_e_pontuacao(numero_limpo):
            raise ValueError("O número deve conter apenas dígitos, pontos, barras ou traços.")

        telefone = TelefoneFornecedor(
            id_telefone=id_telefone,
            id_fornecedor=id_fornecedor,
            numero=numero_limpo,
        )

        return self.repositorio.atualizar(telefone)

    def remover_telefone(self, id_telefone: int) -> bool:

        if not id_telefone:
            raise ValueError("Não foi fornecido um ID.")

        if id_telefone <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

        return self.repositorio.remover(id_telefone)
