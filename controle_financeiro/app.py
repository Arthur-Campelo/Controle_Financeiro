from http import HTTPStatus

from fastapi import FastAPI

from controle_financeiro.routers import auth, users

app = FastAPI(title='Controle Financeiro')

app.include_router(auth.router)
app.include_router(users.router)


@app.get('/', status_code=HTTPStatus.OK)
def root_deve_retornar_ok_e_ola_mundo():
    return {'message': 'Olá Mundo!'}
