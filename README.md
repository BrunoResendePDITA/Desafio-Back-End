# Sistema de Cadastro de Alunos, Cursos e Matrículas

API REST desenvolvida com **FastAPI**, **SQLAlchemy** e **SQLite** para gerenciamento de alunos, cursos e matrículas.

---

## Tecnologias utilizadas

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* Uvicorn

---

## Estrutura do projeto

```text
app/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── utils.py
├── services/
├── routes/
```

O projeto foi organizado em camadas:

* **routes** → endpoints da API
* **services** → regras de negócio
* **models** → estrutura das tabelas
* **schemas** → validação dos dados
* **database** → conexão com o banco

---

## Como rodar o projeto localmente

### 1. Clonar o repositório

```bash
git clone <LINK_DO_REPOSITORIO>
cd <NOME_DA_PASTA>
```

---

### 2. Criar e ativar o ambiente virtual

#### Windows (PowerShell)

```bash
python -m venv .venv
.\.venv\Scripts\Activate
```

---

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

### 4. Rodar o servidor

```bash
uvicorn app.main:app --reload
```

---

### 5. Acessar no navegador

* API: http://127.0.0.1:8000
* Swagger (documentação): http://127.0.0.1:8000/docs

---

## Banco de dados

O projeto utiliza **SQLite**.

* O banco é criado automaticamente
* Arquivo gerado: `database.db`
* Não é necessário instalar servidor de banco

As tabelas são criadas automaticamente ao iniciar o projeto.

---

## Endpoints disponíveis

### Alunos

* `POST /alunos` → Criar aluno
* `GET /alunos` → Listar alunos
* `GET /alunos/{id}` → Buscar aluno por ID
* `PUT /alunos/{id}` → Atualizar aluno
* `DELETE /alunos/{id}` → Desativar aluno (soft delete)

---

### Cursos

* `POST /cursos` → Criar curso
* `GET /cursos` → Listar cursos
* `GET /cursos/{id}` → Buscar curso por ID
* `DELETE /cursos/{id}` → Desativar curso (soft delete)

---

### Matrículas

* `POST /matriculas` → Criar matrícula
* `GET /matriculas` → Listar matrículas
* `PUT /matriculas/{id}/cancelar` → Cancelar matrícula
* `PUT /matriculas/{id}/concluir` → Concluir matrícula
* `GET /alunos/{id}/cursos` → Cursos de um aluno
* `GET /cursos/{id}/alunos` → Alunos de um curso

---

## Regras de negócio implementadas

* Email do aluno é único
* Email é normalizado para minúsculo
* Nome do aluno não pode ser vazio
* Título do curso não pode ser vazio
* Não permite matrícula de aluno inexistente
* Não permite matrícula de curso inexistente
* Um aluno não pode se matricular duas vezes no mesmo curso
* Um aluno pode ter no máximo **5 matrículas ativas**
* Soft delete para alunos e cursos
* Reativação automática de alunos e cursos inativos

---

## Deploy

### Plataforma utilizada

Render

---

### Link da aplicação

*A adicionar após deploy*

---

### Link da API

*A adicionar após deploy*

---

### Variáveis de ambiente

Nenhuma variável de ambiente obrigatória foi utilizada.

---

### Como fazer o deploy no Render

1. Subir o projeto para o GitHub
2. Acessar https://render.com
3. Criar um novo **Web Service**
4. Conectar o repositório
5. Configurar:

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

6. Criar o serviço
7. Aguardar o deploy
8. Copiar o link gerado e adicionar neste README

---

## Observações finais

Este projeto segue uma organização em camadas, separando responsabilidades para melhor manutenção e escalabilidade.

A documentação da API pode ser acessada automaticamente via Swagger em `/docs`.
