from sqlalchemy.orm import Session
from app.models import Aluno
from app.utils import erro
from app.schemas import AlunoCreate


def criar_aluno_service(aluno: AlunoCreate, db: Session):
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


def listar_alunos_service(skip: int, limit: int, db: Session):
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


def buscar_aluno_service(id: int, db: Session):
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


def atualizar_aluno_service(id: int, aluno: AlunoCreate, db: Session):
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


def deletar_aluno_service(id: int, db: Session):
    aluno = db.query(Aluno).filter(
        Aluno.id == id,
        Aluno.ativo == True
    ).first()

    if not aluno:
        erro(404, "Aluno não encontrado")

    aluno.ativo = False
    db.commit()

    return {"mensagem": "Aluno desativado com sucesso"}
