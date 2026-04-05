from sqlalchemy.orm import Session
from app.models import Aluno, Curso, Matricula
from app.utils import erro
from app.schemas import MatriculaCreate


def criar_matricula_service(dados: MatriculaCreate, db: Session):
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


def listar_matriculas_service(skip: int, limit: int, db: Session):
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


def cancelar_matricula_service(id: int, db: Session):
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


def concluir_matricula_service(id: int, db: Session):
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


def listar_cursos_do_aluno_service(id: int, skip: int, limit: int, db: Session):
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


def listar_alunos_do_curso_service(id: int, skip: int, limit: int, db: Session):
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
