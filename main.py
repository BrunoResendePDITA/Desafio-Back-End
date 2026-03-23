from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
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


# MODELS DO BANCO

class Aluno(Base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)


class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)


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


class CursoCreate(BaseModel):
    titulo: str


class MatriculaCreate(BaseModel):
    aluno_id: int
    curso_id: int


# CRIA AS TABELAS NO BANCO
Base.metadata.create_all(bind=engine)


# ROTAS DE ALUNOS

@app.post("/alunos")
def criar_aluno(aluno: AlunoCreate, db: Session = Depends(get_db)):
    existente = db.query(Aluno).filter(Aluno.email == aluno.email).first()

    if existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

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
def listar_alunos(db: Session = Depends(get_db)):
    alunos = db.query(Aluno).all()

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
    aluno = db.query(Aluno).filter(Aluno.id == id).first()

    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    return {
        "id": aluno.id,
        "nome": aluno.nome,
        "email": aluno.email
    }


@app.put("/alunos/{id}")
def atualizar_aluno(id: int, aluno: AlunoCreate, db: Session = Depends(get_db)):
    aluno_db = db.query(Aluno).filter(Aluno.id == id).first()

    if not aluno_db:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    email_existente = db.query(Aluno).filter(
        Aluno.email == aluno.email,
        Aluno.id != id
    ).first()

    if email_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    aluno_db.nome = aluno.nome
    aluno_db.email = aluno.email

    db.commit()

    return {
        "id": aluno_db.id,
        "nome": aluno_db.nome,
        "email": aluno_db.email
    }


@app.delete("/alunos/{id}")
def deletar_aluno(id: int, db: Session = Depends(get_db)):
    aluno = db.query(Aluno).filter(Aluno.id == id).first()

    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    db.delete(aluno)
    db.commit()

    return {"mensagem": "Aluno deletado com sucesso"}


# ROTAS DE CURSOS

@app.post("/cursos")
def criar_curso(curso: CursoCreate, db: Session = Depends(get_db)):
    novo = Curso(titulo=curso.titulo)

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return {
        "id": novo.id,
        "titulo": novo.titulo
    }


@app.get("/cursos")
def listar_cursos(db: Session = Depends(get_db)):
    cursos = db.query(Curso).all()

    return [
        {
            "id": c.id,
            "titulo": c.titulo
        }
        for c in cursos
    ]


@app.get("/cursos/{id}")
def buscar_curso(id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(Curso.id == id).first()

    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    return {
        "id": curso.id,
        "titulo": curso.titulo
    }


# ROTAS DE MATRÍCULAS

@app.post("/matriculas")
def criar_matricula(dados: MatriculaCreate, db: Session = Depends(get_db)):
    aluno = db.query(Aluno).filter(Aluno.id == dados.aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    curso = db.query(Curso).filter(Curso.id == dados.curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    matricula_existente = db.query(Matricula).filter(
        Matricula.aluno_id == dados.aluno_id,
        Matricula.curso_id == dados.curso_id
    ).first()

    if matricula_existente:
        raise HTTPException(status_code=400, detail="Aluno já matriculado neste curso")

    total_ativas = db.query(Matricula).filter(
        Matricula.aluno_id == dados.aluno_id,
        Matricula.status == "ativa"
    ).count()

    if total_ativas >= 5:
        raise HTTPException(status_code=400, detail="Aluno já possui 5 matrículas ativas")

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
def listar_matriculas(db: Session = Depends(get_db)):
    matriculas = db.query(Matricula).all()

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
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")

    matricula.status = "cancelada"
    db.commit()

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
        raise HTTPException(status_code=404, detail="Matrícula não encontrada")

    matricula.status = "concluida"
    db.commit()

    return {
        "id": matricula.id,
        "aluno_id": matricula.aluno_id,
        "curso_id": matricula.curso_id,
        "status": matricula.status
    }


@app.get("/alunos/{id}/cursos")
def listar_cursos_do_aluno(id: int, db: Session = Depends(get_db)):
    aluno = db.query(Aluno).filter(Aluno.id == id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    matriculas = db.query(Matricula).filter(Matricula.aluno_id == id).all()

    return [
        {
            "id_matricula": m.id,
            "curso_id": m.curso_id,
            "status": m.status
        }
        for m in matriculas
    ]


@app.get("/cursos/{id}/alunos")
def listar_alunos_do_curso(id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(Curso.id == id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    matriculas = db.query(Matricula).filter(Matricula.curso_id == id).all()

    return [
        {
            "id_matricula": m.id,
            "aluno_id": m.aluno_id,
            "status": m.status
        }
        for m in matriculas
    ]
