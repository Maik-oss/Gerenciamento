from typing import Optional
from datetime import datetime

from src.dados.produtos_repository import ProdutoRepository
from src.dominio.produto import Produto


class ProdutoService:
    """Camada de negócio: aplica validações e regras simples."""

    def __init__(self, repositorio: ProdutoRepository) -> None:
        self.repositorio = repositorio

    def cadastrar_produto(
        self,
        id_fornecedor: Optional[int],
        nome: str,
        preco: float,
        quantidade: int,
        data_cadastro: str,
        data_validade: str,
    ) -> Produto:

        nome_limpo = nome.strip()

        if not nome_limpo:
            raise ValueError("O nome do produto nao pode ficar vazio.")

        if preco < 0:
            raise ValueError("O preco do produto nao pode ser negativo.")

        if quantidade < 0:
            raise ValueError("A quantidade do produto nao pode ser negativa.")

        # CORRIGIDO: converte dd/mm/aaaa → aaaa-mm-dd para o MySQL
        try:
            data_cadastro_mysql = datetime.strptime(data_cadastro.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Data de cadastro inválida. Use o formato dd/mm/aaaa.")

        try:
            data_validade_mysql = datetime.strptime(data_validade.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Data de validade inválida. Use o formato dd/mm/aaaa.")

        produto = Produto(
            id_produto=None,
            id_fornecedor=id_fornecedor,
            nome=nome_limpo,
            preco=preco,
            quantidade=quantidade,
            data_cadastro=data_cadastro_mysql,
            data_validade=data_validade_mysql,
        )

        novo_id = self.repositorio.adicionar(produto)
        produto.id_produto = novo_id

        return produto

    def listar_produtos(self) -> list[Produto]:

        produtos = self.repositorio.listar_todos()

        if not produtos:
            raise ValueError("Não existem produtos cadastrados.")

        return produtos

    def buscar_produto_por_nome(self, nome: str) -> list[Produto]:

        nome_limpo = nome.strip()

        if not nome_limpo:
            raise ValueError("Digite um nome para buscar.")

        resultados = self.repositorio.buscar_por_nome(nome_limpo)

        if not resultados:
            raise ValueError("Nenhum produto encontrado com esse nome.")

        return resultados

    def atualizar_produto(
        self,
        id_produto: int,
        id_fornecedor: Optional[int],
        nome: str,
        preco: float,
        quantidade: int,
        data_cadastro: str,
        data_validade: str,
    ) -> bool:

        if not id_produto:
            raise ValueError("Não foi fornecido um ID.")

        if id_produto <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

        nome_limpo = nome.strip()

        if not nome_limpo:
            raise ValueError("O nome do produto nao pode ficar vazio.")

        if preco < 0:
            raise ValueError("O preco do produto nao pode ser negativo.")

        if quantidade < 0:
            raise ValueError("A quantidade do produto nao pode ser negativa.")

        # CORRIGIDO: converte dd/mm/aaaa → aaaa-mm-dd para o MySQL
        try:
            data_cadastro_mysql = datetime.strptime(data_cadastro.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Data de cadastro inválida. Use o formato dd/mm/aaaa.")

        try:
            data_validade_mysql = datetime.strptime(data_validade.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Data de validade inválida. Use o formato dd/mm/aaaa.")

        produto = Produto(
            id_produto=id_produto,
            id_fornecedor=id_fornecedor,
            nome=nome_limpo,
            preco=preco,
            quantidade=quantidade,
            data_cadastro=data_cadastro_mysql,
            data_validade=data_validade_mysql,
        )

        return self.repositorio.atualizar(produto)

    def remover_produto(self, id_produto: int) -> bool:

        if not id_produto:
            raise ValueError("Não foi fornecido um ID.")

        if id_produto <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

        return self.repositorio.remover(id_produto)
