from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AlunoCreate
from app.services.aluno_service import (
    criar_aluno_service,
    listar_alunos_service,
    buscar_aluno_service,
    atualizar_aluno_service,
    deletar_aluno_service
)

router = APIRouter(prefix="/alunos", tags=["Alunos"])


@router.post("")
def criar_aluno(aluno: AlunoCreate, db: Session = Depends(get_db)):
    return criar_aluno_service(aluno, db)


@router.get("")
def listar_alunos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return listar_alunos_service(skip, limit, db)


@router.get("/{id}")
def buscar_aluno(id: int, db: Session = Depends(get_db)):
    return buscar_aluno_service(id, db)


@router.put("/{id}")
def atualizar_aluno(id: int, aluno: AlunoCreate, db: Session = Depends(get_db)):
    return atualizar_aluno_service(id, aluno, db)


@router.delete("/{id}")
def deletar_aluno(id: int, db: Session = Depends(get_db)):
    return deletar_aluno_service(id, db)
