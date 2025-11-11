-- Script para criação do schema e tabelas no MySQL
-- CUIDADO: Este script apaga o banco de dados se ele já existir.

CREATE DATABASE IF NOT EXISTS sua_app_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE sua_app_db;

-- Tabela de Professores
-- Professores são cadastrados diretamente no banco.
CREATE TABLE IF NOT EXISTS professor (
    id INT AUTO_INCREMENT PRIMARY_KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL
) ENGINE=InnoDB;

-- Tabela de Alunos
CREATE TABLE IF NOT EXISTS aluno (
    id INT AUTO_INCREMENT PRIMARY_KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    
    -- 'convidado': acabou de ser cadastrado pelo professor
    -- 'ativo': já fez o primeiro login e mudou a senha
    status ENUM('convidado', 'ativo') NOT NULL DEFAULT 'convidado',
    
    -- Flag para forçar a troca de senha no primeiro login
    primeiro_acesso BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- Tabela de Disciplinas
CREATE TABLE IF NOT EXISTS disciplina (
    id INT AUTO_INCREMENT PRIMARY_KEY,
    nome VARCHAR(100) NOT NULL,
    
    -- Chave estrangeira para o professor que leciona
    professor_id INT NOT NULL,
    FOREIGN KEY (professor_id) REFERENCES professor(id)
        ON DELETE CASCADE -- Se o professor for deletado, a disciplina também é.
) ENGINE=InnoDB;

-- Tabela de Associação (Muitos-para-Muitos)
-- Define quais alunos estão matriculados em quais disciplinas
CREATE TABLE IF NOT EXISTS aluno_disciplina (
    aluno_id INT NOT NULL,
    disciplina_id INT NOT NULL,
    
    PRIMARY KEY (aluno_id, disciplina_id),
    
    FOREIGN KEY (aluno_id) REFERENCES aluno(id)
        ON DELETE CASCADE, -- Se o aluno for deletado, a matrícula some.
        
    FOREIGN KEY (disciplina_id) REFERENCES disciplina(id)
        ON DELETE CASCADE -- Se a disciplina for deletada, a matrícula some.
) ENGINE=InnoDB;

-- Exemplo: Inserir um professor manualmente (Hash da senha "senha123")
-- Lembre-se: Em produção, o hash deve ser gerado pela aplicação, não manualmente!
-- O hash abaixo é apenas para fins de exemplo e corresponde a 'senha123'
INSERT IGNORE INTO professor (nome, email, password_hash) 
VALUES (
    'Professor Admin', 
    'admin@email.com', 
    '$2b$12$EaG2J8y9i9yL8K1X.1K5d.X.s8b1l6C.D.gYw/8l.3qfH/jZ/g.G'
);