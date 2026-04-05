from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session

DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI()


# FUNÇÃO PARA ABRIR E FECHAR A SESSÃO DO BANCO
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FUNÇÃO AUXILIAR PARA PADRONIZAR ERROS
def erro(status_code: int, mensagem: str):
    raise HTTPException(
        status_code=status_code,
        detail={
            "error": mensagem,
            "statusCode": status_code
        }
    )


# MODELS DO BANCO

class Aluno(Base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    ativo = Column(Boolean, default=True)  # soft delete


class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)  # soft delete


class Matricula(Base):
    __tablename__ = "matriculas"

    id = Column(Integer, primary_key=True)
    aluno_id = Column(Integer, ForeignKey("alunos.id"))
    curso_id = Column(Integer, ForeignKey("cursos.id"))
    status = Column(String, default="ativa")


# SCHEMAS DO PYDANTIC

class AlunoCreate(BaseModel):
    nome: str
    email: EmailStr

    @field_validator("email")
    def normalizar_email(cls, v):
        return v.lower()

    @field_validator("nome")
    def validar_nome(cls, v):
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v.strip()


class CursoCreate(BaseModel):
    titulo: str

    @field_validator("titulo")
    def validar_titulo(cls, v):
        if not v.strip():
            raise ValueError("Título não pode ser vazio")
        return v.strip()


class MatriculaCreate(BaseModel):
    aluno_id: int
    curso_id: int


# CRIA AS TABELAS NO BANCO
Base.metadata.create_all(bind=engine)


# =========================
# ROTAS DE ALUNOS
# =========================

