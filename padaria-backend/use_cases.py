from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Usuario, Produto, Carrinho, ItemCarrinho, Pedido, ItemPedido, Pagamento
from models import UsuarioCreate, ProdutoCreate, ItemCarrinhoInput, FinalizarPedidoInput, LoginInput, UsuarioUpdate

def cadastrar_usuario_uc(usuario: UsuarioCreate, db: Session):
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    
    novo_usuario = Usuario(**usuario.dict())
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    
    if novo_usuario.tipo_usuario.lower() == "cliente":
        db.add(Carrinho(cliente_id=novo_usuario.id))
        db.commit()
        
    return novo_usuario

def listar_produtos_uc(db: Session):
    return db.query(Produto).all()

def adicionar_produto_uc(produto: ProdutoCreate, db: Session):
    novo = Produto(**produto.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

def finalizar_pedido_uc(dados: FinalizarPedidoInput, db: Session):
    carrinho = db.query(Carrinho).filter(Carrinho.cliente_id == dados.cliente_id).first()
    if not carrinho or not carrinho.itens:
        raise HTTPException(status_code=400, detail="O carrinho está vazio")
    
    valor_total = 0.0
    itens_para_criar = []
    
    for item in carrinho.itens:
        if item.produto.estoque < item.quantidade:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente para: {item.produto.nome}")
        
        valor_total += (item.quantidade * item.produto.preco)
        item.produto.estoque -= item.quantidade
        
        itens_para_criar.append({
            "produto_id": item.produto_id,
            "quantidade": item.quantidade,
            "preco_unitario": item.produto.preco
        })
    
    novo_pedido = Pedido(cliente_id=dados.cliente_id, valor_total=valor_total, status="Pendente")
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)
    
    for item_dados in itens_para_criar:
        db.add(ItemPedido(pedido_id=novo_pedido.id, **item_dados))
        
    db.add(Pagamento(pedido_id=novo_pedido.id, metodo_pagamento=dados.metodo_pagamento))
    db.query(ItemCarrinho).filter(ItemCarrinho.carrinho_id == carrinho.id).delete()
    
    db.commit()
    db.refresh(novo_pedido)
    return novo_pedido

def editar_produto_uc(id: int, produto_atualizado: ProdutoCreate, db: Session):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    for key, value in produto_atualizado.dict().items():
        setattr(produto, key, value)
    db.commit()
    db.refresh(produto)
    return produto

def deletar_produto_uc(id: int, db: Session):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()
    return {"detail": "Produto removido com sucesso"}

def adicionar_item_carrinho_uc(cliente_id: int, item_in: ItemCarrinhoInput, db: Session):
    carrinho = db.query(Carrinho).filter(Carrinho.cliente_id == cliente_id).first()
    if not carrinho:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado para este cliente")
    
    produto = db.query(Produto).filter(Produto.id == item_in.produto_id).first()
    if not produto or produto.estoque < item_in.quantidade:
        raise HTTPException(status_code=400, detail="Produto indisponível ou estoque insuficiente")
    
    item_existente = db.query(ItemCarrinho).filter(
        ItemCarrinho.carrinho_id == carrinho.id, 
        ItemCarrinho.produto_id == item_in.produto_id
    ).first()
    
    if item_existente:
        item_existente.quantidade += item_in.quantidade
    else:
        novo_item = ItemCarrinho(carrinho_id=carrinho.id, produto_id=item_in.produto_id, quantidade=item_in.quantidade)
        db.add(novo_item)
        
    db.commit()
    return {"detail": "Produto adicionado ao carrinho"}

def visualizar_historico_uc(cliente_id: int, db: Session):
    pedidos = db.query(Pedido).filter(Pedido.cliente_id == cliente_id).order_by(Pedido.data_criacao.desc()).all()
    
    historico_formatado = []
    for pedido in pedidos:
        itens_formatados = []
        for item in pedido.itens:
            itens_formatados.append({
                "nome_produto": item.produto.nome,
                "quantidade": item.quantidade,
                "preco_unitario": item.preco_unitario
            })
            
        historico_formatado.append({
            "pedido_id": pedido.id,
            "data": pedido.data_criacao.strftime("%d/%m/%Y às %H:%M"),
            "valor_total": pedido.valor_total,
            "status": pedido.status,
            "metodo_pagamento": pedido.pagamento.metodo_pagamento if pedido.pagamento else "Não informado",
            "itens": itens_formatados
        })
        
    return historico_formatado

def buscar_produto_uc(id: int, db: Session):
    produto = db.query(Produto).filter(Produto.id == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

def autenticar_usuario_uc(dados: LoginInput, db: Session):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email, Usuario.senha == dados.senha).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    
    return {
        "id": usuario.id, 
        "nome": usuario.nome, 
        "tipo_usuario": usuario.tipo_usuario,
        "telefone": usuario.telefone,
        "endereco_entrega": usuario.endereco_entrega
    }

def ver_carrinho_uc(cliente_id: int, db: Session):
    carrinho = db.query(Carrinho).filter(Carrinho.cliente_id == cliente_id).first()
    if not carrinho:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")
    
    itens_formatados = []
    for item in carrinho.itens:
        itens_formatados.append({
            "id": item.id,
            "produto_id": item.produto_id,
            "nome_produto": item.produto.nome,
            "preco_unitario": item.produto.preco,
            "quantidade": item.quantidade,
            "subtotal": item.quantidade * item.produto.preco
        })
        
    return {"carrinho_id": carrinho.id, "itens": itens_formatados}

def editar_usuario_uc(id: int, dados: UsuarioUpdate, db: Session):
    usuario = db.query(Usuario).filter(Usuario.id == id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    usuario.nome = dados.nome
    usuario.email = dados.email
    usuario.senha = dados.senha
    usuario.telefone = dados.telefone
    usuario.endereco_entrega = dados.endereco_entrega
    
    db.commit()
    db.refresh(usuario)
    
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "tipo_usuario": usuario.tipo_usuario,
        "telefone": usuario.telefone,
        "endereco_entrega": usuario.endereco_entrega
    }

def remover_item_carrinho_uc(item_id: int, db: Session):
    item = db.query(ItemCarrinho).filter(ItemCarrinho.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado no carrinho")
    
    db.delete(item)
    db.commit()
    return {"mensagem": "Item removido com sucesso"}

def limpar_carrinho_uc(cliente_id: int, db: Session):
    carrinho = db.query(Carrinho).filter(Carrinho.cliente_id == cliente_id).first()
    if not carrinho:
        raise HTTPException(status_code=404, detail="Carrinho não encontrado")
    
    db.query(ItemCarrinho).filter(ItemCarrinho.carrinho_id == carrinho.id).delete()
    db.commit()
    return {"mensagem": "Carrinho esvaziado com sucesso"}