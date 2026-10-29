
import wx
import hashlib
import secrets

from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


# ==========================================
# CONFIGURAÇÃO DO BANCO DE DADOS
# ==========================================

CAMINHO_BANCO = Path(__file__).with_name("usuarios.db")

engine = create_engine(
    f"sqlite:///{CAMINHO_BANCO.as_posix()}",
    echo=False
)

Base = declarative_base()


# ==========================================
# TABELA DE USUÁRIOS
# ==========================================

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(64), nullable=False)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


# ==========================================
# FUNÇÕES DO SISTEMA
# ==========================================

def gerar_hash(senha):
    """Transforma a senha em hash."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def preparar_banco():
    """Cria um usuário de exemplo se ele não existir."""

    with Session() as sessao:

        usuario = sessao.query(Usuario).filter_by(
            nome="Fernando"
        ).first()

        if usuario is None:

            novo_usuario = Usuario(
                nome="Fernando",
                senha_hash=gerar_hash("1234")
            )

            sessao.add(novo_usuario)
            sessao.commit()


def verificar_usuario(usuario, senha):
    """Verifica se o usuário e a senha estão corretos."""

    with Session() as sessao:

        resultado = sessao.query(Usuario).filter_by(
            nome=usuario
        ).first()

        if resultado and secrets.compare_digest(
            resultado.senha_hash,
            gerar_hash(senha)
        ):
            return True

        return False


def atualizar_usuario(usuario_atual, novo_usuario, nova_senha):
    """Atualiza o nome e a senha no banco de dados."""

    with Session() as sessao:

        resultado = sessao.query(Usuario).filter_by(
            nome=usuario_atual
        ).first()

        if resultado is None:
            return "nao_encontrado"

        existente = sessao.query(Usuario).filter(
            Usuario.nome == novo_usuario,
            Usuario.id != resultado.id
        ).first()

        if existente:
            return "duplicado"

        resultado.nome = novo_usuario
        resultado.senha_hash = gerar_hash(nova_senha)

        sessao.commit()

        return True


# ==========================================
# JANELA PRINCIPAL - LOGIN
# ==========================================

class JanelaPrincipal(wx.Frame):

    def __init__(self):

        super().__init__(
            None,
            title="Sistema de Cadastro",
            size=(340, 370)
        )

        self.SetMinSize((340, 370))

        painel = wx.Panel(self)
        painel.SetBackgroundColour("#eeeeee")

        titulo = wx.StaticText(
            painel,
            label="Sistema de Cadastro"
        )

        titulo.SetFont(wx.Font(
            18,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL
        ))

        self.usuario = wx.TextCtrl(painel, size=(180, -1))

        self.senha = wx.TextCtrl(
            painel,
            style=wx.TE_PASSWORD,
            size=(180, -1)
        )

        entrar = wx.Button(
            painel,
            label="Entrar",
            size=(110, 36)
        )

        sair = wx.Button(
            painel,
            label="Sair",
            size=(110, 36)
        )

        redefinir = wx.Button(
            painel,
            label="Redefinir senha",
            style=wx.BORDER_NONE
        )

        grade = wx.FlexGridSizer(
            rows=2,
            cols=2,
            vgap=18,
            hgap=10
        )

        grade.Add(
            wx.StaticText(painel, label="Usuário:"),
            0,
            wx.ALIGN_CENTER_VERTICAL
        )

        grade.Add(self.usuario, 0)

        grade.Add(
            wx.StaticText(painel, label="Senha:"),
            0,
            wx.ALIGN_CENTER_VERTICAL
        )

        grade.Add(self.senha, 0)

        botoes = wx.BoxSizer(wx.HORIZONTAL)

        botoes.Add(entrar, 0, wx.RIGHT, 12)
        botoes.Add(sair, 0)

        layout = wx.BoxSizer(wx.VERTICAL)

        layout.Add(
            titulo,
            0,
            wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM,
            28
        )

        layout.Add(
            grade,
            0,
            wx.ALIGN_CENTER | wx.BOTTOM,
            28
        )

        layout.Add(
            botoes,
            0,
            wx.ALIGN_CENTER | wx.BOTTOM,
            6
        )

        layout.Add(
            redefinir,
            0,
            wx.ALIGN_CENTER
        )

        painel.SetSizer(layout)

        entrar.Bind(wx.EVT_BUTTON, self.fazer_login)

        sair.Bind(
            wx.EVT_BUTTON,
            lambda evento: self.Close()
        )

        redefinir.Bind(
            wx.EVT_BUTTON,
            self.abrir_redefinicao
        )

        self.Centre()
        self.Show()

    def fazer_login(self, evento):

        usuario = self.usuario.GetValue().strip()
        senha = self.senha.GetValue()

        if verificar_usuario(usuario, senha):

            self.Hide()

            janela = JanelaAcesso(self, usuario)
            janela.Show()

        else:

            wx.MessageBox(
                "Usuário ou senha incorretos.",
                "Falha no login",
                wx.OK | wx.ICON_ERROR
            )

    def abrir_redefinicao(self, evento):

        JanelaRedefinir(self).Show()


# ==========================================
# JANELA DE ACESSO AUTORIZADO
# ==========================================

class JanelaAcesso(wx.Frame):

    def __init__(self, janela_login, usuario):

        super().__init__(
            None,
            title="Área do sistema",
            size=(420, 280)
        )

        self.janela_login = janela_login

        painel = wx.Panel(self)
        painel.SetBackgroundColour("#eeeeee")

        titulo = wx.StaticText(
            painel,
            label="Acesso autorizado!"
        )

        titulo.SetFont(wx.Font(
            18,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD
        ))

        texto = wx.StaticText(
            painel,
            label=f"Bem-vindo(a), {usuario}!\n"
                  "Você entrou no sistema com sucesso."
        )

        voltar = wx.Button(
            painel,
            label="Voltar para o login"
        )

        sair = wx.Button(
            painel,
            label="Sair do programa"
        )

        layout = wx.BoxSizer(wx.VERTICAL)

        layout.Add(
            titulo,
            0,
            wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM,
            28
        )

        layout.Add(
            texto,
            0,
            wx.ALIGN_CENTER | wx.BOTTOM,
            28
        )

        layout.Add(
            voltar,
            0,
            wx.ALIGN_CENTER | wx.BOTTOM,
            8
        )

        layout.Add(
            sair,
            0,
            wx.ALIGN_CENTER
        )

        painel.SetSizer(layout)

        voltar.Bind(
            wx.EVT_BUTTON,
            self.voltar_login
        )

        sair.Bind(
            wx.EVT_BUTTON,
            lambda evento: self.Close()
        )

        self.Bind(wx.EVT_CLOSE, self.ao_fechar)

        self.Centre()

    def voltar_login(self, evento):

        self.janela_login.usuario.SetValue("")
        self.janela_login.senha.SetValue("")

        self.janela_login.Show()
        self.Destroy()

    def ao_fechar(self, evento):

        if self.janela_login:
            self.janela_login.Show()

        evento.Skip()


# ==========================================
# JANELA DE REDEFINIÇÃO DE USUÁRIO E SENHA
# ==========================================

class JanelaRedefinir(wx.Frame):

    def __init__(self, janela_login):

        super().__init__(
            janela_login,
            title="Redefinir usuário e senha",
            size=(430, 390)
        )

        painel = wx.Panel(self)
        painel.SetBackgroundColour("#eeeeee")

        titulo = wx.StaticText(
            painel,
            label="Redefinir usuário e senha"
        )

        titulo.SetFont(wx.Font(
            14,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL
        ))

        # Campos de preenchimento

        self.usuario = wx.TextCtrl(
            painel,
            size=(200, -1)
        )

        self.novo_usuario = wx.TextCtrl(
            painel,
            size=(200, -1)
        )

        self.senha = wx.TextCtrl(
            painel,
            style=wx.TE_PASSWORD,
            size=(200, -1)
        )

        self.confirmar = wx.TextCtrl(
            painel,
            style=wx.TE_PASSWORD,
            size=(200, -1)
        )

        # Organização dos campos

        grade = wx.FlexGridSizer(
            rows=4,
            cols=2,
            vgap=18,
            hgap=10
        )

        grade.Add(
            wx.StaticText(painel, label="Usuário atual:"),
            0,
            wx.ALIGN_CENTER_VERTICAL
        )

        grade.Add(self.usuario, 0)

        grade.Add(
            wx.StaticText(painel, label="Novo usuário:"),
            0,
            wx.ALIGN_CENTER_VERTICAL
        )

        grade.Add(self.novo_usuario, 0)

        grade.Add(
            wx.StaticText(painel, label="Nova senha:"),
            0,
            wx.ALIGN_CENTER_VERTICAL
        )

        grade.Add(self.senha, 0)

        grade.Add(
            wx.StaticText(painel, label="Confirme a senha:"),
            0,
            wx.ALIGN_CENTER_VERTICAL
        )

        grade.Add(self.confirmar, 0)

        # Botões

        salvar = wx.Button(
            painel,
            label="Salvar alterações"
        )

        cancelar = wx.Button(
            painel,
            label="Cancelar"
        )

        botoes = wx.BoxSizer(wx.HORIZONTAL)

        botoes.Add(salvar, 0, wx.RIGHT, 10)
        botoes.Add(cancelar, 0)

        # Layout da janela

        layout = wx.BoxSizer(wx.VERTICAL)

        layout.Add(
            titulo,
            0,
            wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM,
            24
        )

        layout.Add(
            grade,
            0,
            wx.ALIGN_CENTER | wx.BOTTOM,
            24
        )

        layout.Add(
            botoes,
            0,
            wx.ALIGN_CENTER
        )

        painel.SetSizer(layout)

        salvar.Bind(
            wx.EVT_BUTTON,
            self.salvar_nova_senha
        )

        cancelar.Bind(
            wx.EVT_BUTTON,
            lambda evento: self.Close()
        )

        self.Centre()

    def salvar_nova_senha(self, evento):

        usuario_atual = self.usuario.GetValue().strip()
        novo_usuario = self.novo_usuario.GetValue().strip()
        senha = self.senha.GetValue()
        confirmar = self.confirmar.GetValue()

        # Verifica os campos vazios

        if not usuario_atual or not novo_usuario or not senha or not confirmar:

            wx.MessageBox(
                "Preencha todos os campos.",
                "Atenção",
                wx.OK | wx.ICON_WARNING
            )

            return

        # Verifica se as senhas são iguais

        if senha != confirmar:

            wx.MessageBox(
                "As senhas não são iguais.",
                "Atenção",
                wx.OK | wx.ICON_WARNING
            )

            return

        # Atualiza os dados no banco

        resultado = atualizar_usuario(
            usuario_atual,
            novo_usuario,
            senha
        )

        if resultado == "nao_encontrado":

            wx.MessageBox(
                "O usuário atual não existe. Confira o nome informado.",
                "Usuário não encontrado",
                wx.OK | wx.ICON_ERROR
            )

            return

        if resultado == "duplicado":

            wx.MessageBox(
                "Esse novo nome de usuário já está cadastrado.",
                "Usuário existente",
                wx.OK | wx.ICON_WARNING
            )

            return

        # Confirma a atualização

        wx.MessageBox(
            "Nome de usuário e senha alterados com sucesso!",
            "Concluído",
            wx.OK | wx.ICON_INFORMATION
        )

        self.Close()


# ==========================================
# INICIALIZAÇÃO DO PROGRAMA
# ==========================================

if __name__ == "__main__":

    preparar_banco()

    app = wx.App(False)

    janela = JanelaPrincipal()

    app.MainLoop()
