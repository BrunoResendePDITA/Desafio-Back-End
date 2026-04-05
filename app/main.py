from fastapi import FastAPI

from app.database import engine, Base
from app.routes.aluno_routes import router as aluno_router
from app.routes.curso_routes import router as curso_router
from app.routes.matricula_routes import router as matricula_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(aluno_router)
app.include_router(curso_router)
app.include_router(matricula_router)
