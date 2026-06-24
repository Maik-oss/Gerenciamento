from src.dados.usuarios_repository import UsuariosRepository


class LoginService:
    """Camada de negócio: valida usuário e senha do gerenciador."""

    # Único usuário autorizado a acessar a área de gerenciamento de Usuários
    # (cadastrar, listar, buscar, atualizar e remover outros usuários).
    USUARIO_MESTRE = "Maikson"

    def __init__(self, repositorio: UsuariosRepository) -> None:
        self.repositorio = repositorio

    def autenticar(self, usuario: str, senha: str) -> bool:
        """Retorna True se usuário e senha forem válidos, False caso contrário.

        Não lança exceção para senha incorreta nem usuário inexistente —
        ambos os casos simplesmente retornam False, para não dar pistas
        de qual dos dois campos estava errado.
        """
        usuario_limpo = (usuario or "").strip()
        senha_limpa = (senha or "")

        if not usuario_limpo or not senha_limpa:
            return False

        cadastrado = self.repositorio.buscar_por_usuario(usuario_limpo)
        if cadastrado is None:
            return False

        return cadastrado.senha == senha_limpa

    def eh_usuario_mestre(self, usuario: str) -> bool:
        """Verifica se o nome de usuário informado é o do usuário mestre.

        Usado para liberar (ou não) o acesso à área restrita de Usuários —
        mesmo que outro usuário esteja cadastrado e tenha senha válida, só
        o usuário mestre pode entrar nessa área.
        """
        return (usuario or "").strip().lower() == self.USUARIO_MESTRE.lower()
