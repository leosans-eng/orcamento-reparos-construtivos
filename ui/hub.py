import tkinter as tk


class HubFrame(tk.Frame):
    def __init__(self, parent, on_selecionar_modulo):
        super().__init__(parent, bg="#ececec")
        self.on_selecionar_modulo = on_selecionar_modulo
        self._montar()

    def _montar(self):
        container = tk.Frame(self, bg="#ececec")
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            container,
            text="ORC",
            font=("Arial", 22, "bold"),
            fg="#006699",
            bg="#ececec",
        ).pack(pady=(0, 4))

        tk.Label(
            container,
            text="Orçamentos de Reparos Construtivos",
            font=("Arial", 11),
            fg="#444444",
            bg="#ececec",
        ).pack(pady=(0, 24))

        cartoes = tk.Frame(container, bg="#ececec")
        cartoes.pack()

        self._criar_cartao(
            cartoes,
            titulo="Área Privativa",
            descricao="Orçamento de reparos em unidades autônomas",
            modulo="area_privativa",
            habilitado=True,
            coluna=0,
        )
        self._criar_cartao(
            cartoes,
            titulo="Área Comum",
            descricao="Orçamento de reparos em áreas comuns do edifício",
            modulo="area_comum",
            habilitado=False,
            coluna=1,
            aviso="Em breve",
        )
        self._criar_cartao(
            cartoes,
            titulo="Consulta SINAPI",
            descricao="Pesquisar composições e preços da base",
            modulo="consulta_sinapi",
            habilitado=True,
            coluna=2,
        )

    def _criar_cartao(
        self,
        parent,
        titulo,
        descricao,
        modulo,
        habilitado,
        coluna,
        aviso=None,
    ):
        largura = 220
        altura = 130
        cor_fundo = "#ffffff" if habilitado else "#f0f0f0"
        cor_borda = "#006699" if habilitado else "#cccccc"
        cor_titulo = "#006699" if habilitado else "#999999"
        cor_texto = "#555555" if habilitado else "#aaaaaa"

        cartao = tk.Frame(
            parent,
            width=largura,
            height=altura,
            bg=cor_fundo,
            highlightbackground=cor_borda,
            highlightthickness=2,
            cursor="hand2" if habilitado else "arrow",
        )
        cartao.grid(row=0, column=coluna, padx=12, pady=4)
        cartao.grid_propagate(False)

        tk.Label(
            cartao,
            text=titulo,
            font=("Arial", 12, "bold"),
            fg=cor_titulo,
            bg=cor_fundo,
        ).pack(pady=(18, 6))

        tk.Label(
            cartao,
            text=descricao,
            font=("Arial", 9),
            fg=cor_texto,
            bg=cor_fundo,
            wraplength=largura - 24,
            justify="center",
        ).pack(padx=12)

        if aviso:
            tk.Label(
                cartao,
                text=aviso,
                font=("Arial", 8, "italic"),
                fg="#999999",
                bg=cor_fundo,
            ).pack(pady=(8, 0))

        if habilitado:
            def ao_clicar(_event=None, mod=modulo):
                self.on_selecionar_modulo(mod)

            cartao.bind("<Button-1>", ao_clicar)
            for filho in cartao.winfo_children():
                filho.bind("<Button-1>", ao_clicar)

            def ao_entrar(_event, c=cartao):
                c.configure(highlightbackground="#004466")

            def ao_sair(_event, c=cartao):
                c.configure(highlightbackground="#006699")

            cartao.bind("<Enter>", ao_entrar)
            cartao.bind("<Leave>", ao_sair)
