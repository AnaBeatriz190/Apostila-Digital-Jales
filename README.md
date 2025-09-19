# 📘 Apostila Digital

## 📖 Introdução
O **Apostila Digital** é uma plataforma voltada para a disponibilização de conteúdo educacional em formato digital.  
Professores podem criar disciplinas, turmas e organizar conteúdos em tópicos e unidades com páginas HTML.  
Os alunos acessam o conteúdo **apenas após aceitarem o convite enviado por e-mail**.  

### O sistema possibilita:
- Acompanhamento do progresso dos alunos na visualização dos conteúdos.  
- Controle de matrículas.  
- Edição e arquivamento de turmas.  

Tudo isso garante um **ambiente digital estruturado** para ensino e acompanhamento de atividades acadêmicas.  

---

## 👥 Usuários
- Professor  
- Aluno  

---

## 🛠 Tecnologias
- **GitHub** → versionamento e colaboração  
- **Flask** → framework backend em Python  
- **MySQL** → banco de dados relacional  
- **Bootstrap** → estilização e responsividade do frontend  

---

## ⚙️ Funcionalidades

### F1 - Login (Página inicial)
- **Professor**: cadastrado diretamente no banco de dados (e-mail + senha).  
- **Aluno**: cadastrado pelo professor em uma disciplina.  
  - Inicialmente, o aluno é considerado **convidado**.  
  - Só se torna ativo após aceitar o convite por e-mail e acessar o sistema.  
  - Recebe senha aleatória (8–12 dígitos) enviada por e-mail.  
- **Troca obrigatória de senha** no primeiro acesso (professor).  

---

### F2 - Dashboard do Professor
- Exibe as disciplinas criadas.  
- Em cada card:  
  - Quantidade de alunos matriculados (sem contar convidados).  
  - Ícones para **editar** e **excluir** disciplina.  
- Opção de **adicionar nova disciplina**.  

---

### F3 - Cadastro de Disciplinas
- Professor define **nome** e **cor do tema** da disciplina.  

---

### F4 - Cadastro de Conteúdo
- Criar **tópicos** e **unidades**.  
- Upload de páginas **HTML** nos tópicos.  
- Unidades vinculadas ao tópico.  
- Ordenação via **drag-and-drop** (tópicos e unidades).  

---

### F5 - Cadastro de Turmas (Vinculado a uma Disciplina)
- Dentro da disciplina, exibição dos **cards de turmas**.  
- Opções: **adicionar**, **editar**, **excluir** e **arquivar** turma.  
- Exibir quantidade de alunos matriculados (sem convidados).  
- Botão para visualizar turmas **arquivadas**.  

---

### F6 - Cadastro de Alunos nas Turmas
- Pop-up para inserção de e-mails (um por linha).  
- Se o aluno **não estiver cadastrado**:  
  - E-mail enviado automaticamente com credenciais.  
- Se o aluno **já estiver cadastrado**:  
  - Ele é **vinculado à turma**.  

---

### F7 - Acompanhamento de Alunos por Turma
- Exibição do **progresso dos alunos** em formato de tabela.  
- **Checkbox não-editável**, marcado quando o aluno visitou o conteúdo.  

---

### F8 - Dashboard do Aluno
- Exibe as turmas do aluno (**matriculado ou convidado**).  
- Opção de **aceitar convite**.  

---

### F9 - Tela de Conteúdo
- Acessível apenas após **aceitar convite da turma**.  

---

### F10 - Alterar/Recuperar Senha
- Funcionalidade prevista para redefinição de senha.  

---

## 🔮 Futuro
- Compartilhar disciplina com outro professor.  
- Monitorar **tempo do aluno** em cada tópico.  
