from pydantic import BaseModel, EmailStr, field_validator


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
