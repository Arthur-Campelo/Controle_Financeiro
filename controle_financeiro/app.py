from http import HTTPStatus

from fastapi import FastAPI

from controle_financeiro.schemas import Message, UserPublicSchema, UserPrivateSchema

app = FastAPI()

database= []  # Simulando um banco de dados com uma lista

@app.get(
    '/', status_code=HTTPStatus.OK, summary='Endpoint de teste', response_model=Message
)
def read_root():
    return {'message': 'Olá mundo!'}

@app.post(
    '/users',status_code=HTTPStatus.CREATED, summary='Criar um usário', response_model=UserPublicSchema
)
def create_user(user: UserPrivateSchema):
    user_with_id = {**user}
    database.append(user) 
    return user

@app.get(
    '/users',status_code=HTTPStatus.OK, summary='Listar usuários', response_model=list[UserPublicSchema]
)
def fetch_users():
    return database
