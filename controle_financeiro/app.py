from fastapi import FastAPI

from controle_financeiro.routers import auth, users

app = FastAPI(title='Controle Financeiro')

app.include_router(auth.router)
app.include_router(users.router)
