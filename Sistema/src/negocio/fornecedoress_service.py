from typing import Optional
from email_validator import validate_email, EmailNotValidError
from src.dados.fornecedoress_repository import FornecedoresRepository
from src.dominio.fornecedores import Fornecedores
import re
from datetime import datetime


def _somente_numeros_e_pontuacao(valor: str) -> bool:
    """Permite dígitos, ponto, barra, traço, parênteses e espaço."""
    return bool(re.fullmatch(r'[\d.\-/()\s]+', valor))


UFS_VALIDAS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


def _uf_valida(valor: str) -> bool:
    """Verifica se o valor é uma sigla de estado (UF) válida."""
    return valor.strip().upper() in UFS_VALIDAS


class FornecedoresService:
    """Camada de negócio: aplica validações e regras simples."""

    def __init__(self, repositorio: FornecedoresRepository) -> None:
        self.repositorio = repositorio

    def cadastrar_fornecedor(self, nome: str, tipo: str, cnpj: str, telefone_fornecedor: str, cpf: str, email: str, cidade: str, estado: str, data_cadastro: str) -> Fornecedores:
        nome_limpo = nome.strip()
        cpf_limpo = cpf.strip()
        cnpj_limpo = cnpj.strip()
        telefone_fornecedor_limpo = telefone_fornecedor.strip()
        email_valido = email.strip()
        cidade_limpo = cidade.strip()
        estado_limpo = estado.strip()
        data_cadastro_limpo = data_cadastro.strip()

        if not nome_limpo:
            raise ValueError("O nome do fornecedor nao pode ficar vazio.")

        if tipo.strip().lower() not in ("pessoa", "empresa"):
            raise ValueError("O tipo do fornecedor deve ser 'pessoa' ou 'empresa'.")

        if tipo.strip().lower() == "pessoa":
            if not cpf_limpo:
                raise ValueError("O CPF do fornecedor não pode ficar vazio.")
            if not _somente_numeros_e_pontuacao(cpf_limpo):
                raise ValueError("O CPF deve conter apenas dígitos, pontos, barras ou traços.")
            cnpj_limpo = ""
        else:
            if not cnpj_limpo:
                raise ValueError("O CNPJ não pode ficar vazio.")
            if not _somente_numeros_e_pontuacao(cnpj_limpo):
                raise ValueError("O CNPJ deve conter apenas dígitos, pontos, barras ou traços.")
            cpf_limpo = ""

        if not telefone_fornecedor_limpo:
            raise ValueError("O telefone do fornecedor não pode ficar vazio.")

        if not _somente_numeros_e_pontuacao(telefone_fornecedor_limpo):
            raise ValueError("O telefone deve conter apenas dígitos, pontos, barras ou traços.")

        if email_valido:
            try:
                info = validate_email(email_valido, check_deliverability=False)
                email_valido = info.normalized
            except EmailNotValidError:
                raise ValueError("E-mail inválido")
        else:
            raise ValueError("E-mail inválido")

        if not cidade_limpo:
            raise ValueError("A cidade do fornecedor não pode ficar vazia.")

        if not estado_limpo:
            raise ValueError("O estado do fornecedor não pode ficar vazio.")

        if not _uf_valida(estado_limpo):
            raise ValueError("O estado deve ser uma sigla de UF válida (ex.: RN, CE).")

        estado_limpo = estado_limpo.upper()

        if not data_cadastro_limpo:
            raise ValueError("A data de cadastro não pode ficar vazia.")

        try:
            data_cadastro_mysql = datetime.strptime(data_cadastro_limpo, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Data inválida. Use o formato dd/mm/aaaa.")

        fornecedor = Fornecedores(
            id_fornecedor=None,
            nome=nome_limpo,
            tipo=tipo,
            cnpj=cnpj_limpo,
            telefone_fornecedor=telefone_fornecedor_limpo,
            cpf=cpf_limpo,
            email=email_valido,
            cidade=cidade_limpo,
            estado=estado_limpo,
            data_cadastro=data_cadastro_mysql,
        )

        novo_id = self.repositorio.adicionar(fornecedor)
        fornecedor.id_fornecedor = novo_id

        return fornecedor

    def listar_fornecedores(self) -> list[Fornecedores]:
        fornecedores = self.repositorio.listar_todos()

        if not fornecedores:
            raise ValueError("Não existe fornecedores cadastrados no sistema.")

        return fornecedores

    def buscar_fornecedor_por_nome(self, nome: str) -> list[Fornecedores]:
        nome_limpo = nome.strip()

        if not nome_limpo:
            raise ValueError("Digite um nome para buscar.")

        resultados = self.repositorio.buscar_por_nome(nome_limpo)

        if not resultados:
            raise ValueError("Nenhum fornecedor encontrado com esse nome.")

        return resultados

    def atualizar_fornecedor(self, id_fornecedor: int, nome: str, tipo: str, cnpj: str, telefone_fornecedor: str, cpf: str, email: str, cidade: str, estado: str, data_cadastro: str) -> bool:
        nome_limpo = nome.strip()
        cpf_limpo = cpf.strip()
        cnpj_limpo = cnpj.strip()
        telefone_fornecedor_limpo = telefone_fornecedor.strip()
        email_valido = email.strip()
        cidade_limpo = cidade.strip()
        estado_limpo = estado.strip()
        data_cadastro_limpo = data_cadastro.strip()

        if not id_fornecedor:
            raise ValueError("Não foi fornecido um ID.")

        if id_fornecedor <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

        if not nome_limpo:
            raise ValueError("O nome do fornecedor nao pode ficar vazio.")

        if tipo.strip().lower() not in ("pessoa", "empresa"):
            raise ValueError("O tipo do fornecedor deve ser 'pessoa' ou 'empresa'.")

        if tipo.strip().lower() == "pessoa":
            if not cpf_limpo:
                raise ValueError("O CPF não pode ficar vazio.")
            if not _somente_numeros_e_pontuacao(cpf_limpo):
                raise ValueError("O CPF deve conter apenas dígitos, pontos, barras ou traços.")
            cnpj_limpo = ""
        else:
            if not cnpj_limpo:
                raise ValueError("O CNPJ não pode ficar vazio.")
            if not _somente_numeros_e_pontuacao(cnpj_limpo):
                raise ValueError("O CNPJ deve conter apenas dígitos, pontos, barras ou traços.")
            cpf_limpo = ""

        if not telefone_fornecedor_limpo:
            raise ValueError("O telefone não pode ficar vazio.")

        if not _somente_numeros_e_pontuacao(telefone_fornecedor_limpo):
            raise ValueError("O telefone deve conter apenas dígitos, pontos, barras ou traços.")

        if email_valido:
            try:
                info = validate_email(email_valido, check_deliverability=False)
                email_valido = info.normalized
            except EmailNotValidError:
                raise ValueError("E-mail inválido")
        else:
            raise ValueError("E-mail inválido")

        if not cidade_limpo:
            raise ValueError("A cidade do fornecedor não pode ficar vazia.")

        if not estado_limpo:
            raise ValueError("O estado do fornecedor não pode ficar vazio.")

        if not _uf_valida(estado_limpo):
            raise ValueError("O estado deve ser uma sigla de UF válida (ex.: RN, CE).")

        estado_limpo = estado_limpo.upper()

        if not data_cadastro_limpo:
            raise ValueError("A data de cadastro não pode ficar vazia.")

        try:
            data_cadastro_mysql = datetime.strptime(data_cadastro_limpo, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Data inválida. Use o formato dd/mm/aaaa.")

        fornecedor = Fornecedores(
            id_fornecedor=id_fornecedor,
            nome=nome_limpo,
            tipo=tipo,
            cnpj=cnpj_limpo,
            telefone_fornecedor=telefone_fornecedor_limpo,
            cpf=cpf_limpo,
            email=email_valido,
            cidade=cidade_limpo,
            estado=estado_limpo,
            data_cadastro=data_cadastro_mysql,
        )
        return self.repositorio.atualizar(fornecedor)

    def remover_fornecedor(self, id_fornecedor: int) -> bool:
        if not id_fornecedor:
            raise ValueError("Não foi fornecido um ID.")

        if id_fornecedor <= 0:
            raise ValueError("O ID deve ser um numero inteiro positivo.")

        return self.repositorio.remover(id_fornecedor)
