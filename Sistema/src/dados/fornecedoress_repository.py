import mysql.connector

from src.dominio.fornecedores import Fornecedores


class FornecedoresRepository:

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def adicionar(self, fornecedores: Fornecedores) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            """
            INSERT INTO fornecedores
            (nome, tipo, cnpj, telefone_fornecedor, cpf, email, cidade, estado, data_cadastro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                fornecedores.nome,
                fornecedores.tipo,
                fornecedores.cnpj,
                fornecedores.telefone_fornecedor,
                fornecedores.cpf,
                fornecedores.email,
                fornecedores.cidade,
                fornecedores.estado,
                fornecedores.data_cadastro,
            ),
        )
        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def listar_todos(self) -> list[Fornecedores]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_fornecedor, nome, tipo, cnpj, telefone_fornecedor, cpf,
                   email, cidade, estado, data_cadastro
            FROM fornecedores
            ORDER BY id_fornecedor
            """
        )
        linhas = cursor.fetchall()
        cursor.close()

        return [
            Fornecedores(
                id_fornecedor=linha["id_fornecedor"],
                nome=linha["nome"],
                tipo=linha["tipo"],
                cnpj=linha["cnpj"],
                telefone_fornecedor=linha["telefone_fornecedor"],
                cpf=linha["cpf"],
                email=linha["email"],
                cidade=linha["cidade"],
                estado=linha["estado"],
                data_cadastro=str(linha["data_cadastro"]),
            )
            for linha in linhas
        ]

    def buscar_por_nome(self, nome: str) -> list[Fornecedores]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_fornecedor, nome, tipo, cnpj, telefone_fornecedor, cpf,
                   email, cidade, estado, data_cadastro
            FROM fornecedores
            WHERE nome LIKE %s
            ORDER BY id_fornecedor
            """,
            (f"%{nome}%",),
        )
        linhas = cursor.fetchall()
        cursor.close()

        return [
            Fornecedores(
                id_fornecedor=linha["id_fornecedor"],
                nome=linha["nome"],
                tipo=linha["tipo"],
                cnpj=linha["cnpj"],
                telefone_fornecedor=linha["telefone_fornecedor"],
                cpf=linha["cpf"],
                email=linha["email"],
                cidade=linha["cidade"],
                estado=linha["estado"],
                data_cadastro=str(linha["data_cadastro"]),
            )
            for linha in linhas
        ]

    def atualizar(self, fornecedores: Fornecedores) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            """
            UPDATE fornecedores
            SET nome = %s,
                tipo = %s,
                cnpj = %s,
                telefone_fornecedor = %s,
                cpf = %s,
                email = %s,
                cidade = %s,
                estado = %s,
                data_cadastro = %s
            WHERE id_fornecedor = %s
            """,
            (
                fornecedores.nome,
                fornecedores.tipo,
                fornecedores.cnpj,
                fornecedores.telefone_fornecedor,
                fornecedores.cpf,
                fornecedores.email,
                fornecedores.cidade,
                fornecedores.estado,
                fornecedores.data_cadastro,
                fornecedores.id_fornecedor,
            ),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_fornecedor: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE produtos SET id_fornecedor = NULL WHERE id_fornecedor = %s",
            (id_fornecedor,),
        )
        cursor.execute(
            "UPDATE telefone_fornecedor SET id_fornecedor = NULL WHERE id_fornecedor = %s",
            (id_fornecedor,),
        )
        cursor.execute(
            "DELETE FROM fornecedores WHERE id_fornecedor = %s",
            (id_fornecedor,),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados
