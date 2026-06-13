from typing import Optional
from datetime import datetime

from src.dados.movimentacoess_repository import MovimentacoesRepository
from src.dominio.movimentacoes_estoque import Movimentacoes_estoque


class MovimentacoesService:
    """Camada de negócio: aplica validações e regras simples."""

    def __init__(self, repositorio: MovimentacoesRepository) -> None:
        self.repositorio = repositorio

    def cadastrar_movimentacao(
        self,
        id_produto: Optional[int],
        tipo_movimentacao: str,
        quantidade: int,
        data_movimentacao: str,
    ) -> Movimentacoes_estoque:

        tipo_movimentacoes_limpo = tipo_movimentacao.strip()
        data_movimentacao_limpo = data_movimentacao.strip()

        if not tipo_movimentacoes_limpo:
            raise ValueError("O tipo de movimentacao nao pode ficar vazio.")

        if quantidade < 0:
            raise ValueError("A quantidade do produto nao pode ser abaixo de zero.")

        if not data_movimentacao_limpo:
            raise ValueError("A data da movimentação não pode ficar vazia.")

        # CORRIGIDO: converte dd/mm/aaaa → aaaa-mm-dd para o MySQL
        try:
            data_mysql = datetime.strptime(data_movimentacao_limpo, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Data inválida. Use o formato dd/mm/aaaa.")

        movimentacoes = Movimentacoes_estoque(
            id_movimentacao=None,
            id_produto=id_produto,
            tipo_movimentacao=tipo_movimentacoes_limpo,
            quantidade=quantidade,
            data_movimentacao=data_mysql,
        )

        novo_id = self.repositorio.adicionar(movimentacoes)
        movimentacoes.id_movimentacao = novo_id

        return movimentacoes

    def listar_movimentacoes(self) -> list[Movimentacoes_estoque]:

        movimentacoes = self.repositorio.listar_todos()

        if not movimentacoes:
            raise ValueError("Não existem movimentações cadastradas.")

        return movimentacoes

    def buscar_movimentacao_por_tipo(self, tipo: str) -> list[Movimentacoes_estoque]:

        tipo_limpo = tipo.strip()

        if not tipo_limpo:
            raise ValueError("Digite um tipo para buscar.")

        resultados = self.repositorio.buscar_por_tipo(tipo_limpo)

        if not resultados:
            raise ValueError("Nenhuma movimentação encontrada com esse tipo.")

        return resultados

    def atualizar_movimentacao(
        self,
        id_movimentacao: int,
        id_produto: Optional[int],
        tipo_movimentacao: str,
        quantidade: int,
        data_movimentacao: str,
    ) -> bool:

        if not id_movimentacao:
            raise ValueError("Não foi fornecido um ID.")

        if id_movimentacao <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

        tipo_movimentacao_limpo = tipo_movimentacao.strip()
        data_movimentacao_limpo = data_movimentacao.strip()

        if not tipo_movimentacao_limpo:
            raise ValueError("O tipo da movimentacao nao pode ficar vazio.")

        if quantidade < 0:
            raise ValueError("A quantidade do produto nao pode ser negativa.")

        if not data_movimentacao_limpo:
            raise ValueError("A data da movimentação não pode ficar vazia.")

        # CORRIGIDO: converte dd/mm/aaaa → aaaa-mm-dd para o MySQL
        try:
            data_mysql = datetime.strptime(data_movimentacao_limpo, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Data inválida. Use o formato dd/mm/aaaa.")

        movimentacoes = Movimentacoes_estoque(
            id_movimentacao=id_movimentacao,
            id_produto=id_produto,
            tipo_movimentacao=tipo_movimentacao_limpo,
            quantidade=quantidade,
            data_movimentacao=data_mysql,
        )

        return self.repositorio.atualizar(movimentacoes)

    def remover_movimentacao(self, id_movimentacao: int) -> bool:

        if not id_movimentacao:
            raise ValueError("Não foi fornecido um ID.")

        if id_movimentacao <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

        return self.repositorio.remover(id_movimentacao)