@app.post("/alunos")
def criar_aluno(aluno: AlunoCreate, db: Session = Depends(get_db)):
    existente = db.query(Aluno).filter(
        Aluno.email == aluno.email
    ).first()

    if existente:
        if existente.ativo:
            erro(400, "Email já cadastrado")
        else:
            existente.nome = aluno.nome
            existente.ativo = True
            db.commit()
            db.refresh(existente)

            return {
                "id": existente.id,
                "nome": existente.nome,
                "email": existente.email
            }

    novo = Aluno(
        nome=aluno.nome,
        email=aluno.email
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return {
        "id": novo.id,
        "nome": novo.nome,
        "email": novo.email
    }


@app.get("/alunos")
def listar_alunos(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    alunos = db.query(Aluno).filter(
        Aluno.ativo == True
    ).order_by(Aluno.nome).offset(skip).limit(limit).all()

    return [
        {
            "id": a.id,
            "nome": a.nome,
            "email": a.email
        }
        for a in alunos
    ]


@app.get("/alunos/{id}")
def buscar_aluno(id: int, db: Session = Depends(get_db)):
    aluno = db.query(Aluno).filter(
        Aluno.id == id,
        Aluno.ativo == True
    ).first()

    if not aluno:
        erro(404, "Aluno não encontrado")

    return {
        "id": aluno.id,
        "nome": aluno.nome,
        "email": aluno.email
    }


@app.put("/alunos/{id}")
def atualizar_aluno(id: int, aluno: AlunoCreate, db: Session = Depends(get_db)):
    aluno_db = db.query(Aluno).filter(
        Aluno.id == id,
        Aluno.ativo == True
    ).first()

    if not aluno_db:
        erro(404, "Aluno não encontrado")

    email_existente = db.query(Aluno).filter(
        Aluno.email == aluno.email,
        Aluno.id != id
    ).first()

    if email_existente:
        erro(400, "Email já cadastrado")

    aluno_db.nome = aluno.nome
    aluno_db.email = aluno.email

    db.commit()
    db.refresh(aluno_db)

    return {
        "id": aluno_db.id,
        "nome": aluno_db.nome,
        "email": aluno_db.email
    }


@app.delete("/alunos/{id}")
def deletar_aluno(id: int, db: Session = Depends(get_db)):
    aluno = db.query(Aluno).filter(
        Aluno.id == id,
        Aluno.ativo == True
    ).first()

    if not aluno:
        erro(404, "Aluno não encontrado")

    aluno.ativo = False
    db.commit()

    return {"mensagem": "Aluno desativado com sucesso"}


# =========================
# ROTAS DE CURSOS
# =========================

@app.post("/cursos")
def criar_curso(curso: CursoCreate, db: Session = Depends(get_db)):
    titulo_normalizado = curso.titulo.strip().lower()

    existente = db.query(Curso).filter(
        func.lower(Curso.titulo) == titulo_normalizado
    ).first()

    if existente:
        if existente.ativo:
            erro(400, "Curso já cadastrado")
        else:
            existente.ativo = True
            existente.titulo = curso.titulo.strip()
            db.commit()
            db.refresh(existente)

            return {
                "id": existente.id,
                "titulo": existente.titulo
            }

    novo = Curso(titulo=curso.titulo.strip())

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return {
        "id": novo.id,
        "titulo": novo.titulo
    }


@app.get("/cursos")
def listar_cursos(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    cursos = db.query(Curso).filter(
        Curso.ativo == True
    ).order_by(Curso.titulo).offset(skip).limit(limit).all()

    return [
        {
            "id": c.id,
            "titulo": c.titulo
        }
        for c in cursos
    ]


@app.get("/cursos/{id}")
def buscar_curso(id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(
        Curso.id == id,
        Curso.ativo == True
    ).first()

    if not curso:
        erro(404, "Curso não encontrado")

    return {
        "id": curso.id,
        "titulo": curso.titulo
    }


@app.delete("/cursos/{id}")
def deletar_curso(id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(
        Curso.id == id,
        Curso.ativo == True
    ).first()

    if not curso:
        erro(404, "Curso não encontrado")

    curso.ativo = False
    db.commit()

    return {"mensagem": "Curso desativado com sucesso"}


# =========================
# ROTAS DE MATRÍCULAS
# =========================

@app.post("/matriculas")
def criar_matricula(dados: MatriculaCreate, db: Session = Depends(get_db)):
    aluno = db.query(Aluno).filter(
        Aluno.id == dados.aluno_id,
        Aluno.ativo == True
    ).first()

    if not aluno:
        erro(404, "Aluno não encontrado")

    curso = db.query(Curso).filter(
        Curso.id == dados.curso_id,
        Curso.ativo == True
    ).first()

    if not curso:
        erro(404, "Curso não encontrado")

    matricula_existente = db.query(Matricula).filter(
        Matricula.aluno_id == dados.aluno_id,
        Matricula.curso_id == dados.curso_id
    ).first()

    if matricula_existente:
        erro(400, "Aluno já matriculado neste curso")

    total_ativas = db.query(Matricula).filter(
        Matricula.aluno_id == dados.aluno_id,
        Matricula.status == "ativa"
    ).count()

    if total_ativas >= 5:
        erro(400, "Aluno já possui 5 matrículas ativas")

    nova = Matricula(
        aluno_id=dados.aluno_id,
        curso_id=dados.curso_id,
        status="ativa"
    )

    db.add(nova)
    db.commit()
    db.refresh(nova)

    return {
        "id": nova.id,
        "aluno_id": nova.aluno_id,
        "curso_id": nova.curso_id,
        "status": nova.status
    }


@app.get("/matriculas")
def listar_matriculas(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    matriculas = db.query(Matricula).order_by(Matricula.id).offset(skip).limit(limit).all()

    return [
        {
            "id": m.id,
            "aluno_id": m.aluno_id,
            "curso_id": m.curso_id,
            "status": m.status
        }
        for m in matriculas
    ]


@app.put("/matriculas/{id}/cancelar")
def cancelar_matricula(id: int, db: Session = Depends(get_db)):
    matricula = db.query(Matricula).filter(Matricula.id == id).first()

    if not matricula:
        erro(404, "Matrícula não encontrada")

    matricula.status = "cancelada"
    db.commit()
    db.refresh(matricula)

    return {
        "id": matricula.id,
        "aluno_id": matricula.aluno_id,
        "curso_id": matricula.curso_id,
        "status": matricula.status
    }


@app.put("/matriculas/{id}/concluir")
def concluir_matricula(id: int, db: Session = Depends(get_db)):
    matricula = db.query(Matricula).filter(Matricula.id == id).first()

    if not matricula:
        erro(404, "Matrícula não encontrada")

    matricula.status = "concluida"
    db.commit()
    db.refresh(matricula)

    return {
        "id": matricula.id,
        "aluno_id": matricula.aluno_id,
        "curso_id": matricula.curso_id,
        "status": matricula.status
    }


@app.get("/alunos/{id}/cursos")
def listar_cursos_do_aluno(
    id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    aluno = db.query(Aluno).filter(
        Aluno.id == id,
        Aluno.ativo == True
    ).first()

    if not aluno:
        erro(404, "Aluno não encontrado")

    matriculas = db.query(Matricula).filter(
        Matricula.aluno_id == id
    ).order_by(Matricula.id).offset(skip).limit(limit).all()

    return [
        {
            "id_matricula": m.id,
            "curso_id": m.curso_id,
            "status": m.status
        }
        for m in matriculas
    ]


@app.get("/cursos/{id}/alunos")
def listar_alunos_do_curso(
    id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    curso = db.query(Curso).filter(
        Curso.id == id,
        Curso.ativo == True
    ).first()

    if not curso:
        erro(404, "Curso não encontrado")

    matriculas = db.query(Matricula).filter(
        Matricula.curso_id == id
    ).order_by(Matricula.id).offset(skip).limit(limit).all()

    return [
        {
            "id_matricula": m.id,
            "aluno_id": m.aluno_id,
            "status": m.status
        }
        for m in matriculas
    ]
