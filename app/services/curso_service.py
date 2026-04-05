from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Curso
from app.utils import erro
from app.schemas import CursoCreate


def criar_curso_service(curso: CursoCreate, db: Session):
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


def listar_cursos_service(skip: int, limit: int, db: Session):
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


def buscar_curso_service(id: int, db: Session):
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


def deletar_curso_service(id: int, db: Session):
    curso = db.query(Curso).filter(
        Curso.id == id,
        Curso.ativo == True
    ).first()

    if not curso:
        erro(404, "Curso não encontrado")

    curso.ativo = False
    db.commit()

    return {"mensagem": "Curso desativado com sucesso"}
