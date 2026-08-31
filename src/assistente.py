import datetime
import time
import webbrowser
import speech_recognition as sr
from src.agenda import GerenciadorAgenda
from src.captura import GerenciadorCaptura
from src.config import (
    NOME_ASSISTENTE,
    TIMEOUT_PADRAO_ESCUTA,
    TIMEOUT_RESPOSTA,
    LIMITE_FALA_PADRAO,
    LIMITE_FALA_CURTA,
    LIMITE_FALA_LONGA,
)
from src.ia_groq import ClienteIA
from src.microfone import OuvinteMicrofone
from src.voz import SintetizadorVoz
from src.reconhecimento import GerenciadorFacial
from src.leitura import LeitorTexto
from src.servicos import ServicosWeb, ControleSistema
from src.easter_eggs import GerenciadorEasterEggs

class AssistenteBruxo:
    """
    Classe orquestradora da Assistente Virtual Bruxo.
    
    Responsabilidades:
    - Integrar módulos de voz, microfone, agenda, captura, visão, web e IA.
    - Executar o loop contínuo de escuta com acionamento por Wake Word.
    - Despachar intenções e comandos do usuário de forma modular (Dispatcher Pattern).
    """

    def __init__(self):
        self.nome = NOME_ASSISTENTE
        self.voz = SintetizadorVoz()
        self.microfone = OuvinteMicrofone()
        self.agenda = GerenciadorAgenda()
        self.captura = GerenciadorCaptura()
        self.ia = ClienteIA()
        self.facial = GerenciadorFacial()
        self.leitor_texto = LeitorTexto()
        self.web = ServicosWeb()
        self.sistema = ControleSistema()
        self.easter_eggs = GerenciadorEasterEggs()

    def _eh_eco(self, resposta: str, pergunta: str) -> bool:
        """
        Verifica se o que foi captado pelo microfone foi apenas o áudio
        da própria pergunta dita pelo assistente saindo pela caixa de som.
        """
        resp = resposta.strip().lower()
        perg = pergunta.strip().lower()

        # Remove pontuações simples
        for p in "?!.,:;\"'":
            resp = resp.replace(p, "")
            perg = perg.replace(p, "")

        if not resp:
            return False

        # Se a resposta for exatamente igual à pergunta
        if resp == perg:
            return True

        # Se for uma frase longa (4+ palavras) e for um trecho da pergunta
        palavras_resp = resp.split()
        if len(palavras_resp) >= 4 and resp in perg:
            return True

        return False

    def perguntar(
        self,
        texto_pergunta: str,
        fonte,
        timeout: int = TIMEOUT_RESPOSTA,
        phrase_time_limit: int = LIMITE_FALA_CURTA,
    ) -> str:
        """
        Fala a pergunta ao usuário e escuta o microfone com janela de tempo persistente.
        Garante que o áudio termine de forma limpa e dá o tempo total de timeout para o usuário responder.
        """
        # Reproduz a pergunta até o final para evitar que o alto-falante interfira no microfone
        self.voz.falar(texto_pergunta, aguardar=True)
        
        inicio = time.time()

        while time.time() - inicio < timeout:
            tempo_decorrido = time.time() - inicio
            tempo_restante = timeout - tempo_decorrido
            if tempo_restante < 1.0:
                break

            resposta = self.microfone.escutar(
                fonte,
                timeout=max(2, int(tempo_restante)),
                phrase_time_limit=phrase_time_limit,
            )

            # Se não ouviu nada nessa fatia, não desiste: continua escutando até o tempo total acabar
            if not resposta:
                continue

            # Se captou o eco residual da pergunta do Bruxo, continua escutando
            if self._eh_eco(resposta, texto_pergunta):
                continue

            return resposta.strip()

        return ""

    # ==========================================
    # CONSULTAS BÁSICAS (Horas e Data)
    # ==========================================

    def obter_horas(self) -> str:
        """Item 4: Retorna a hora atual por extenso."""
        agora = datetime.datetime.now()
        return f"Agora são {agora.hour} horas e {agora.minute} minutos."

    def obter_data(self) -> str:
        """Item 5: Retorna a data atual por extenso."""
        agora = datetime.datetime.now()
        meses = [
            "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
        ]
        return f"Hoje é dia {agora.day} de {meses[agora.month - 1]} de {agora.year}."

    # ==========================================
    # MÉTODOS DE AGENDA (Itens 2, 3 e 8)
    # ==========================================

    def cadastrar_evento(self, fonte):
        print("[AGUARDANDO DESCRICAO DO EVENTO...]")
        evento = self.perguntar(
            "Ok, qual evento devo cadastrar?",
            fonte,
            timeout=TIMEOUT_RESPOSTA,
            phrase_time_limit=LIMITE_FALA_LONGA,
        )

        if not evento:
            self.voz.falar("Não consegui ouvir o evento. O cadastro foi cancelado.")
            return

        print(f"[EVENTO TRANSCRITO]: \"{evento}\"")
        if self.agenda.cadastrar_evento(evento):
            self.voz.falar(f"Evento {evento} cadastrado com sucesso na sua agenda.")
        else:
            self.voz.falar("Houve um erro ao salvar o evento na agenda.")

    def ler_agenda(self):
        eventos = self.agenda.ler_eventos()
        if not eventos:
            self.voz.falar("Sua agenda está vazia no momento.")
            return

        print(f"[LENDO AGENDA] Total: {len(eventos)} evento(s)")
        texto_falado = f"Você tem {len(eventos)} evento{'s' if len(eventos) > 1 else ''} na agenda: "
        for i, evento in enumerate(eventos, 1):
            texto_falado += f" Evento {i}: {evento}."

        self.voz.falar(texto_falado)

    def limpar_agenda(self):
        if self.agenda.limpar_agenda():
            self.voz.falar("Sua agenda foi limpa com sucesso.")
            print("[AGENDA LIMPA] Todos os eventos foram removidos.")
        else:
            self.voz.falar("Houve um erro ao limpar sua agenda.")

    # ==========================================
    # CAPTURA E LIMPEZA DE IMAGENS (Item 10)
    # ==========================================

    def tirar_print(self):
        caminho = self.captura.tirar_print()
        if caminho:
            self.voz.falar("Print da tela tirado e salvo com sucesso na pasta imagens.")
        else:
            self.voz.falar("Houve um erro ao tentar tirar o print da tela.")

    def limpar_fotos(self):
        qtd, sucesso = self.captura.limpar_fotos()
        if sucesso:
            if qtd == 0:
                self.voz.falar("A pasta de imagens já está vazia.")
            else:
                self.voz.falar(f"Todas as {qtd} imagens foram apagadas da pasta.")
        else:
            self.voz.falar("Houve um erro ao limpar as imagens.")

    # ==========================================
    # RECONHECIMENTO FACIAL
    # ==========================================
    def cadastrar_facial(self, fonte):
        print("[AGUARDANDO NOME PARA CADASTRO FACIAL...]")
        nome = self.perguntar(
            "Qual é o nome da pessoa que será cadastrada?",
            fonte,
            timeout=TIMEOUT_RESPOSTA,
            phrase_time_limit=LIMITE_FALA_CURTA,
        )
        if not nome:
            self.voz.falar("Não escutei o nome. Cadastro cancelado.")
            return
            
        nome_limpo = nome.strip()
        self.voz.falar(f"Certo. Vou abrir a câmera agora. Por favor, {nome_limpo}, olhe para a lente.", aguardar=True)
        
        sucesso = self.facial.capturar_rosto(nome_limpo)
        if sucesso:
            self.voz.falar(f"Pronto! O rosto de {nome_limpo} foi cadastrado com sucesso no sistema.")
        else:
            self.voz.falar("Desculpe, ocorreu um erro ao acessar a câmera ou não consegui identificar o rosto.")

    def identificar_usuario(self):
        self.voz.falar("Deixe-me dar uma olhada. Olhe para a câmera.", aguardar=True)
        nome = self.facial.reconhecer_rosto()
        
        if nome:
            self.voz.falar(f"Você é o {nome}! Como posso ajudar?")
        else:
            self.voz.falar("Não consegui reconhecer seu rosto. Talvez você precise se cadastrar primeiro.")

    def remover_cadastro_facial(self, fonte, comando: str = None):
        # 1. Se o comando já mencionou um nome específico (ex: "apagar rosto do Pedro", "remover o cadastro do Bruno")
        nome_especifico = None
        if comando:
            for prefixo in ["rosto do ", "rosto da ", "rosto de ", "rostos de ", "cadastro do ", "cadastro da ", "cadastro de ", "pessoa "]:
                if prefixo in comando:
                    candidato = comando.split(prefixo, 1)[1].strip()
                    palavras_uteis = [w for w in candidato.split() if w not in ["o", "a", "os", "as", "do", "da", "de", "rosto", "rostos", "cadastro", "todos", "tudo", "geral", "específico", "uma", "pessoa", "rust", "facial", "biometria"]]
                    if palavras_uteis:
                        nome_especifico = " ".join(palavras_uteis)
                        break

        if nome_especifico:
            sucesso, msg = self.facial.apagar_cadastro(nome_especifico)
            self.voz.falar(msg)
            return

        print("[AGUARDANDO: TODOS OU ESPECÍFICO...]")
        resposta = self.perguntar(
            "Você deseja apagar todos os cadastros ou de uma pessoa específica?",
            fonte,
            timeout=TIMEOUT_RESPOSTA,
            phrase_time_limit=LIMITE_FALA_CURTA,
        )
        
        if not resposta:
            self.voz.falar("Não escutei sua resposta. Operação cancelada.")
            return
            
        resposta = resposta.lower().strip()
        if any(t in resposta for t in ["todos", "geral", "todo mundo", "tudo", "ambos", "gerais", "limpar tudo"]):
            sucesso, msg = self.facial.apagar_cadastro(None)
            self.voz.falar(msg)
        elif any(t in resposta for t in ["específico", "uma pessoa", "alguém", "especifica", "específica", "um"]):
            print("[AGUARDANDO NOME PARA REMOVER...]")
            nome = self.perguntar(
                "Qual é o nome da pessoa que devo remover do sistema?",
                fonte,
                timeout=TIMEOUT_RESPOSTA,
                phrase_time_limit=LIMITE_FALA_CURTA,
            )
            if not nome:
                self.voz.falar("Não escutei o nome. Cancelando.")
                return
            sucesso, msg = self.facial.apagar_cadastro(nome)
            self.voz.falar(msg)
        else:
            # Caso a pessoa responda diretamente o nome (ex: "Pedro", "do Bruno", "Eduardo")
            nome_direto = resposta.replace("do ", "").replace("da ", "").replace("de ", "").replace("o ", "").replace("a ", "").strip()
            if nome_direto:
                sucesso, msg = self.facial.apagar_cadastro(nome_direto)
                self.voz.falar(msg)
            else:
                self.voz.falar("Opção não reconhecida. Cancelando a exclusão.")

    # ==========================================
    # LEITURA OCR (TEXTO E NÚMEROS)
    # ==========================================
    def ler_texto_camera(self):
        self.voz.falar("Modo leitura ativado. Posicione o texto na câmera e aperte S para eu ler, ou Q para cancelar.", aguardar=True)
        texto_lido = self.leitor_texto.escanear_texto()
        
        if texto_lido:
            self.voz.falar(f"Eu identifiquei o seguinte texto: {texto_lido}")
        else:
            self.voz.falar("Não consegui ler nenhum texto ou número da câmera, ou a operação foi cancelada.")

    # ==========================================
    # APRESENTAÇÃO E LISTA DE COMANDOS
    # ==========================================

    def apresentar(self):
        """Apresenta o assistente Bruxo e explica detalhadamente todas as suas funcionalidades."""
        separador = "=" * 60
        apresentacao_terminal = (
            f"\n{separador}\n"
            "               APRESENTAÇÃO DO BRUXO\n"
            f"{separador}\n"
            "  Olá! Eu sou o Bruxo, seu assistente virtual inteligente.\n"
            "  Fui desenvolvido para ajudar você no dia a dia com automação,\n"
            "  inteligência artificial e visão computacional.\n\n"
            "  Principais funcionalidades:\n"
            "  1. Agenda: Cadastrar, ler e limpar seus compromissos diários.\n"
            "  2. Visão Computacional: Cadastrar e reconhecer seu rosto pela câmera.\n"
            "  3. Leitura OCR: Escanear e ler textos ou números de documentos físicos.\n"
            "  4. Multimídia: Tocar no Spotify e pesquisar vídeos no YouTube.\n"
            "  5. Web e Produtividade: Pesquisar no Google com filtro IA e abrir o portal da FIAP.\n"
            "  6. Informações Úteis: Previsão do tempo de qualquer cidade e cotação do dólar.\n"
            "  7. Controle de Sistema: Volume, play/pause de mídia e captura de tela (prints).\n"
            "  8. IA Generativa: Conversar e tirar dúvidas usando LLaMA via Groq Cloud.\n"
            f"{separador}\n"
        )
        print(apresentacao_terminal)
        
        texto_voz = (
            "Olá! Eu sou o Bruxo, seu assistente virtual inteligente. "
            "Fui desenvolvido para ajudar você no dia a dia com automação, inteligência artificial e visão computacional. "
            "Entre as minhas principais funcionalidades, eu posso: "
            "gerenciar, cadastrar e ler sua agenda de compromissos; "
            "cadastrar e reconhecer seu rosto pela câmera em tempo real; "
            "escanear e ler textos ou números de documentos físicos usando OCR; "
            "tocar músicas e artistas diretamente no Spotify e abrir vídeos no YouTube; "
            "fazer pesquisas seguras no Google e abrir o portal da faculdade; "
            "informar a previsão do tempo de qualquer cidade e a cotação do dólar em tempo real; "
            "tirar prints da tela, limpar imagens e controlar o volume e reprodução do sistema; "
            "e responder a qualquer dúvida ou pergunta usando Inteligência Artificial Generativa. "
            "Como posso ajudar você hoje?"
        )
        self.voz.falar(texto_voz)

    def listar_comandos(self):
        separador = "=" * 55
        menu = (
            f"\n{separador}\n"
            "          LISTA DE COMANDOS DO BRUXO\n"
            f"{separador}\n"
            "  1. 'Bruxo, que horas são?'\n"
            "  2. 'Bruxo, que dia é hoje?'\n"
            "  3. 'Bruxo, cadastrar evento na agenda'\n"
            "  4. 'Bruxo, ler agenda'\n"
            "  5. 'Bruxo, limpar agenda'\n"
            "  6. 'Bruxo, tirar um print da tela'\n"
            "  7. 'Bruxo, limpar fotos'\n"
            "  8. 'Bruxo, youtube' (buscar vídeo)\n"
            "  9. 'Bruxo, google' (pesquisar com filtro)\n"
            " 10. 'Bruxo, temperatura' (previsão do tempo)\n"
            " 11. 'Bruxo, dólar' (cotação)\n"
            " 12. 'Bruxo, volume' (aumentar/diminuir/mutar)\n"
            " 13. 'Bruxo, portal' (faculdade)\n"
            " 14. 'Bruxo, pausar/despausar' (controle de mídia)\n"
            " 15. 'Bruxo, cadastrar rosto' (dataset facial)\n"
            " 16. 'Bruxo, apagar rosto' (limpar dataset)\n"
            " 17. 'Bruxo, quem sou eu' (reconhecimento facial)\n"
            " 18. 'Bruxo, escanear texto' (leitura OCR)\n"
            " 19. 'Bruxo, quem é você' (apresentação completa)\n"
            " 20. 'Bruxo, Alanzoka' / 'Pega no Breu' (Easter Eggs)\n"
            " 21. 'Bruxo, <qualquer pergunta>' (Groq IA)\n"
            " 22. 'Bruxo, tchau' (ou 'desligar')\n"
            f"{separador}\n"
        )
        print(menu)
        texto_voz = "Adicionei comandos de escaneamento de texto e reconhecimento facial à minha lista. Confira o terminal para mais detalhes."
        self.voz.falar(texto_voz)

    # ==========================================
    # DESPACHO E PROCESSAMENTO DE COMANDOS (DISPATCHER)
    # ==========================================

    def _tratar_utilitarios(self, comando: str) -> bool:
        """Processa comandos utilitários (apresentação, ajuda, horas e data)."""
        # Apresentação do Bruxo
        if any(t in comando for t in [
            "quem é você", "quem e voce", "quem você é", "quem voce e",
            "o que você faz", "o que voce faz", "o que você sabe fazer", "o que voce sabe fazer",
            "se apresente", "apresente-se", "apresente se", "apresentar", "apresentação",
            "fale sobre você", "fale sobre voce", "conte sobre você", "conte sobre voce",
            "suas funcionalidades", "suas funções", "suas funcoes", "qual o seu papel", "qual é o seu papel"
        ]):
            self.apresentar()
            return True

        # Ajuda e Lista de Comandos
        elif any(t in comando for t in ["comando", "comandos", "ajuda", "menu"]):
            self.listar_comandos()
            return True

        # Horas e Data
        elif any(t in comando for t in ["hora", "horas"]):
            self.voz.falar(self.obter_horas())
            return True
        elif any(t in comando for t in ["dia", "data"]):
            self.voz.falar(self.obter_data())
            return True

        return False

    def _tratar_agenda(self, comando: str, fonte) -> bool:
        """Processa comandos de persistência e consulta da agenda."""
        # Limpar Agenda
        if any(t in comando for t in [
            "limpar agenda", "limpar a agenda", "apagar agenda", "apagar a agenda",
            "excluir agenda", "excluir a agenda", "deletar agenda", "deletar a agenda",
            "remover agenda", "remover a agenda", "zerar agenda", "esvaziar agenda",
            "limpar eventos", "apagar eventos", "excluir eventos", "deletar eventos",
            "limpar os eventos", "apagar todos os eventos", "apagar os eventos",
            "limpar compromissos", "apagar compromissos"
        ]) or ("agenda" in comando and any(t in comando for t in ["limpar", "apagar", "excluir", "deletar", "remover", "zerar", "esvaziar"])):
            self.limpar_agenda()
            return True

        # Ler Agenda
        elif any(t in comando for t in [
            "ler agenda", "ler a agenda", "ver agenda", "ver a agenda", "minha agenda",
            "consultar agenda", "consultar a agenda", "o que tem na agenda", "quais os eventos",
            "quais são os eventos", "mostrar agenda", "mostrar a agenda", "eventos da agenda",
            "abrir agenda", "agenda de hoje", "eventos de hoje", "ler os eventos", "ver os eventos"
        ]) or ("agenda" in comando and any(t in comando for t in ["ler", "ver", "mostrar", "consultar", "abrir", "quais", "qual", "tem", "lê", "leia"]) and not any(t in comando for t in ["limpar", "apagar", "excluir", "deletar", "remover", "zerar", "esvaziar", "cadastrar", "novo"])):
            self.ler_agenda()
            return True

        # Cadastrar Evento Diretamente
        elif any(t in comando for t in ["cadastrar evento", "cadastrar na agenda", "novo evento", "agendar compromisso", "adicionar evento", "agendar evento"]):
            self.cadastrar_evento(fonte)
            return True

        return False

    def _tratar_biometria(self, comando: str, fonte) -> bool:
        """Processa comandos de visão computacional e reconhecimento facial."""
        # Identificar Usuário (Quem sou eu)
        if any(t in comando for t in ["quem sou eu", "me reconhece", "reconhecer meu rosto", "qual o meu nome", "qual é o meu nome"]):
            self.identificar_usuario()
            return True

        # Cadastrar Rosto Diretamente
        elif any(t in comando for t in ["cadastrar rosto", "cadastrar face", "cadastrar pessoa", "gravar rosto", "registrar rosto", "reconhecimento facial"]):
            self.cadastrar_facial(fonte)
            return True

        # Apagar Cadastro Facial
        elif any(t in comando for t in [
            "apagar rosto", "apagar rostos", "apagar os rostos", "apagar o rosto",
            "remover rosto", "remover rostos", "remover os rostos", "remover o rosto",
            "deletar rosto", "deletar rostos", "deletar os rostos", "deletar o rosto",
            "excluir rosto", "excluir rostos", "excluir os rostos", "excluir o rosto",
            "limpar rosto", "limpar rostos", "limpar os rostos", "limpar o rosto",
            "apagar cadastro", "remover cadastro", "excluir cadastro", "deletar cadastro",
            "apagar biometria", "remover biometria", "excluir biometria", "limpar biometria",
            "apagar cadastro facial", "remover cadastro facial", "excluir cadastro facial",
            "apagar rust", "remover rust", "deletar rust", "excluir rust", "limpar rust",
            "apagar rusto", "remover rusto", "apagar rostu", "remover rostu"
        ]):
            self.remover_cadastro_facial(fonte, comando)
            return True

        return False

    def _tratar_midia_e_sistema(self, comando: str, fonte) -> bool:
        """Processa controle de hardware, volume, prints e leitura OCR."""
        # Volume e Controle de Som
        if any(t in comando for t in ["volume", "mutar", "mudo", "som", "desmutar", "silenciar"]):
            if any(t in comando for t in ["desmutar", "desmuta", "voltar som", "volta o som", "tirar mudo", "tira o mudo", "reativar som", "desmutado"]):
                self.sistema.mutar_desmutar()
                self.voz.falar("Som restaurado.")
            elif any(t in comando for t in ["mutar", "muta", "mudo", "silenciar", "silencio", "silêncio"]) and not any(t in comando for t in ["desmuta", "tirar mudo", "tira o mudo", "voltar som"]):
                self.sistema.mutar_desmutar()
                self.voz.falar("Volume mutado.")
            elif any(t in comando for t in ["aumentar", "aumente", "aumenta", "sobe", "subir", "mais alto"]):
                self.sistema.aumentar_volume()
                self.voz.falar("Aumentando o volume.")
            elif any(t in comando for t in ["diminuir", "diminua", "diminui", "abaixa", "abaixar", "mais baixo"]):
                self.sistema.diminuir_volume()
                self.voz.falar("Diminuindo o volume.")
            else:
                self.voz.falar("Não entendi se devo aumentar, diminuir, mutar ou desmutar o volume.")
            return True

        # Pausar / Despausar Mídia
        elif any(t in comando for t in ["pausa", "despausa", "play", "parar", "continuar", "paus"]):
            self.sistema.pausar_despausar()
            self.voz.falar("Feito.")
            return True

        # Tirar Print da Tela
        elif any(t in comando for t in ["print", "captura de tela", "tirar foto da tela", "prin"]):
            self.tirar_print()
            return True

        # Limpar Imagens / Prints
        elif any(t in comando for t in ["limpar fotos", "apagar fotos", "limpar prints", "apagar imagens", "limpar imagens", "apagar foto", "limpar imagem"]):
            self.limpar_fotos()
            return True

        # Escanear Texto / OCR pela Câmera
        elif any(t in comando for t in [
            "escanear", "modo leitura", "extrair texto", "o que está escrito",
            "ler texto", "ler texto na câmera", "ler com a câmera", "ler pela câmera",
            "ler documento", "ler papel", "ler da câmera", "ler na câmera",
            "leitor de texto", "ler pela camera", "ler na camera", "escanear documento",
            "escanear texto", "escanear papel"
        ]):
            self.ler_texto_camera()
            return True

        return False

    def _tratar_web_e_servicos(self, comando: str, fonte) -> bool:
        """Processa buscas na web, YouTube, Spotify e APIs externas."""
        # Previsão do Tempo (Clima)
        if any(t in comando for t in ["clima", "temperatura", "previsão", "previsao", "tempo"]):
            print("[AGUARDANDO NOME DA CIDADE...]")
            cidade = self.perguntar(
                "De qual cidade você quer saber a temperatura?",
                fonte,
                timeout=TIMEOUT_RESPOSTA,
                phrase_time_limit=LIMITE_FALA_CURTA,
            )
            if not cidade:
                self.voz.falar("Não entendi a cidade. Busca de clima cancelada.")
                return True
            self.voz.falar(self.web.obter_clima(cidade))
            return True

        # Cotação do Dólar
        elif any(t in comando for t in ["dólar", "dolar", "cotação"]):
            self.voz.falar(self.web.obter_cotacao_dolar())
            return True

        # Pesquisar no Google (com filtro de segurança)
        elif any(t in comando for t in ["google", "pesquisar na internet"]):
            print("[AGUARDANDO TERMO DE BUSCA...]")
            termo = self.perguntar(
                "O que você deseja pesquisar no Google?",
                fonte,
                timeout=TIMEOUT_RESPOSTA,
                phrase_time_limit=LIMITE_FALA_LONGA,
            )
            if not termo:
                self.voz.falar("Não escutei nada. Pesquisa cancelada.")
                return True
            
            self.voz.falar("Verificando a segurança da sua pesquisa, um instante...")
            msg = self.web.pesquisar_google(termo, self.ia)
            self.voz.falar(msg)
            return True

        # Tocar no Spotify Desktop
        elif any(t in comando for t in ["spotify", "ouvir", "tocar", "escutar", "música", "musica", "som"]) and not any(t in comando for t in ["parar", "pausar", "despausar", "paus"]):
            if "youtube" not in comando and "vídeo" not in comando and "video" not in comando:
                comando_limpo = comando.replace("quero", "").replace("gostaria de", "").strip()
                artista = None
                for palavra in ["ouvir ", "tocar ", "escutar ", "colocar ", "põe ", "poe ", "música ", "musica ", "som "]:
                    if palavra in comando_limpo:
                        partes = comando_limpo.split(palavra, 1)
                        if len(partes) > 1:
                            candidato = partes[1].strip()
                            if candidato not in ["música", "musica", "som", "spotify", "uma música", "um som"]:
                                artista = candidato
                                break
                
                if not artista:
                    print("[AGUARDANDO MÚSICA/ARTISTA...]")
                    artista = self.perguntar(
                        "O que você deseja ouvir no Spotify?",
                        fonte,
                        timeout=TIMEOUT_RESPOSTA,
                        phrase_time_limit=LIMITE_FALA_LONGA,
                    )
                    if not artista:
                        self.voz.falar("Não consegui ouvir o que você quer tocar. Cancelado.")
                        return True
                        
                msg = self.web.tocar_spotify(artista)
                self.voz.falar(msg)
                return True

        # Vídeos no YouTube
        elif any(t in comando for t in ["youtube", "vídeo", "video", "assistir", "clipe"]):
            print("[AGUARDANDO NOME DO VÍDEO...]")
            video = self.perguntar(
                "Qual vídeo você deseja ver?",
                fonte,
                timeout=TIMEOUT_RESPOSTA,
                phrase_time_limit=LIMITE_FALA_LONGA,
            )
            if not video:
                self.voz.falar("Não consegui ouvir o nome do vídeo. Busca cancelada.")
                return True
            
            msg = self.web.tocar_youtube(video)
            self.voz.falar(msg)
            return True

        # Portal da Faculdade FIAP
        elif any(t in comando for t in ["portal", "faculdade", "fiap", "on fiap", "portal do aluno"]):
            self.voz.falar("Abrindo o portal da faculdade FIAP.")
            self.web.abrir_portal_fiap()
            return True

        return False

    def _tratar_desambiguacoes(self, comando: str, fonte) -> bool:
        """Resolve comandos curtos ou ambíguos perguntando a intenção do usuário."""
        # 1. Desambiguação de "Ler" (Agenda vs OCR)
        if comando in ["ler", "leia", "lê", "le", "ler a", "leia a", "ler o", "leia o"]:
            print("[AGUARDANDO DESAMBIGUAÇÃO DE LEITURA: AGENDA OU CÂMERA...]")
            resposta = self.perguntar(
                "Você deseja ler os eventos da agenda ou escanear um texto pela câmera?",
                fonte,
                timeout=TIMEOUT_RESPOSTA,
                phrase_time_limit=LIMITE_FALA_CURTA,
            )
            if not resposta:
                self.voz.falar("Não escutei. Operação de leitura cancelada.")
                return True
            resposta_limpa = resposta.lower()
            if any(t in resposta_limpa for t in ["agenda", "evento", "compromisso", "eventos"]):
                self.ler_agenda()
            elif any(t in resposta_limpa for t in ["câmera", "camera", "escanear", "texto", "papel", "foto"]):
                self.ler_texto_camera()
            else:
                self.voz.falar("Opção não reconhecida. Cancelando a leitura.")
            return True

        # 2. Desambiguação de "Cadastrar" (Agenda vs Rosto)
        elif any(t in comando for t in ["cadastrar", "registrar", "gravar", "novo evento", "agendar"]):
            print("[AGUARDANDO DESAMBIGUAÇÃO: EVENTO OU ROSTO...]")
            resposta = self.perguntar(
                "Você deseja cadastrar um evento na agenda ou cadastrar um rosto?",
                fonte,
                timeout=TIMEOUT_RESPOSTA,
                phrase_time_limit=LIMITE_FALA_CURTA,
            )
            if not resposta:
                self.voz.falar("Não escutei. Operação de cadastro cancelada.")
                return True
                
            resposta_limpa = resposta.lower()
            if any(t in resposta_limpa for t in ["rosto", "facial", "face", "pessoa"]):
                self.cadastrar_facial(fonte)
            elif any(t in resposta_limpa for t in ["evento", "agenda", "compromisso"]):
                self.cadastrar_evento(fonte)
            else:
                self.voz.falar("Comando não reconhecido. Cancelando o cadastro.")
            return True

        # 3. Desambiguação de "Apagar" / "Remover"
        elif comando in ["apagar", "remover", "limpar", "excluir", "deletar", "apaga", "remove", "limpa", "exclui", "deleta"]:
            print("[AGUARDANDO DESAMBIGUAÇÃO DE EXCLUSÃO...]")
            resposta = self.perguntar(
                "Você deseja apagar a agenda, as fotos ou os cadastros de rosto?",
                fonte,
                timeout=TIMEOUT_RESPOSTA,
                phrase_time_limit=LIMITE_FALA_CURTA,
            )
            if not resposta:
                self.voz.falar("Não escutei. Operação de exclusão cancelada.")
                return True
            resposta_limpa = resposta.lower()
            if any(t in resposta_limpa for t in ["agenda", "evento", "compromisso", "eventos"]):
                self.limpar_agenda()
            elif any(t in resposta_limpa for t in ["foto", "fotos", "print", "prints", "imagem", "imagens"]):
                self.limpar_fotos()
            elif any(t in resposta_limpa for t in ["rosto", "rostos", "facial", "face", "biometria", "cadastro", "rust"]):
                self.remover_cadastro_facial(fonte)
            else:
                self.voz.falar("Opção não reconhecida. Cancelando a exclusão.")
            return True

        return False

    def processar_comando(self, comando: str, fonte) -> str | None:
        """
        Método central de despacho de comandos (Dispatcher Pattern).
        Encaminha a intenção para o módulo especializado correspondente.
        """
        comando = comando.strip().lower()

        if not comando:
            self.voz.falar("Fala comigo! O que o Bruxo pode fazer por você?")
            return None

        # 1. Encerramento da aplicação
        if any(t in comando for t in ["tchau", "desligar", "sair", "encerrar", "desliga"]):
            self.voz.falar("Bruxo saindo... KABUUUM!", aguardar=True)
            return "sair"

        # 2. Utilitários (Apresentação, Ajuda, Horas, Data)
        if self._tratar_utilitarios(comando):
            return None

        # 3. Easter Eggs e Piadas
        if self.easter_eggs.processar(comando, self.voz):
            return None

        # 4. Agenda e Compromissos
        if self._tratar_agenda(comando, fonte):
            return None

        # 5. Biometria e Visão Computacional
        if self._tratar_biometria(comando, fonte):
            return None

        # 6. Mídia, Hardware e Sistema
        if self._tratar_midia_e_sistema(comando, fonte):
            return None

        # 7. Web, Streaming e APIs
        if self._tratar_web_e_servicos(comando, fonte):
            return None

        # 8. Desambiguações de termos genéricos ("ler", "cadastrar", "apagar")
        if self._tratar_desambiguacoes(comando, fonte):
            return None

        # 9. Fallback: Inteligência Artificial Generativa (Groq Cloud)
        print(f"[PENSANDO COM GROQ IA]: Analisando \"{comando}\"...")
        resposta_ia = self.ia.perguntar(comando)
        self.voz.falar(resposta_ia)
        return None

    # ==========================================
    # LOOP PRINCIPAL DE ESCUTA
    # ==========================================

    def iniciar(self):
        with sr.Microphone() as fonte:
            separador = "=" * 60
            print(separador)
            print("[INICIO] ASSISTENTE VIRTUAL BRUXO")
            print(separador)
            print("[CALIBRANDO] Ajustando ruído ambiente do microfone... Aguarde 1s.")
            self.microfone.calibrar(fonte, duracao=1)
            print(f"[PRONTO] Bruxo pronto com voz masculina grave! Diga '{self.nome.capitalize()}'...")
            
            while True:
                try:
                    texto = self.microfone.escutar(fonte, timeout=TIMEOUT_PADRAO_ESCUTA, phrase_time_limit=LIMITE_FALA_PADRAO)

                    if not texto:
                        continue

                    gatilho_detectado, comando = self.microfone.verificar_wake_word(texto)

                    if not gatilho_detectado:
                        print(f"[OUVIDO (sem comando)]: \"{texto}\"")
                        continue

                    self.voz.parar()
                    print(f"\n[WAKE WORD DETECTADA]: \"{texto}\"")

                    status = self.processar_comando(comando, fonte)
                    if status == "sair":
                        print("[ENCERRADO] Assistente Bruxo finalizado com sucesso.")
                        break

                except KeyboardInterrupt:
                    print("\n[ENCERRADO] Assistente finalizado pelo teclado (Ctrl+C).")
                    break
                except Exception as e:
                    print(f"[AVISO]: {e}")
                    time.sleep(1)
