from fastapi import FastAPI, Response
from fastapi import Depends
from fastapi.responses import PlainTextResponse
from fastapi_asyncpg import configure_asyncpg
import asyncpg

app = FastAPI()
db = configure_asyncpg(app, "postgresql://admin:123@192.168.0.10/rinha", )

@db.on_init
async def initialization(conn):
    # you can run your db initialization code here
    await conn.execute("SELECT 1")

limites_clientes = [100000, 80000, 1000000, 10000000, 500000]
def get_cliente_limite(id: int):
    limites_clientes[id - 1]

@app.get("/clientes/{id}/extrato")
async def extrato(id: int, response: Response, db=Depends(db.connection)):
    if (id < 1 or id > 5):
        response.status_code = 404
        return {}

    row_saldo = await db.fetch('SELECT saldo as total, now() as data_extrato, limite FROM clientes WHERE id = $1',  id)
    row_transacoes = await db.fetch('SELECT valor, tipo, descricao, realizada_em FROM transacoes WHERE cliente_id = $1 ORDER BY realizada_em DESC LIMIT 10', id)
    
    response.status_code = 200
    return {
        "saldo": row_saldo[0],
        "ultimas_transacoes": [dict(r) for r in row_transacoes]        
    } 

