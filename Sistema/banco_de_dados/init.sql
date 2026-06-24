CREATE DATABASE IF NOT EXISTS gerenciamento;
USE gerenciamento;

CREATE TABLE IF NOT EXISTS usuarios(
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1
);

-- Usuário padrão do gerenciador (login: Maikson / senha: show123)
-- O valor abaixo é a senha "show123" cifrada pela própria aplicação
-- (veja _cifrar/_decifrar em usuarios_repository.py) — não é a senha em texto puro.
INSERT INTO usuarios (usuario, senha)
SELECT 'Maikson', 'OgUfEkNbUg=='
WHERE NOT EXISTS (SELECT 1 FROM usuarios WHERE usuario = 'Maikson');

CREATE TABLE IF NOT EXISTS fornecedores(
    id_fornecedor INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo ENUM('pessoa', 'empresa') NOT NULL,
    cnpj VARCHAR(18) NOT NULL,
    telefone_fornecedor VARCHAR(20) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    email VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL,
    data_cadastro DATE,
    ativo TINYINT(1) NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS telefone_fornecedor(
    id_telefone INT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(20) NOT NULL,
    id_fornecedor INT,
    ativo TINYINT(1) NOT NULL DEFAULT 1,

    FOREIGN KEY(id_fornecedor)
    REFERENCES fornecedores(id_fornecedor)
    ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS produtos(
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10,2) NOT NULL,
    quantidade INT NOT NULL,

    id_fornecedor INT,

    data_cadastro DATE NOT NULL,
    data_validade DATE NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,

    FOREIGN KEY(id_fornecedor)
    REFERENCES fornecedores(id_fornecedor)
    ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS movimentacoes_estoque(
    id_movimentacao INT AUTO_INCREMENT PRIMARY KEY,
    id_produto INT,

    tipo_movimentacao ENUM('entrada', 'saida') NOT NULL,
    quantidade INT NOT NULL,

    data_movimentacao DATE NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,

    FOREIGN KEY(id_produto)
    REFERENCES produtos(id_produto)
    ON DELETE SET NULL
);
