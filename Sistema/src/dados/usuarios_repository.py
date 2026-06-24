import base64

import mysql.connector

from src.dominio.usuario import Usuario

# Chave fixa usada só para "embaralhar" a senha antes de salvar no banco.
# Importante: isso NÃO é uma criptografia forte de verdade — é uma cifra
# simples (XOR + base64) que a própria aplicação consegue reverter, porque
# a chave mora aqui no código-fonte. Protege contra alguém só abrindo o
# banco direto (ex.: um cliente MySQL ou um backup), mas não contra quem
# também tem acesso a este código-fonte.
_CHAVE_SENHA = b"ImperialRango#2026!"


def _cifrar(senha: str) -> str:
    """Embaralha a senha antes de gravar no banco (reversível com _decifrar)."""
    dados = senha.encode("utf-8")
    cifrado = bytes(b ^ _CHAVE_SENHA[i % len(_CHAVE_SENHA)] for i, b in enumerate(dados))
    return base64.b64encode(cifrado).decode("ascii")


def _decifrar(valor: str) -> str:
    """Reverte o que _cifrar fez, devolvendo a senha real."""
    cifrado = base64.b64decode(valor.encode("ascii"))
    dados = bytes(b ^ _CHAVE_SENHA[i % len(_CHAVE_SENHA)] for i, b in enumerate(cifrado))
    return dados.decode("utf-8")


class UsuariosRepository:
    """Camada de dados: acesso à tabela 'usuarios' do banco.

    A senha é gravada cifrada no banco e decifrada ao ser lida — para o
    resto do sistema (negócio e tela), o objeto Usuario sempre tem a senha
    real em texto puro; só aqui dentro ela existe cifrada.
    """

    def __init__(self, conexao: mysql.connector.MySQLConnection) -> None:
        self.conexao = conexao

    def buscar_por_usuario(self, usuario: str) -> "Usuario | None":
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_usuario, usuario, senha FROM usuarios WHERE usuario = %s AND ativo = 1",
            (usuario,),
        )
        linha = cursor.fetchone()
        cursor.close()

        if not linha:
            return None

        return Usuario(
            id_usuario=linha["id_usuario"],
            usuario=linha["usuario"],
            senha=_decifrar(linha["senha"]),
        )

    def buscar_por_id(self, id_usuario: int) -> "Usuario | None":
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_usuario, usuario, senha FROM usuarios WHERE id_usuario = %s",
            (id_usuario,),
        )
        linha = cursor.fetchone()
        cursor.close()

        if not linha:
            return None

        return Usuario(
            id_usuario=linha["id_usuario"],
            usuario=linha["usuario"],
            senha=_decifrar(linha["senha"]),
        )

    def adicionar(self, usuario: Usuario) -> int:
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)",
            (usuario.usuario, _cifrar(usuario.senha)),
        )
        self.conexao.commit()
        novo_id = int(cursor.lastrowid)
        cursor.close()
        return novo_id

    def listar_todos(self) -> list[Usuario]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_usuario, usuario, senha FROM usuarios ORDER BY id_usuario"
        )
        linhas = cursor.fetchall()
        cursor.close()

        return [
            Usuario(
                id_usuario=linha["id_usuario"],
                usuario=linha["usuario"],
                senha=_decifrar(linha["senha"]),
            )
            for linha in linhas
        ]

    def buscar_por_nome(self, nome: str) -> list[Usuario]:
        cursor = self.conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id_usuario, usuario, senha
            FROM usuarios
            WHERE usuario LIKE %s
            ORDER BY id_usuario
            """,
            (f"%{nome}%",),
        )
        linhas = cursor.fetchall()
        cursor.close()

        return [
            Usuario(
                id_usuario=linha["id_usuario"],
                usuario=linha["usuario"],
                senha=_decifrar(linha["senha"]),
            )
            for linha in linhas
        ]

    def atualizar(self, usuario: Usuario) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE usuarios SET usuario = %s, senha = %s WHERE id_usuario = %s",
            (usuario.usuario, _cifrar(usuario.senha), usuario.id_usuario),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados

    def remover(self, id_usuario: int) -> bool:
        cursor = self.conexao.cursor()
        cursor.execute(
            "DELETE FROM usuarios WHERE id_usuario = %s",
            (id_usuario,),
        )
        self.conexao.commit()
        afetados = cursor.rowcount > 0
        cursor.close()
        return afetados
