import os
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

from src.negocio.produtos_service import ProdutoService
from src.negocio.fornecedoress_service import FornecedoresService
from src.negocio.telefones_forn_service import TelefoneService
from src.negocio.movimentacoess_service import MovimentacoesService

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")


class SistemaGUI:

    def __init__(self, servico_produto, servico_fornecedor, servico_telefone, servico_movimentacao):
        self.servico_produto = servico_produto
        self.servico_fornecedor = servico_fornecedor
        self.servico_telefone = servico_telefone
        self.servico_movimentacao = servico_movimentacao

        self.root = tk.Tk()
        self.root.title("Imperial Rango - Sistema de Estoque")
        self.root.geometry("1000x640")
        self.root.configure(bg="#f0f0f0")

        # Carrega imagens do logo (topo e marca d'água da tela inicial)
        self._img_logo_topo = None
        self._img_logo_grande = None
        self._img_logo_watermark = None
        try:
            self._img_logo_topo = ImageTk.PhotoImage(
                Image.open(os.path.join(_ASSETS_DIR, "logo_topo.png")))
            self._img_logo_grande = ImageTk.PhotoImage(
                Image.open(os.path.join(_ASSETS_DIR, "logo_fundo.png")).resize((420, 280)))
            self._img_logo_watermark = ImageTk.PhotoImage(
                Image.open(os.path.join(_ASSETS_DIR, "logo_watermark.png")))
        except Exception:
            pass

        self._entidade_atual = None
        self._flash = None
        self._build_layout()
        self._mostrar_boas_vindas()

    # ── Layout ─────────────────────────────────────────────────────
    def _build_layout(self):
        BAR_BG = "#1a4f8a"   # azul mais claro que o original #0d2c54
        BTN_BG = "#2563a8"   # botões de navegação ligeiramente mais claros que a barra

        self.top_bar = tk.Frame(self.root, bg=BAR_BG, height=70)
        self.top_bar.pack(side=tk.TOP, fill=tk.X)
        self.top_bar.pack_propagate(False)

        if self._img_logo_topo:
            tk.Label(self.top_bar, image=self._img_logo_topo,
                     bg=BAR_BG).pack(side=tk.LEFT, padx=(12, 16), pady=8)
        else:
            tk.Label(self.top_bar, text="Imperial Rango", bg=BAR_BG,
                     fg="white", font=("Arial", 13, "bold")).pack(side=tk.LEFT, padx=15)

        for label, ent in [
            ("Produto",        "Produto"),
            ("Fornecedor",     "Fornecedor"),
            ("Telefone Forn.", "Telefone"),
            ("Movimentações",  "Movimentacao"),
        ]:
            tk.Button(self.top_bar, text=label, bg=BTN_BG, fg="white",
                      relief=tk.FLAT, padx=12, pady=8, cursor="hand2",
                      activebackground="#f6a800", activeforeground="#0d2c54",
                      font=("Arial", 10),
                      command=lambda e=ent: self._selecionar_entidade(e)
                      ).pack(side=tk.LEFT, padx=2, pady=5)

        # Botão Início no canto direito da barra superior
        tk.Button(self.top_bar, text="🏠 Início", bg="#c1272d", fg="white",
                  relief=tk.FLAT, padx=12, pady=8, cursor="hand2",
                  activebackground="#f6a800", activeforeground="#0d2c54",
                  font=("Arial", 10, "bold"),
                  command=self._voltar_inicio
                  ).pack(side=tk.RIGHT, padx=10, pady=5)

        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.content = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Sidebar esquerda
        self.sidebar = tk.Frame(self.main_frame, bg="#ecf0f1", width=155)
        self.sidebar_label = tk.Label(self.sidebar, text="", bg="#2c3e50", fg="white",
                                      font=("Arial", 11, "bold"), pady=8)
        self.sidebar_label.pack(fill=tk.X)
        self.sidebar_buttons = []

    def _mostrar_sidebar(self, entidade):
        for b in self.sidebar_buttons:
            b.destroy()
        self.sidebar_buttons = []

        self.sidebar_label.config(text=entidade)

        acoes = [
            ("📋 Cadastrar", lambda: self.formulario(entidade, "Cadastrar")),
            ("📄 Listar",    lambda: self.listar(entidade)),
        ]

        if entidade == "Movimentacao":
            acoes.append(("🔍 Buscar por Tipo", lambda: self.buscar_por_nome(entidade)))
        else:
            acoes.append(("🔍 Buscar por Nome", lambda: self.buscar_por_nome(entidade)))

        for label, cmd in acoes:
            b = tk.Button(self.sidebar, text=label, width=18, anchor="w",
                          bg="#dfe6e9", fg="#0d2c54", relief=tk.FLAT,
                          font=("Arial", 10), cursor="hand2", pady=8, padx=6,
                          activebackground="#f6a800", activeforeground="#0d2c54",
                          command=cmd)
            b.pack(fill=tk.X, padx=8, pady=3)
            self.sidebar_buttons.append(b)

        # Separador visual antes do botão de voltar
        sep = tk.Frame(self.sidebar, bg="#bdc3c7", height=2)
        sep.pack(fill=tk.X, padx=8, pady=(12, 6))
        self.sidebar_buttons.append(sep)

        b_voltar = tk.Button(self.sidebar, text="← Tela Inicial", width=18, anchor="w",
                              bg="#c1272d", fg="white", relief=tk.FLAT,
                              font=("Arial", 10, "bold"), cursor="hand2", pady=8, padx=6,
                              activebackground="#f6a800", activeforeground="#0d2c54",
                              command=self._voltar_inicio)
        b_voltar.pack(fill=tk.X, padx=8, pady=3)
        self.sidebar_buttons.append(b_voltar)

        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

    def _limpar_conteudo(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _fundo_marca_dagua(self, parent=None):
        """Coloca o logo semitransparente centralizado atrás do conteúdo."""
        if parent is None:
            parent = self.content
        if self._img_logo_watermark:
            lbl = tk.Label(parent, image=self._img_logo_watermark, bg="#f0f0f0")
            lbl.place(relx=0.5, rely=0.5, anchor="center")
            lbl.lower()
            return lbl
        return None

    def _selecionar_entidade(self, entidade):
        self._entidade_atual = entidade
        self._mostrar_sidebar(entidade)
        self._tela_inicial_entidade(entidade)

    def _voltar_inicio(self):
        self.sidebar.pack_forget()
        self._entidade_atual = None
        self._limpar_conteudo()
        self._mostrar_boas_vindas()

    def _mostrar_boas_vindas(self):
        wrapper = tk.Frame(self.content, bg="#f0f0f0")
        wrapper.pack(expand=True)
        if self._img_logo_grande:
            tk.Label(wrapper, image=self._img_logo_grande, bg="#f0f0f0").pack(pady=(40, 10))
        tk.Label(wrapper,
                 text="Bem-vindo ao Sistema de Estoque\n\nSelecione uma categoria no menu superior.",
                 font=("Arial", 14), bg="#f0f0f0", fg="#0d2c54",
                 justify=tk.CENTER).pack(pady=10)

    # ── Formulário de Cadastro/Atualização ─────────────────────────
    def formulario(self, entidade, operacao, dados_iniciais=None):
        self._limpar_conteudo()
        self._btn_voltar()
        self._fundo_marca_dagua()

        tk.Label(self.content, text=f"{operacao} {entidade}",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=(8, 4))

        # Linha separadora visual abaixo do título
        tk.Frame(self.content, bg="#c8d6e5", height=1).pack(fill=tk.X, padx=30, pady=(0, 8))

        # Frame externo que ocupa o espaço mas ancora o conteúdo ao topo
        outer = tk.Frame(self.content, bg="#f0f0f0")
        outer.pack(fill=tk.BOTH, expand=True, anchor="n")

        # Frame central com largura fixa para manter campos e botões alinhados
        centro = tk.Frame(outer, bg="#f0f0f0")
        centro.pack(anchor="n", pady=4)

        # Campos exibidos: IDs de FK aparecem apenas no Atualizar (vêm de dados_iniciais["_id"]),
        # no Cadastrar os IDs de FK também são digitados pelo usuário (chave estrangeira, não PK)
        # A PK (id_produto, id_fornecedor etc.) nunca é exibida — o banco gera automaticamente
        campos_map_cadastrar = {
            "Produto":      ["Nome Fornecedor", "Nome", "Preço", "Quantidade", "Data Cadastro", "Data Validade"],
            "Fornecedor":   ["Nome", "Tipo", "Telefone Fornecedor", "Email", "Cidade", "Estado", "Data Cadastro"],
            "Telefone":     ["Nome Fornecedor", "Número"],
            "Movimentacao": ["Nome Produto", "Tipo Movimentação", "Quantidade", "Data Movimentação"],
        }
        campos_map_atualizar = {
            "Produto":      ["Nome Fornecedor", "Nome", "Preço", "Quantidade", "Data Cadastro", "Data Validade"],
            "Fornecedor":   ["Nome", "Tipo", "Telefone Fornecedor", "Email", "Cidade", "Estado", "Data Cadastro"],
            "Telefone":     ["Nome Fornecedor", "Número"],
            "Movimentacao": ["Nome Produto", "Tipo Movimentação", "Quantidade", "Data Movimentação"],
        }
        campos_map = campos_map_atualizar if operacao == "Atualizar" else campos_map_cadastrar

        campos = campos_map.get(entidade, [])
        self.entries = {}

        # Dicas exibidas ao lado do label para campos de tipo livre
        dicas_map = {
            "Fornecedor":   {"Tipo": "pessoa ou empresa"},
            "Movimentacao": {"Tipo Movimentação": "entrada ou saida"},
        }
        dicas_campo = dicas_map.get(entidade, {})

        # Determina o tipo atual do fornecedor (para saber qual campo doc exibir)
        tipo_confirmado = None
        if entidade == "Fornecedor" and dados_iniciais:
            tipo_confirmado = dados_iniciais.get("Tipo", "").strip().lower()
            if tipo_confirmado not in ("pessoa", "empresa"):
                tipo_confirmado = None

        # Um único form_frame com grid — garante alinhamento de todas as linhas
        form_frame = tk.Frame(centro, bg="#f0f0f0")
        form_frame.pack(pady=2)
        form_frame.columnconfigure(0, minsize=190)
        form_frame.columnconfigure(1, minsize=280)

        linha = 0

        # Callback confirmar tipo — definido aqui para ficar disponível no loop
        def _confirmar_tipo(ent=entidade, op=operacao):
            novos_dados = {}
            for nome_campo, widget in self.entries.items():
                if widget is None:
                    continue
                novos_dados[nome_campo] = widget.get()
            if dados_iniciais and "_id" in dados_iniciais:
                novos_dados["_id"] = dados_iniciais["_id"]
            self.formulario(ent, op, dados_iniciais=novos_dados)

        for campo in campos:
            dica = dicas_campo.get(campo, "")
            label_texto = f"{campo} ({dica}):" if dica else f"{campo}:"
            tk.Label(form_frame, text=label_texto, anchor="e",
                     bg="#f0f0f0", font=("Arial", 10)).grid(
                         row=linha, column=0, sticky="e", padx=(0, 8), pady=3)
            e = tk.Entry(form_frame, width=32, font=("Arial", 10))
            e.grid(row=linha, column=1, sticky="w", pady=3)
            if dados_iniciais and campo in dados_iniciais:
                val = dados_iniciais[campo]
                e.insert(0, str(val) if val is not None else "")
            self.entries[campo] = e

            # Botão Confirmar ao lado do campo Tipo
            if entidade == "Fornecedor" and campo == "Tipo":
                tk.Button(form_frame, text="Confirmar", bg="#7f8c8d", fg="white",
                          font=("Arial", 9), padx=8, pady=2, relief=tk.FLAT,
                          cursor="hand2", command=_confirmar_tipo).grid(
                              row=linha, column=2, sticky="w", padx=(6, 0))
            linha += 1

            # CPF ou CNPJ logo após o Tipo, dentro do mesmo grid
            if entidade == "Fornecedor" and campo == "Tipo" and tipo_confirmado in ("pessoa", "empresa"):
                doc_label = "CPF:" if tipo_confirmado == "pessoa" else "CNPJ:"
                doc_key   = "CPF"  if tipo_confirmado == "pessoa" else "CNPJ"
                outro_key = "CNPJ" if tipo_confirmado == "pessoa" else "CPF"
                tk.Label(form_frame, text=doc_label, anchor="e",
                         bg="#f0f0f0", font=("Arial", 10)).grid(
                             row=linha, column=0, sticky="e", padx=(0, 8), pady=3)
                e_doc = tk.Entry(form_frame, width=32, font=("Arial", 10))
                e_doc.grid(row=linha, column=1, sticky="w", pady=3)
                if dados_iniciais and doc_key in dados_iniciais:
                    e_doc.insert(0, str(dados_iniciais[doc_key] or ""))
                self.entries[doc_key]   = e_doc
                self.entries[outro_key] = None
                linha += 1

        tk.Frame(centro, bg="#c8d6e5", height=1).pack(fill=tk.X, padx=10, pady=(8, 4))

        # Botões centralizados abaixo do form, alinhados com o bloco de campos
        botoes = tk.Frame(centro, bg="#f0f0f0")
        botoes.pack(pady=(4, 6))
        tk.Button(botoes, text="✔  Salvar", bg="#27ae60", fg="white",
                  font=("Arial", 11, "bold"), padx=22, pady=6, relief=tk.FLAT,
                  cursor="hand2",
                  command=lambda: self._executar_operacao(entidade, operacao, dados_iniciais)).pack(side=tk.LEFT, padx=8)
        tk.Button(botoes, text="✖  Limpar", bg="#95a5a6", fg="white",
                  font=("Arial", 11), padx=22, pady=6, relief=tk.FLAT,
                  cursor="hand2",
                  command=lambda: self.formulario(entidade, operacao,
                      dados_iniciais={"_id": dados_iniciais["_id"]} if dados_iniciais and "_id" in dados_iniciais else None)
                  ).pack(side=tk.LEFT, padx=8)

        self._erro_label = tk.Label(centro, text="", bg="#f0f0f0",
                                     fg="#e74c3c", font=("Arial", 10, "bold"))
        self._erro_label.pack(pady=(2, 6))

    def _executar_operacao(self, entidade, operacao, dados_iniciais=None):
        try:
            if entidade == "Produto":
                self._operacao_produto(operacao, dados_iniciais)
            elif entidade == "Fornecedor":
                self._operacao_fornecedor(operacao, dados_iniciais)
            elif entidade == "Telefone":
                self._operacao_telefone(operacao, dados_iniciais)
            elif entidade == "Movimentacao":
                self._operacao_movimentacao(operacao, dados_iniciais)
        except ValueError as e:
            self._erro_label.config(text=str(e))
        except Exception as e:
            self._erro_label.config(text=str(e))

    def _tela_inicial_entidade(self, entidade=None):
        if entidade is None:
            entidade = self._entidade_atual
        self._limpar_conteudo()
        self._fundo_marca_dagua()
        if self._flash:
            cor = "#27ae60" if self._flash[0] == "ok" else "#e74c3c"
            tk.Label(self.content, text=self._flash[1], bg="#f0f0f0",
                     fg=cor, font=("Arial", 11, "bold")).pack(pady=(10, 0))
            self._flash = None
        tk.Label(self.content,
                 text=f"Selecione uma operação para {entidade}",
                 font=("Arial", 14), bg="#f0f0f0", fg="#555").pack(pady=20)

    def _btn_voltar(self):
        """Adiciona botão Voltar no topo do content."""
        tk.Button(self.content, text="← Voltar", bg="#16407a", fg="white",
                  font=("Arial", 10), padx=10, pady=4, relief=tk.FLAT,
                  cursor="hand2",
                  command=lambda: self._tela_inicial_entidade()
                  ).pack(anchor="nw", padx=10, pady=(8, 0))

    def _operacao_produto(self, operacao, dados_iniciais=None):
        e = self.entries

        # Resolver nome do fornecedor → id_fornecedor
        nome_forn = e["Nome Fornecedor"].get().strip()
        id_fornecedor = None
        if nome_forn:
            try:
                todos_forn = self.servico_fornecedor.listar_fornecedores()
                encontrados = [f for f in todos_forn if f.nome.lower() == nome_forn.lower()]
                if not encontrados:
                    raise ValueError(f"Fornecedor '{nome_forn}' não encontrado.")
                if len(encontrados) > 1:
                    raise ValueError(f"Mais de um fornecedor com o nome '{nome_forn}'. Use um nome único.")
                id_fornecedor = encontrados[0].id_fornecedor
            except ValueError:
                raise
            except Exception as ex:
                raise ValueError(f"Erro ao buscar fornecedor: {ex}")

        if operacao == "Cadastrar":
            self.servico_produto.cadastrar_produto(
                id_fornecedor=id_fornecedor,
                nome=e["Nome"].get(), preco=float(e["Preço"].get()),
                quantidade=int(e["Quantidade"].get()),
                data_cadastro=e["Data Cadastro"].get(), data_validade=e["Data Validade"].get())
            self._flash = ("ok", "Produto cadastrado com sucesso!")
            self._tela_inicial_entidade("Produto")
        elif operacao == "Atualizar":
            self.servico_produto.atualizar_produto(
                id_produto=dados_iniciais["_id"],
                id_fornecedor=id_fornecedor,
                nome=e["Nome"].get(), preco=float(e["Preço"].get()),
                quantidade=int(e["Quantidade"].get()),
                data_cadastro=e["Data Cadastro"].get(), data_validade=e["Data Validade"].get())
            self._flash = ("ok", "Produto atualizado com sucesso!")
            self._tela_inicial_entidade("Produto")

    def _operacao_fornecedor(self, operacao, dados_iniciais=None):
        e = self.entries
        tipo = e["Tipo"].get().strip().lower() if "Tipo" in e else ""
        if tipo not in ("pessoa", "empresa"):
            raise ValueError("Tipo inválido. Digite 'pessoa' ou 'empresa' e clique em Confirmar Tipo.")
        cpf_widget = e.get("CPF")
        cnpj_widget = e.get("CNPJ")
        cpf = cpf_widget.get() if cpf_widget else ""
        cnpj = cnpj_widget.get() if cnpj_widget else ""
        if operacao == "Cadastrar":
            novo = self.servico_fornecedor.cadastrar_fornecedor(
                nome=e["Nome"].get(), tipo=tipo, cnpj=cnpj,
                telefone_fornecedor=e["Telefone Fornecedor"].get(), cpf=cpf,
                email=e["Email"].get(), cidade=e["Cidade"].get(),
                estado=e["Estado"].get(), data_cadastro=e["Data Cadastro"].get())
            self._sincronizar_telefone_fornecedor(novo.id_fornecedor, novo.telefone_fornecedor)
            self._flash = ("ok", "Fornecedor cadastrado com sucesso!")
            self._tela_inicial_entidade("Fornecedor")
        elif operacao == "Atualizar":
            id_fornecedor = dados_iniciais["_id"]
            self.servico_fornecedor.atualizar_fornecedor(
                id_fornecedor=id_fornecedor,
                nome=e["Nome"].get(), tipo=tipo, cnpj=cnpj,
                telefone_fornecedor=e["Telefone Fornecedor"].get(), cpf=cpf,
                email=e["Email"].get(), cidade=e["Cidade"].get(),
                estado=e["Estado"].get(), data_cadastro=e["Data Cadastro"].get())
            self._sincronizar_telefone_fornecedor(id_fornecedor, e["Telefone Fornecedor"].get())
            self._flash = ("ok", "Fornecedor atualizado com sucesso!")
            self._tela_inicial_entidade("Fornecedor")

    def _sincronizar_telefone_fornecedor(self, id_fornecedor, numero):
        """Garante que o telefone do fornecedor também exista na tabela telefone_fornecedor."""
        numero_limpo = (numero or "").strip()
        if not id_fornecedor or not numero_limpo:
            return
        try:
            existentes = self.servico_telefone.listar_telefones()
        except ValueError:
            existentes = []
        ja_existe = any(
            t.id_fornecedor == id_fornecedor and t.numero == numero_limpo
            for t in existentes
        )
        if not ja_existe:
            try:
                self.servico_telefone.cadastrar_telefone(id_fornecedor=id_fornecedor, numero=numero_limpo)
            except Exception:
                pass

    def _operacao_telefone(self, operacao, dados_iniciais=None):
        e = self.entries

        # Resolver nome do fornecedor → id_fornecedor
        nome_forn = e["Nome Fornecedor"].get().strip()
        id_fornecedor = None
        if nome_forn:
            try:
                todos_forn = self.servico_fornecedor.listar_fornecedores()
                encontrados = [f for f in todos_forn if f.nome.lower() == nome_forn.lower()]
                if not encontrados:
                    raise ValueError(f"Fornecedor '{nome_forn}' não encontrado.")
                if len(encontrados) > 1:
                    raise ValueError(f"Mais de um fornecedor com o nome '{nome_forn}'. Use um nome único.")
                id_fornecedor = encontrados[0].id_fornecedor
            except ValueError:
                raise
            except Exception as ex:
                raise ValueError(f"Erro ao buscar fornecedor: {ex}")

        if operacao == "Cadastrar":
            self.servico_telefone.cadastrar_telefone(
                id_fornecedor=id_fornecedor,
                numero=e["Número"].get())
            self._flash = ("ok", "Telefone cadastrado com sucesso!")
            self._tela_inicial_entidade("Telefone")
        elif operacao == "Atualizar":
            self.servico_telefone.atualizar_telefone(
                id_telefone=dados_iniciais["_id"],
                id_fornecedor=id_fornecedor,
                numero=e["Número"].get())
            self._flash = ("ok", "Telefone atualizado com sucesso!")
            self._tela_inicial_entidade("Telefone")

    def _operacao_movimentacao(self, operacao, dados_iniciais=None):
        e = self.entries

        # Resolver nome do produto → id_produto
        nome_prod = e["Nome Produto"].get().strip()
        id_produto = None
        if nome_prod:
            try:
                todos_prod = self.servico_produto.listar_produtos()
                encontrados = [p for p in todos_prod if p.nome.lower() == nome_prod.lower()]
                if not encontrados:
                    raise ValueError(f"Produto '{nome_prod}' não encontrado.")
                if len(encontrados) > 1:
                    raise ValueError(f"Mais de um produto com o nome '{nome_prod}'. Use um nome único.")
                id_produto = encontrados[0].id_produto
            except ValueError:
                raise
            except Exception as ex:
                raise ValueError(f"Erro ao buscar produto: {ex}")

        if operacao == "Cadastrar":
            self.servico_movimentacao.cadastrar_movimentacao(
                id_produto=id_produto,
                tipo_movimentacao=e["Tipo Movimentação"].get(),
                quantidade=int(e["Quantidade"].get()),
                data_movimentacao=e["Data Movimentação"].get())
            self._flash = ("ok", "Movimentação cadastrada com sucesso!")
            self._tela_inicial_entidade("Movimentacao")
        elif operacao == "Atualizar":
            self.servico_movimentacao.atualizar_movimentacao(
                id_movimentacao=dados_iniciais["_id"],
                id_produto=id_produto,
                tipo_movimentacao=e["Tipo Movimentação"].get(),
                quantidade=int(e["Quantidade"].get()),
                data_movimentacao=e["Data Movimentação"].get())
            self._flash = ("ok", "Movimentação atualizada com sucesso!")
            self._tela_inicial_entidade("Movimentacao")

    # ── Listar com tabela clicável ─────────────────────────────────
    def listar(self, entidade, registros=None):
        self._limpar_conteudo()
        self._btn_voltar()

        tk.Label(self.content,
                 text=f"Listagem de {entidade}  (clique em um item para editar ou remover)",
                 font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=8)

        self._contagem_label = tk.Label(self.content, text="", bg="#f0f0f0",
                                         fg="#555", font=("Arial", 9, "italic"))
        self._contagem_label.pack()

        frame_tree = tk.Frame(self.content, bg="#f0f0f0")
        frame_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self._acao_frame = tk.Frame(self.content, bg="#eef3f9")
        self._acao_frame.pack(fill=tk.X, padx=10, pady=(0, 8))

        self._fundo_marca_dagua(frame_tree)

        config = {
            "Produto": {
                "colunas": ("Nome", "Preço", "Qtd", "Cadastro", "Validade"),
                "larguras": (180, 90, 60, 110, 110),
            },
            "Fornecedor": {
                "colunas": ("Nome", "Tipo", "CNPJ", "CPF", "Cidade", "UF", "Cadastro"),
                "larguras": (150, 75, 140, 120, 120, 40, 110),
            },
            "Telefone": {
                "colunas": ("Fornecedor", "Número"),
                "larguras": (220, 220),
            },
            "Movimentacao": {
                "colunas": ("Tipo", "Qtd", "Data"),
                "larguras": (150, 70, 120),
            },
        }

        cfg = config.get(entidade, {"colunas": (), "larguras": ()})
        colunas = cfg["colunas"]

        style = ttk.Style()
        style.configure("Treeview", rowheight=26, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        scrollbar = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL)
        tree = ttk.Treeview(frame_tree, columns=colunas, show="headings",
                            yscrollcommand=scrollbar.set, selectmode="browse")
        scrollbar.config(command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col, larg in zip(colunas, cfg["larguras"]):
            tree.heading(col, text=col)
            tree.column(col, width=larg, anchor=tk.CENTER)

        self._registros_listados = {}

        try:
            if registros is None:
                if entidade == "Produto":
                    registros = self.servico_produto.listar_produtos()
                elif entidade == "Fornecedor":
                    registros = self.servico_fornecedor.listar_fornecedores()
                elif entidade == "Telefone":
                    registros = self.servico_telefone.listar_telefones()
                elif entidade == "Movimentacao":
                    registros = self.servico_movimentacao.listar_movimentacoes()

            self._contagem_label.config(text=f"{len(registros)} registro(s)")

            for r in registros:
                if entidade == "Produto":
                    vals = (r.nome, f"{r.preco:.2f}", r.quantidade, r.data_cadastro, r.data_validade)
                elif entidade == "Fornecedor":
                    vals = (r.nome, r.tipo, r.cnpj, r.cpf, r.cidade, r.estado, r.data_cadastro)
                elif entidade == "Telefone":
                    vals = (self._nome_fornecedor_por_id(r.id_fornecedor), r.numero)
                elif entidade == "Movimentacao":
                    vals = (r.tipo_movimentacao, r.quantidade, r.data_movimentacao)
                else:
                    vals = ()
                iid = tree.insert("", tk.END, values=vals)
                self._registros_listados[iid] = r

        except ValueError as ex:
            tk.Label(self.content, text=str(ex), bg="#f0f0f0",
                     fg="#e74c3c", font=("Arial", 11)).pack(pady=10)
            return
        except Exception as ex:
            tk.Label(self.content, text=f"Erro ao listar: {ex}", bg="#f0f0f0",
                     fg="#e74c3c", font=("Arial", 11)).pack(pady=10)
            return

        def ao_clicar(event):
            sel = tree.selection()
            if not sel:
                return
            reg = self._registros_listados.get(sel[0])
            if reg:
                self._painel_acao(entidade, reg)

        tree.bind("<<TreeviewSelect>>", ao_clicar)

    # ── Buscar por Nome ────────────────────────────────────────────
    def buscar_por_nome(self, entidade):
        self._limpar_conteudo()
        self._btn_voltar()

        if entidade == "Telefone":
            label_campo = "Nome Fornecedor"
        elif entidade == "Movimentacao":
            label_campo = "Tipo Movimentação"
        else:
            label_campo = "Nome"
        tk.Label(self.content, text=f"Buscar {entidade} por {label_campo}",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=20)

        row = tk.Frame(self.content, bg="#f0f0f0")
        row.pack()
        tk.Label(row, text=f"{label_campo}:", bg="#f0f0f0", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        entry = tk.Entry(row, width=30, font=("Arial", 11))
        entry.pack(side=tk.LEFT)
        entry.focus()

        resultado_frame = tk.Frame(self.content, bg="#f0f0f0")
        resultado_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        _wm_lbl = self._fundo_marca_dagua(resultado_frame)

        def executar_busca(event=None):
            termo = entry.get().strip()

            # Limpar resultado anterior
            for w in resultado_frame.winfo_children():
                if w is not _wm_lbl:
                    w.destroy()

            if not termo:
                tk.Label(resultado_frame, text="Digite um termo para buscar.",
                         bg="#f0f0f0", font=("Arial", 11), fg="#e74c3c").pack(pady=15)
                return

            try:
                if entidade == "Produto":
                    encontrados = self.servico_produto.buscar_produto_por_nome(termo)
                elif entidade == "Fornecedor":
                    encontrados = self.servico_fornecedor.buscar_fornecedor_por_nome(termo)
                elif entidade == "Telefone":
                    encontrados = self.servico_telefone.buscar_telefone_por_nome_fornecedor(termo)
                elif entidade == "Movimentacao":
                    encontrados = self.servico_movimentacao.buscar_movimentacao_por_tipo(termo)
                else:
                    encontrados = []
            except ValueError:
                encontrados = []
            except Exception as ex:
                messagebox.showerror("Erro", str(ex))
                return

            if not encontrados:
                tk.Label(resultado_frame, text="Nenhum resultado encontrado.",
                         bg="#f0f0f0", font=("Arial", 11), fg="#e74c3c").pack(pady=15)
                return

            tk.Label(resultado_frame,
                     text=f"{len(encontrados)} resultado(s) — clique para editar ou remover",
                     bg="#f0f0f0", font=("Arial", 10, "italic"), fg="#555").pack(pady=4)

            self.listar(entidade, registros=encontrados)

        tk.Button(row, text="Buscar", bg="#2980b9", fg="white",
                  font=("Arial", 11), padx=12, relief=tk.FLAT,
                  cursor="hand2", command=executar_busca).pack(side=tk.LEFT, padx=8)

        entry.bind("<Return>", executar_busca)

    # ── Painel inline: Atualizar ou Remover ─────────────────────────
    def _painel_acao(self, entidade, reg):
        painel = self._acao_frame
        for w in painel.winfo_children():
            w.destroy()

        resumo = self._resumo_registro(entidade, reg)
        tk.Label(painel, text=resumo, font=("Courier", 10), justify=tk.LEFT,
                 bg="#eef3f9", padx=10, pady=6).pack()
        tk.Label(painel, text="O que deseja fazer com este registro?",
                 font=("Arial", 10), bg="#eef3f9", pady=2).pack()

        btn_frame = tk.Frame(painel, bg="#eef3f9")
        btn_frame.pack(pady=(0, 8))

        def abrir_atualizacao():
            self.formulario(entidade, "Atualizar", dados_iniciais=self._dados_para_form(entidade, reg))

        def remover_de_fato():
            try:
                if entidade == "Produto":
                    self.servico_produto.remover_produto(reg.id_produto)
                elif entidade == "Fornecedor":
                    self.servico_fornecedor.remover_fornecedor(reg.id_fornecedor)
                elif entidade == "Telefone":
                    self.servico_telefone.remover_telefone(reg.id_telefone)
                elif entidade == "Movimentacao":
                    self.servico_movimentacao.remover_movimentacao(reg.id_movimentacao)
                self._flash = ("ok", "Registro removido com sucesso!")
                self._tela_inicial_entidade(entidade)
            except Exception as e:
                for w in painel.winfo_children():
                    w.destroy()
                tk.Label(painel, text=resumo, font=("Courier", 10), justify=tk.LEFT,
                         bg="#eef3f9", padx=10, pady=6).pack()
                tk.Label(painel, text=f"Erro ao remover: {e}", font=("Arial", 10),
                         bg="#eef3f9", fg="#e74c3c", pady=2).pack()

        def confirmar_remocao():
            for w in painel.winfo_children():
                w.destroy()
            tk.Label(painel, text=resumo, font=("Courier", 10), justify=tk.LEFT,
                     bg="#eef3f9", padx=10, pady=6).pack()
            tk.Label(painel, text="Tem certeza que deseja remover?",
                     font=("Arial", 10), bg="#eef3f9", fg="#e74c3c", pady=2).pack()

            confirm_frame = tk.Frame(painel, bg="#eef3f9")
            confirm_frame.pack(pady=(0, 8))

            tk.Button(confirm_frame, text="Sim, remover", bg="#e74c3c", fg="white",
                      font=("Arial", 10), padx=10, relief=tk.FLAT,
                      cursor="hand2", command=remover_de_fato).pack(side=tk.LEFT, padx=5)
            tk.Button(confirm_frame, text="Cancelar", bg="#bdc3c7", fg="black",
                      font=("Arial", 10), padx=10, relief=tk.FLAT,
                      cursor="hand2", command=cancelar).pack(side=tk.LEFT, padx=5)

        def cancelar():
            for w in painel.winfo_children():
                w.destroy()

        tk.Button(btn_frame, text="✏ Atualizar", bg="#2980b9", fg="white",
                  font=("Arial", 11), padx=15, pady=6, relief=tk.FLAT,
                  cursor="hand2", command=abrir_atualizacao).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="🗑 Remover", bg="#e74c3c", fg="white",
                  font=("Arial", 11), padx=15, pady=6, relief=tk.FLAT,
                  cursor="hand2", command=confirmar_remocao).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Cancelar", bg="#95a5a6", fg="white",
                  font=("Arial", 11), padx=15, pady=6, relief=tk.FLAT,
                  cursor="hand2", command=cancelar).pack(side=tk.LEFT, padx=8)

    def _resumo_registro(self, entidade, reg):
        if entidade == "Produto":
            return (f"Nome: {reg.nome}  |  Preço: {reg.preco:.2f}  |  Qtd: {reg.quantidade}\n"
                    f"Cadastro: {reg.data_cadastro}  |  Validade: {reg.data_validade}")
        elif entidade == "Fornecedor":
            return (f"Nome: {reg.nome}  |  Tipo: {reg.tipo}\n"
                    f"CNPJ: {reg.cnpj}  |  CPF: {reg.cpf}\n"
                    f"Cidade: {reg.cidade} / {reg.estado}  |  Cadastro: {reg.data_cadastro}")
        elif entidade == "Telefone":
            nome_forn = self._nome_fornecedor_por_id(reg.id_fornecedor)
            return f"Fornecedor: {nome_forn}  |  Número: {reg.numero}"
        elif entidade == "Movimentacao":
            return (f"Tipo: {reg.tipo_movimentacao}  |  Qtd: {reg.quantidade}\n"
                    f"Data: {reg.data_movimentacao}")
        return ""

    def _data_para_exibicao(self, valor):
        """Converte aaaa-mm-dd (formato do banco) para dd/mm/aaaa (formato do formulário)."""
        try:
            from datetime import datetime
            return datetime.strptime(str(valor), "%Y-%m-%d").strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            return valor

    def _nome_fornecedor_por_id(self, id_fornecedor):
        if not id_fornecedor:
            return ""
        try:
            for f in self.servico_fornecedor.listar_fornecedores():
                if f.id_fornecedor == id_fornecedor:
                    return f.nome
        except Exception:
            pass
        return ""

    def _nome_produto_por_id(self, id_produto):
        if not id_produto:
            return ""
        try:
            for p in self.servico_produto.listar_produtos():
                if p.id_produto == id_produto:
                    return p.nome
        except Exception:
            pass
        return ""

    def _dados_para_form(self, entidade, reg):
        if entidade == "Produto":
            nome_forn = self._nome_fornecedor_por_id(reg.id_fornecedor)
            return {"_id": reg.id_produto, "Nome Fornecedor": nome_forn,
                    "Nome": reg.nome, "Preço": reg.preco, "Quantidade": reg.quantidade,
                    "Data Cadastro": self._data_para_exibicao(reg.data_cadastro), "Data Validade": self._data_para_exibicao(reg.data_validade)}
        elif entidade == "Fornecedor":
            return {"_id": reg.id_fornecedor, "Nome": reg.nome, "Tipo": reg.tipo,
                    "CNPJ": reg.cnpj, "Telefone Fornecedor": reg.telefone_fornecedor,
                    "CPF": reg.cpf, "Email": reg.email, "Cidade": reg.cidade,
                    "Estado": reg.estado, "Data Cadastro": self._data_para_exibicao(reg.data_cadastro)}
        elif entidade == "Telefone":
            nome_forn = self._nome_fornecedor_por_id(reg.id_fornecedor)
            return {"_id": reg.id_telefone, "Nome Fornecedor": nome_forn, "Número": reg.numero}
        elif entidade == "Movimentacao":
            nome_prod = self._nome_produto_por_id(reg.id_produto)
            return {"_id": reg.id_movimentacao, "Nome Produto": nome_prod,
                    "Tipo Movimentação": reg.tipo_movimentacao,
                    "Quantidade": reg.quantidade, "Data Movimentação": self._data_para_exibicao(reg.data_movimentacao)}
        return {}

    def executar(self):
        self.root.mainloop()
