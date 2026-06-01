from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/padaria_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELOS DO BANCO ---

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha = Column(String, nullable=False)
    tipo_usuario = Column(String, nullable=False)
    telefone = Column(String, nullable=True)
    endereco_entrega = Column(String, nullable=True)

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0)

class Carrinho(Base):
    __tablename__ = "carrinhos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"), unique=True)
    itens = relationship("ItemCarrinho", back_populates="carrinho", cascade="all, delete-orphan")

class ItemCarrinho(Base):
    __tablename__ = "itens_carrinho"
    id = Column(Integer, primary_key=True, index=True)
    carrinho_id = Column(Integer, ForeignKey("carrinhos.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer, nullable=False)
    carrinho = relationship("Carrinho", back_populates="itens")
    produto = relationship("Produto")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    data_criacao = Column(DateTime, default=datetime.utcnow)
    valor_total = Column(Float, nullable=False)
    status = Column(String, default="Pendente")
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")
    pagamento = relationship("Pagamento", uselist=False, back_populates="pedido")

class ItemPedido(Base):
    __tablename__ = "itens_pedido"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")

class Pagamento(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), unique=True)
    metodo_pagamento = Column(String, nullable=False)
    status_pagamento = Column(String, default="Pendente")
    pedido = relationship("Pedido", back_populates="pagamento")

# --- ESQUEMAS ---

class ProdutoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float
    estoque: int

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str
    tipo_usuario: str
    telefone: Optional[str] = None
    endereco_entrega: Optional[str] = None

class ItemCarrinhoInput(BaseModel):
    produto_id: int
    quantidade: int

class FinalizarPedidoInput(BaseModel):
    cliente_id: int
    metodo_pagamento: str

class LoginInput(BaseModel):
    email: str
    senha: str

class UsuarioUpdate(BaseModel):
    nome: str
    email: str
    senha: str
    telefone: str
    endereco_entrega: str