from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import SessionLocal, engine, Base
from models import ProdutoCreate, UsuarioCreate, FinalizarPedidoInput, ItemCarrinhoInput, LoginInput, UsuarioUpdate
import use_cases

app = FastAPI(title="API da Padaria")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria as tabelas se não existirem
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROTAS DE USUÁRIO ---
@app.post("/usuarios/", status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return use_cases.cadastrar_usuario_uc(usuario, db)

@app.post("/login/")
def fazer_login(dados: LoginInput, db: Session = Depends(get_db)):
    return use_cases.autenticar_usuario_uc(dados, db)

@app.put("/usuarios/{id}")
def editar_usuario(id: int, dados: UsuarioUpdate, db: Session = Depends(get_db)):
    return use_cases.editar_usuario_uc(id, dados, db)

# --- ROTAS DE PRODUTO ---
@app.get("/produtos/")
def listar_produtos(db: Session = Depends(get_db)):
    return use_cases.listar_produtos_uc(db)

@app.post("/produtos/", status_code=status.HTTP_201_CREATED)
def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db)):
    return use_cases.adicionar_produto_uc(produto, db)

@app.get("/produtos/{id}")
def buscar_produto(id: int, db: Session = Depends(get_db)):
    return use_cases.buscar_produto_uc(id, db)

# --- ROTAS DE PEDIDO ---
@app.post("/pedidos/finalizar", status_code=status.HTTP_201_CREATED)
def finalizar_pedido(dados: FinalizarPedidoInput, db: Session = Depends(get_db)):
    return use_cases.finalizar_pedido_uc(dados, db)

@app.put("/produtos/{id}")
def editar_produto(id: int, produto_atualizado: ProdutoCreate, db: Session = Depends(get_db)):
    return use_cases.editar_produto_uc(id, produto_atualizado, db)

@app.delete("/produtos/{id}")
def deletar_produto(id: int, db: Session = Depends(get_db)):
    return use_cases.deletar_produto_uc(id, db)

# --- ROTAS DE CARRINHO E HISTÓRICO ---
@app.post("/carrinho/{cliente_id}/adicionar")
def adicionar_item_carrinho(cliente_id: int, item_in: ItemCarrinhoInput, db: Session = Depends(get_db)):
    return use_cases.adicionar_item_carrinho_uc(cliente_id, item_in, db)

@app.get("/pedidos/{cliente_id}/historico")
def visualizar_historico(cliente_id: int, db: Session = Depends(get_db)):
    return use_cases.visualizar_historico_uc(cliente_id, db)

@app.get("/carrinho/{cliente_id}")
def ver_carrinho(cliente_id: int, db: Session = Depends(get_db)):
    return use_cases.ver_carrinho_uc(cliente_id, db)

@app.delete("/carrinho/item/{item_id}")
def remover_item(item_id: int, db: Session = Depends(get_db)):
    return use_cases.remover_item_carrinho_uc(item_id, db)

@app.delete("/carrinho/{cliente_id}/limpar")
def limpar_carrinho(cliente_id: int, db: Session = Depends(get_db)):
    return use_cases.limpar_carrinho_uc(cliente_id, db)