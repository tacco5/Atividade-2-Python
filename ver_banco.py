
from sqlalchemy import create_engine, text
from pathlib import Path

CAMINHO_BANCO = Path(__file__).with_name("usuarios.db")

engine = create_engine(
    f"sqlite:///{CAMINHO_BANCO.as_posix()}"
)
with engine.connect() as conexao:

    resultado = conexao.execute(
        text("SELECT * FROM usuarios")
    )

    print("\n====== USUÁRIOS CADASTRADOS ======\n")

    for usuario in resultado:
        print("ID:", usuario.id)
        print("Nome:", usuario.nome)
        print("Hash da senha:", usuario.senha_hash)
        print("--------------------------------")

