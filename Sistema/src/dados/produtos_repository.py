import mysql.connector

from src.dominio.produto import Produto


class ProdutoRepository:

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def adicionar(self, produto: Produto) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            """
            INSERT INTO produtos (id_fornecedor, nome, preco, quantidade, data_cadastro, data_validade)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (produto.id_fornecedor, produto.nome, produto.preco, produto.quantidade, produto.data_cadastro, produto.data_validade),
        )
        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def listar_todos(self) -> list[Produto]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_produto, id_fornecedor, nome, preco, quantidade, data_cadastro, data_validade
            FROM produtos
            ORDER BY id_produto
            """
        )
        linhas = cursor.fetchall()
        cursor.close()

        return [
            Produto(
                id_produto=linha["id_produto"],
                id_fornecedor=linha["id_fornecedor"],
                nome=linha["nome"],
                preco=float(linha["preco"]),
                quantidade=linha["quantidade"],
                data_cadastro=str(linha["data_cadastro"]),
                data_validade=str(linha["data_validade"]),
            )
            for linha in linhas
        ]

    def buscar_por_nome(self, nome: str) -> list[Produto]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_produto, id_fornecedor, nome, preco, quantidade, data_cadastro, data_validade
            FROM produtos
            WHERE nome LIKE %s
            ORDER BY id_produto
            """,
            (f"%{nome}%",),
        )
        linhas = cursor.fetchall()
        cursor.close()

        return [
            Produto(
                id_produto=linha["id_produto"],
                id_fornecedor=linha["id_fornecedor"],
                nome=linha["nome"],
                preco=float(linha["preco"]),
                quantidade=linha["quantidade"],
                data_cadastro=str(linha["data_cadastro"]),
                data_validade=str(linha["data_validade"]),
            )
            for linha in linhas
        ]

    def atualizar(self, produto: Produto) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            """
            UPDATE produtos
            SET id_fornecedor = %s,
                nome = %s,
                preco = %s,
                quantidade = %s,
                data_cadastro = %s,
                data_validade = %s
            WHERE id_produto = %s
            """,
            (produto.id_fornecedor, produto.nome, produto.preco, produto.quantidade, produto.data_cadastro, produto.data_validade, produto.id_produto),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_produto: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE movimentacoes_estoque SET id_produto = NULL WHERE id_produto = %s",
            (id_produto,),
        )
        cursor.execute(
            "DELETE FROM produtos WHERE id_produto = %s",
            (id_produto,),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados
