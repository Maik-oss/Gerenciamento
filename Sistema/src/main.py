from src.negocio.produtos_service import ProdutoService
from src.negocio.fornecedoress_service import FornecedoresService
from src.negocio.telefones_forn_service import TelefoneService
from src.negocio.movimentacoess_service import MovimentacoesService

from src.dados.conexao_singleton import ConexaoSingleton
from src.dados.produtos_repository import ProdutoRepository
from src.dados.fornecedoress_repository import FornecedoresRepository
from src.dados.telefones_fornecedor_repository import Telefone_fornecedor_Repository
from src.dados.movimentacoess_repository import MovimentacoesRepository

from src.apresentacao.gui_principal import SistemaGUI


def principal() -> None:

    conexao = ConexaoSingleton.obter_conexao(
        tipo_banco="mysql",
        host="127.0.0.1",
        porta=3306,
        usuario="root",
        senha="labinfo",
        banco="gerenciamento",
    )

    repositorio_produto = ProdutoRepository(conexao)
    servico_produto = ProdutoService(repositorio_produto)

    repositorio_fornecedor = FornecedoresRepository(conexao)
    servico_fornecedor = FornecedoresService(repositorio_fornecedor)

    repositorio_telefone = Telefone_fornecedor_Repository(conexao)
    servico_telefone = TelefoneService(repositorio_telefone)

    repositorio_movimentacao = MovimentacoesRepository(conexao)
    servico_movimentacao = MovimentacoesService(repositorio_movimentacao)

    gui = SistemaGUI(
        servico_produto=servico_produto,
        servico_fornecedor=servico_fornecedor,
        servico_telefone=servico_telefone,
        servico_movimentacao=servico_movimentacao,
    )

    try:
        gui.executar()
    finally:
        ConexaoSingleton.fechar_conexao()


if __name__ == "__main__":
    principal()
