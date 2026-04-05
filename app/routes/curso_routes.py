from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CursoCreate
from app.services.curso_service import (
    criar_curso_service,
    listar_cursos_service,
    buscar_curso_service,
    deletar_curso_service
)

router = APIRouter(prefix="/cursos", tags=["Cursos"])


@router.post("")
def criar_curso(curso: CursoCreate, db: Session = Depends(get_db)):
    return criar_curso_service(curso, db)


@router.get("")
def listar_cursos(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return listar_cursos_service(skip, limit, db)


@router.get("/{id}")
def buscar_curso(id: int, db: Session = Depends(get_db)):
    return buscar_curso_service(id, db)


@router.delete("/{id}")
def deletar_curso(id: int, db: Session = Depends(get_db)):
    return deletar_curso_service(id, db)
