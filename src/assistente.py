import datetime
import time
import webbrowser
import speech_recognition as sr
from src.agenda import GerenciadorAgenda
from src.captura import GerenciadorCaptura
from src.config import NOME_ASSISTENTE
from src.ia_groq import ClienteIA
from src.microfone import OuvinteMicrofone
from src.voz import SintetizadorVoz
from src.reconhecimento import GerenciadorFacial
from src.leitura import LeitorTexto
from src.servicos import ServicosWeb, ControleSistema

class AssistenteBruxo:
    """
    Classe orquestradora da Assistente Virtual Bruxo.
    
    Responsabilidades:
    - Integrar módulos de voz, microfone, agenda, captura e inteligência artificial.
    - Executar o loop contínuo de escuta (estilo Alexa) com acionamento por Wake Word.
    - Processar intenções e comandos do usuário.
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
        self.voz.falar("Ok, qual evento devo cadastrar?", aguardar=True)
        print("[AGUARDANDO DESCRICAO DO EVENTO...]")

        evento = self.microfone.escutar(fonte, timeout=7, phrase_time_limit=10)

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
        self.voz.falar("Qual é o nome da pessoa que será cadastrada?", aguardar=True)
        print("[AGUARDANDO NOME PARA CADASTRO FACIAL...]")
        
        nome = self.microfone.escutar(fonte, timeout=5, phrase_time_limit=5)
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

    def remover_cadastro_facial(self, fonte):
        self.voz.falar("Você deseja apagar todos os cadastros ou de uma pessoa específica?", aguardar=True)
        print("[AGUARDANDO: TODOS OU ESPECÍFICO...]")
        resposta = self.microfone.escutar(fonte, timeout=5, phrase_time_limit=5)
        
        if not resposta:
            self.voz.falar("Não escutei sua resposta. Operação cancelada.")
            return
            
        resposta = resposta.lower()
        if any(t in resposta for t in ["todos", "geral", "todo mundo", "tudo", "ambos", "gerais"]):
            sucesso, msg = self.facial.apagar_cadastro(None)
            self.voz.falar(msg)
        elif any(t in resposta for t in ["específico", "uma pessoa", "alguém", "especifica", "específica", "um"]):
            self.voz.falar("Qual é o nome da pessoa que devo remover do sistema?", aguardar=True)
            print("[AGUARDANDO NOME PARA REMOVER...]")
            nome = self.microfone.escutar(fonte, timeout=5, phrase_time_limit=5)
            if not nome:
                self.voz.falar("Não escutei o nome. Cancelando.")
                return
            sucesso, msg = self.facial.apagar_cadastro(nome)
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
    # LISTA DE COMANDOS / AJUDA
    # ==========================================

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
            " 19. 'Bruxo, Alanzoka' / 'Pega no Breu' (Easter Eggs)\n"
            " 20. 'Bruxo, <qualquer pergunta>' (Groq IA)\n"
            " 21. 'Bruxo, tchau' (ou 'desligar')\n"
            f"{separador}\n"
        )
        print(menu)
        texto_voz = "Adicionei comandos de escaneamento de texto e reconhecimento facial à minha lista. Confira o terminal para mais detalhes."
        self.voz.falar(texto_voz)

    # ==========================================
    # PROCESSAMENTO DE COMANDOS
    # ==========================================

    def processar_comando(self, comando: str, fonte) -> str | None:
        comando = comando.strip().lower()

        if not comando:
            self.voz.falar("Fala comigo! O que o Bruxo pode fazer por você?")
            return None

        # ESCANEAR TEXTO / NÚMEROS (OCR)
        # Se contiver palavras de leitura, mas tiver 'agenda', ignora e deixa cair no bloco da agenda lá embaixo
        if any(t in comando for t in ["escanear", "modo leitura", "extrair", "o que está escrito", "ler", "leia", "lê", "le "]):
            if "agenda" not in comando and "evento" not in comando:
                self.ler_texto_camera()
                return None

        # LISTAR COMANDOS
        if any(t in comando for t in ["comando", "comandos", "ajuda", "menu"]):
            self.listar_comandos()

        # CLIMA
        elif any(t in comando for t in ["clima", "temperatura", "previsão", "previsao", "tempo"]):
            self.voz.falar("De qual cidade você quer saber a temperatura?", aguardar=True)
            print("[AGUARDANDO NOME DA CIDADE...]")
            cidade = self.microfone.escutar(fonte, timeout=5, phrase_time_limit=7)
            if not cidade:
                self.voz.falar("Não entendi a cidade. Busca de clima cancelada.")
                return None
            self.voz.falar(self.web.obter_clima(cidade))

        # COTAÇÃO DO DÓLAR
        elif any(t in comando for t in ["dólar", "dolar", "cotação"]):
            self.voz.falar(self.web.obter_cotacao_dolar())

        # VOLUME
        elif any(t in comando for t in ["volume", "mutar", "mudo", "som", "desmutar"]):
            if any(t in comando for t in ["aumentar", "aumente", "sobe", "subir", "mais alto"]):
                self.sistema.aumentar_volume()
                self.voz.falar("Aumentando o volume.")
            elif any(t in comando for t in ["diminuir", "diminua", "abaixa", "abaixar", "mais baixo"]):
                self.sistema.diminuir_volume()
                self.voz.falar("Diminuindo o volume.")
            elif any(t in comando for t in ["mutar", "mudo", "silenciar"]):
                self.sistema.mutar_desmutar()
                self.voz.falar("Volume mutado.")
            elif any(t in comando for t in ["desmutar", "voltar som", "tirar mudo"]):
                self.sistema.mutar_desmutar()
                self.voz.falar("Som restaurado.")
            else:
                self.voz.falar("Não entendi se devo aumentar, diminuir ou mutar o volume.")

        # ABRIR PORTAL DA FACULDADE
        elif any(t in comando for t in ["portal", "faculdade", "fiap", "on fiap", "portal do aluno"]):
            self.voz.falar("Abrindo o portal da faculdade FIAP.")
            self.web.abrir_portal_fiap()

        # SPOTIFY
        elif any(t in comando for t in ["spotify", "ouvir", "tocar", "escutar", "música", "musica", "som"]) and not any(t in comando for t in ["parar", "pausar", "despausar", "paus"]):
            # Garante que não confunda com comandos do youtube se a pessoa disser 'ouvir video'
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
                    self.voz.falar("O que você deseja ouvir no Spotify?", aguardar=True)
                    print("[AGUARDANDO MÚSICA/ARTISTA...]")
                    artista = self.microfone.escutar(fonte, timeout=5, phrase_time_limit=10)
                    if not artista:
                        self.voz.falar("Não consegui ouvir o que você quer tocar. Cancelado.")
                        return None
                        
                msg = self.web.tocar_spotify(artista)
                self.voz.falar(msg)
                return None

        # CONTROLE DE MÍDIA (PAUSAR/DESPAUSAR)
        elif any(t in comando for t in ["pausa", "despausa", "play", "parar", "continuar", "paus"]):
            self.sistema.pausar_despausar()
            self.voz.falar("Feito.")

        # PESQUISAR NO GOOGLE
        elif any(t in comando for t in ["google", "pesquisar na internet"]):
            self.voz.falar("O que você deseja pesquisar no Google?", aguardar=True)
            print("[AGUARDANDO TERMO DE Busca...]")
            termo = self.microfone.escutar(fonte, timeout=7, phrase_time_limit=10)
            if not termo:
                self.voz.falar("Não escutei nada. Pesquisa cancelada.")
                return None
            
            self.voz.falar("Verificando a segurança da sua pesquisa, um instante...")
            msg = self.web.pesquisar_google(termo, self.ia)
            self.voz.falar(msg)

        # LIMPAR FOTOS
        elif any(t in comando for t in ["limpar fotos", "apagar fotos", "limpar prints", "apagar imagens", "limpar imagens", "apagar foto", "limpar imagem"]):
            self.limpar_fotos()

        # TIRAR PRINT
        elif any(t in comando for t in ["print", "captura de tela", "tirar foto da tela", "prin"]):
            self.tirar_print()

        # CADASTRAR / REGISTRAR (EVENTO OU FACIAL)
        elif any(t in comando for t in ["cadastrar", "registrar", "gravar", "novo evento", "agendar", "reconhecimento facial"]):
            if any(t in comando for t in ["rosto", "facial", "face", "pessoa", "reconhecimento"]):
                self.cadastrar_facial(fonte)
            elif any(t in comando for t in ["evento", "agenda", "compromisso", "novo evento", "agendar"]):
                self.cadastrar_evento(fonte)
            else:
                self.voz.falar("Você deseja cadastrar um evento na agenda ou cadastrar um rosto?", aguardar=True)
                print("[AGUARDANDO DESAMBIGUAÇÃO: EVENTO OU ROSTO...]")
                resposta = self.microfone.escutar(fonte, timeout=5, phrase_time_limit=5)
                
                if not resposta:
                    self.voz.falar("Não escutei. Operação de cadastro cancelada.")
                    return None
                    
                resposta_limpa = resposta.lower()
                if any(t in resposta_limpa for t in ["rosto", "facial", "face", "pessoa"]):
                    self.cadastrar_facial(fonte)
                elif any(t in resposta_limpa for t in ["evento", "agenda", "compromisso"]):
                    self.cadastrar_evento(fonte)
                else:
                    self.voz.falar("Comando não reconhecido. Cancelando o cadastro.")

        # APAGAR CADASTRO (FACIAL)
        elif any(t in comando for t in ["apagar rosto", "apagar cadastro facial", "remover rosto", "deletar rosto", "excluir rosto", "apagar cadastro", "remover cadastro"]):
            self.remover_cadastro_facial(fonte)

        # QUEM SOU EU (RECONHECIMENTO FACIAL)
        elif any(t in comando for t in ["quem sou eu", "me reconhece", "reconhecer meu rosto", "qual o meu nome", "qual é o meu nome"]):
            self.identificar_usuario()

        # LER AGENDA
        elif any(t in comando for t in ["ler agenda", "ver agenda", "lê agenda", "le agenda", "ler a agenda"]) or ("agenda" in comando and any(t in comando for t in ["ler", "leia", "lê", "le ", "l"])):
            self.ler_agenda()

        # LIMPAR AGENDA
        elif any(t in comando for t in ["limpar agenda", "apagar agenda"]):
            self.limpar_agenda()

        # HORAS E DATA
        elif any(t in comando for t in ["hora", "horas"]):
            self.voz.falar(self.obter_horas())
        elif any(t in comando for t in ["dia", "data"]):
            self.voz.falar(self.obter_data())

        # EASTER EGG ALANZOKA
        elif any(t in comando for t in ["alanzoka", "alan zoka", "alanzo", "alan", "allan"]):
            self.voz.falar("Nextage, bebê!")

        # EASTER EGG PEGA NO BREU
        elif any(t in comando for t in ["pega no breu", "gaitaço", "gaitaco", "ronaldo", "agro pesca jacaré", "agro pesca jacare", "pega no bre"]):
            self.voz.falar("Abrindo o clássico para você!")
            webbrowser.open("https://www.youtube.com/watch?v=TFdO7oqkMzI")

        # YOUTUBE
        elif any(t in comando for t in ["youtube", "vídeo", "video", "assistir", "clipe"]):
            self.voz.falar("Qual vídeo você deseja ver?", aguardar=True)
            print("[AGUARDANDO NOME DO VÍDEO...]")
            video = self.microfone.escutar(fonte, timeout=7, phrase_time_limit=10)
            if not video:
                self.voz.falar("Não consegui ouvir o nome do vídeo. Busca cancelada.")
                return None
            
            msg = self.web.tocar_youtube(video)
            self.voz.falar(msg)

        # ENCERRAR
        elif any(t in comando for t in ["tchau", "desligar", "sair", "encerrar", "desliga"]):
            self.voz.falar("Bruxo saindo... KABUUUM!", aguardar=True)
            return "sair"

        # IA GENERATIVA (GROQ)
        else:
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
                    texto = self.microfone.escutar(fonte, timeout=5, phrase_time_limit=7)

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
