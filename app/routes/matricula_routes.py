from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MatriculaCreate
from app.services.matricula_service import (
    criar_matricula_service,
    listar_matriculas_service,
    cancelar_matricula_service,
    concluir_matricula_service,
    listar_cursos_do_aluno_service,
    listar_alunos_do_curso_service
)

router = APIRouter(tags=["Matrículas"])


@router.post("/matriculas")
def criar_matricula(dados: MatriculaCreate, db: Session = Depends(get_db)):
    return criar_matricula_service(dados, db)


@router.get("/matriculas")
def listar_matriculas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return listar_matriculas_service(skip, limit, db)


@router.put("/matriculas/{id}/cancelar")
def cancelar_matricula(id: int, db: Session = Depends(get_db)):
    return cancelar_matricula_service(id, db)


@router.put("/matriculas/{id}/concluir")
def concluir_matricula(id: int, db: Session = Depends(get_db)):
    return concluir_matricula_service(id, db)


@router.get("/alunos/{id}/cursos")
def listar_cursos_do_aluno(id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return listar_cursos_do_aluno_service(id, skip, limit, db)


@router.get("/cursos/{id}/alunos")
def listar_alunos_do_curso(id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return listar_alunos_do_curso_service(id, skip, limit, db)
