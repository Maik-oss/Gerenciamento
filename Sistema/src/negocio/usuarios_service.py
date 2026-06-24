import re

from src.dados.usuarios_repository import UsuariosRepository
from src.dominio.usuario import Usuario


def _usuario_valido(valor: str) -> bool:
    """Permite letras (com acentos), números, ponto, underline e traço."""
    return bool(re.fullmatch(r"[A-Za-zÀ-ÿ0-9._-]+", valor))


class UsuarioService:
    """Camada de negócio: aplica validações e regras simples sobre os usuários do sistema."""

    TAMANHO_MINIMO_USUARIO = 3
    TAMANHO_MINIMO_SENHA = 6
    TAMANHO_MAXIMO_SENHA = 72

    def __init__(self, repositorio: UsuariosRepository) -> None:
        self.repositorio = repositorio

    def cadastrar_usuario(self, usuario: str, senha: str) -> Usuario:
        usuario_limpo = (usuario or "").strip()
        senha_limpa = (senha or "").strip()

        if not usuario_limpo:
            raise ValueError("O nome de usuário não pode ficar vazio.")

        if len(usuario_limpo) < self.TAMANHO_MINIMO_USUARIO:
            raise ValueError(f"O nome de usuário deve ter pelo menos {self.TAMANHO_MINIMO_USUARIO} caracteres.")

        if not _usuario_valido(usuario_limpo):
            raise ValueError("O nome de usuário deve conter apenas letras, números, ponto, underline ou traço.")

        if not senha_limpa:
            raise ValueError("A senha não pode ficar vazia.")

        if len(senha_limpa) < self.TAMANHO_MINIMO_SENHA:
            raise ValueError(f"A senha deve ter pelo menos {self.TAMANHO_MINIMO_SENHA} caracteres.")

        if len(senha_limpa) > self.TAMANHO_MAXIMO_SENHA:
            raise ValueError(f"A senha deve ter no máximo {self.TAMANHO_MAXIMO_SENHA} caracteres.")

        if self.repositorio.buscar_por_usuario(usuario_limpo) is not None:
            raise ValueError(f"Já existe um usuário cadastrado com o nome '{usuario_limpo}'.")

        usuario_obj = Usuario(
            id_usuario=None,
            usuario=usuario_limpo,
            senha=senha_limpa,
        )

        novo_id = self.repositorio.adicionar(usuario_obj)
        usuario_obj.id_usuario = novo_id

        return usuario_obj

    def listar_usuarios(self) -> list[Usuario]:
        usuarios = self.repositorio.listar_todos()

        if not usuarios:
            raise ValueError("Não existem usuários cadastrados no sistema.")

        return usuarios

    def buscar_usuario_por_nome(self, nome: str) -> list[Usuario]:
        nome_limpo = (nome or "").strip()

        if not nome_limpo:
            raise ValueError("Digite um nome para buscar.")

        resultados = self.repositorio.buscar_por_nome(nome_limpo)

        if not resultados:
            raise ValueError("Nenhum usuário encontrado com esse nome.")

        return resultados

    def atualizar_usuario(self, id_usuario: int, usuario: str, senha: str) -> bool:
        usuario_limpo = (usuario or "").strip()
        senha_limpa = (senha or "").strip()

        if not id_usuario:
            raise ValueError("Não foi fornecido um ID.")

        if id_usuario <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")

        if not usuario_limpo:
            raise ValueError("O nome de usuário não pode ficar vazio.")

        if len(usuario_limpo) < self.TAMANHO_MINIMO_USUARIO:
            raise ValueError(f"O nome de usuário deve ter pelo menos {self.TAMANHO_MINIMO_USUARIO} caracteres.")

        if not _usuario_valido(usuario_limpo):
            raise ValueError("O nome de usuário deve conter apenas letras, números, ponto, underline ou traço.")

        existente = self.repositorio.buscar_por_usuario(usuario_limpo)
        if existente is not None and existente.id_usuario != id_usuario:
            raise ValueError(f"Já existe outro usuário cadastrado com o nome '{usuario_limpo}'.")

        # Senha em branco: mantém a senha já cadastrada.
        if senha_limpa:
            if len(senha_limpa) < self.TAMANHO_MINIMO_SENHA:
                raise ValueError(f"A senha deve ter pelo menos {self.TAMANHO_MINIMO_SENHA} caracteres.")
            if len(senha_limpa) > self.TAMANHO_MAXIMO_SENHA:
                raise ValueError(f"A senha deve ter no máximo {self.TAMANHO_MAXIMO_SENHA} caracteres.")
        else:
            atual = self.repositorio.buscar_por_id(id_usuario)
            if atual is None:
                raise ValueError("Usuário não encontrado.")
            senha_limpa = atual.senha

        usuario_obj = Usuario(
            id_usuario=id_usuario,
            usuario=usuario_limpo,
            senha=senha_limpa,
        )

        return self.repositorio.atualizar(usuario_obj)

    def remover_usuario(self, id_usuario: int) -> bool:
        if not id_usuario:
            raise ValueError("Não foi fornecido um ID.")

        if id_usuario <= 0:
            raise ValueError("O ID deve ser um número inteiro positivo.")

        # Nunca deixa o sistema sem nenhum usuário cadastrado — senão ninguém
        # mais conseguiria fazer login no gerenciador.
        if len(self.repositorio.listar_todos()) <= 1:
            raise ValueError("Não é possível remover o único usuário cadastrado no sistema.")

        return self.repositorio.remover(id_usuario)
