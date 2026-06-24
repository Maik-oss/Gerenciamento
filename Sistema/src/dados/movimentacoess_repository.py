import mysql.connector

from src.dominio.movimentacoes_estoque import Movimentacoes_estoque


class MovimentacoesRepository:

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def adicionar(self, movimentacoes_estoque: Movimentacoes_estoque) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            """
            INSERT INTO movimentacoes_estoque
            (id_produto, tipo_movimentacao, quantidade, data_movimentacao)
            VALUES (%s, %s, %s, %s)
            """,
            (
                movimentacoes_estoque.id_produto,
                movimentacoes_estoque.tipo_movimentacao,
                movimentacoes_estoque.quantidade,
                movimentacoes_estoque.data_movimentacao,
            ),
        )
        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def listar_todos(self) -> list[Movimentacoes_estoque]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_movimentacao, id_produto, tipo_movimentacao, quantidade, data_movimentacao
            FROM movimentacoes_estoque
            ORDER BY id_movimentacao
            """
        )
        linhas = cursor.fetchall()
        cursor.close()

        return [
            Movimentacoes_estoque(
                id_movimentacao=linha["id_movimentacao"],
                id_produto=linha["id_produto"],
                tipo_movimentacao=linha["tipo_movimentacao"],
                quantidade=linha["quantidade"],
                data_movimentacao=str(linha["data_movimentacao"]),
            )
            for linha in linhas
        ]

    def buscar_por_tipo(self, tipo: str) -> list[Movimentacoes_estoque]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_movimentacao, id_produto, tipo_movimentacao, quantidade, data_movimentacao
            FROM movimentacoes_estoque
            WHERE tipo_movimentacao LIKE %s
            ORDER BY id_movimentacao
            """,
            (f"%{tipo}%",),
        )
        linhas = cursor.fetchall()
        cursor.close()

        return [
            Movimentacoes_estoque(
                id_movimentacao=linha["id_movimentacao"],
                id_produto=linha["id_produto"],
                tipo_movimentacao=linha["tipo_movimentacao"],
                quantidade=linha["quantidade"],
                data_movimentacao=str(linha["data_movimentacao"]),
            )
            for linha in linhas
        ]

    def atualizar(self, movimentacoes_estoque: Movimentacoes_estoque) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            """
            UPDATE movimentacoes_estoque
            SET id_produto = %s,
                tipo_movimentacao = %s,
                quantidade = %s,
                data_movimentacao = %s
            WHERE id_movimentacao = %s
            """,
            (
                movimentacoes_estoque.id_produto,
                movimentacoes_estoque.tipo_movimentacao,
                movimentacoes_estoque.quantidade,
                movimentacoes_estoque.data_movimentacao,
                movimentacoes_estoque.id_movimentacao,
            ),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_movimentacao: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM movimentacoes_estoque WHERE id_movimentacao = %s",
            (id_movimentacao,),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados
