from fastapi import FastAPI, Response
from fastapi import Depends
from fastapi_asyncpg import configure_asyncpg
from pydantic import BaseModel

app = FastAPI()
#db = configure_asyncpg(app, "postgresql://admin:123@192.168.0.10/rinha")
db = configure_asyncpg(app, "postgresql://admin:123@db/rinha")

@db.on_init
async def initialization(conn):
    # you can run your db initialization code here
    await conn.execute("SELECT 1")

class TransacaoRequest(BaseModel):
     valor: int
     tipo: str
     descricao: str

limites_clientes = [100000, 80000, 1000000, 10000000, 500000]
def obter_cliente_limite(id: int):
    return limites_clientes[id - 1]

def is_cliente_invalido(id: int):
    return id < 1 or id > 5

def is_transacao_invalida(transacao: TransacaoRequest):
    return (transacao.valor <= 0 \
            or len(transacao.descricao) == 0 or len(transacao.descricao) > 10 \
            or (transacao.tipo != "c" and transacao.tipo != "d"));

def obter_nome_funcao_transacao(tipo: str) -> str:
    if tipo == "d":
        return "inserir_transacao_debito_e_retornar_saldo"
    return "inserir_transacao_credito_e_retornar_saldo"

@app.get("/clientes/{id}/extrato")
async def extrato(id: int, response: Response, db=Depends(db.connection)):
    if is_cliente_invalido(id):
        response.status_code = 404
        return {}

    row_saldo = await db.fetch('SELECT saldo as total, now() as data_extrato, limite FROM clientes WHERE id = $1',  id)
    row_transacoes = await db.fetch('SELECT valor, tipo, descricao, realizada_em FROM transacoes WHERE cliente_id = $1 ORDER BY realizada_em DESC LIMIT 10', id)
    
    #response.status_code = 200
    return {
        "saldo": row_saldo[0],
        "ultimas_transacoes": [dict(r) for r in row_transacoes]
    } 

@app.post("/clientes/{id}/transacoes")
async def transacoes(id: int, response: Response, transacaoRequest: TransacaoRequest, db=Depends(db.connection)):
    if is_cliente_invalido(id):
        response.status_code = 404
        return {}
    
    if is_transacao_invalida(transacaoRequest):
        response.status_code = 422
        return {}
    
    nome_funcao = obter_nome_funcao_transacao(transacaoRequest.tipo)
    row_saldo = await db.fetch(f'SELECT {nome_funcao} ($1, $2, $3) as saldo', id, transacaoRequest.valor, transacaoRequest.descricao)
    
    saldo = row_saldo[0]['saldo']
    if (saldo == None):
        response.status_code = 422
        return {}
    
    return {
        "limite": obter_cliente_limite(id),
        "saldo": saldo
    }
