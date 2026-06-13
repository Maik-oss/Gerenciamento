import mysql.connector

from src.dominio.telefone import TelefoneFornecedor


class Telefone_fornecedor_Repository:

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def adicionar(self, telefone_fornecedor: TelefoneFornecedor) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO telefone_fornecedor (id_fornecedor, numero) VALUES (%s, %s)",
            (telefone_fornecedor.id_fornecedor, telefone_fornecedor.numero),
        )
        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def listar_todos(self) -> list[TelefoneFornecedor]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_telefone, id_fornecedor, numero FROM telefone_fornecedor ORDER BY id_telefone"
        )
        linhas = cursor.fetchall()
        cursor.close()

        return [
            TelefoneFornecedor(
                id_telefone=linha["id_telefone"],
                id_fornecedor=linha["id_fornecedor"],
                numero=linha["numero"],
            )
            for linha in linhas
        ]

    def buscar_por_nome_fornecedor(self, nome: str) -> list[TelefoneFornecedor]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT tf.id_telefone, tf.id_fornecedor, tf.numero
            FROM telefone_fornecedor tf
            INNER JOIN fornecedores f ON f.id_fornecedor = tf.id_fornecedor
            WHERE f.nome LIKE %s
            ORDER BY tf.id_telefone
            """,
            (f"%{nome}%",),
        )
        linhas = cursor.fetchall()
        cursor.close()

        return [
            TelefoneFornecedor(
                id_telefone=linha["id_telefone"],
                id_fornecedor=linha["id_fornecedor"],
                numero=linha["numero"],
            )
            for linha in linhas
        ]

    def atualizar(self, telefone_fornecedor: TelefoneFornecedor) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            """
            UPDATE telefone_fornecedor
            SET id_fornecedor = %s,
                numero = %s
            WHERE id_telefone = %s
            """,
            (telefone_fornecedor.id_fornecedor, telefone_fornecedor.numero, telefone_fornecedor.id_telefone),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_telefone: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM telefone_fornecedor WHERE id_telefone = %s",
            (id_telefone,),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados
