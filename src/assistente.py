import datetime
import time
import webbrowser
import urllib.parse
import requests
import pyautogui
import speech_recognition as sr
from src.agenda import GerenciadorAgenda
from src.captura import GerenciadorCaptura
from src.config import NOME_ASSISTENTE, OPENWEATHER_API_KEY
from src.ia_groq import ClienteIA
from src.microfone import OuvinteMicrofone
from src.voz import SintetizadorVoz


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
    # YOUTUBE E GOOGLE (NAVEGADOR)
    # ==========================================

    def buscar_video_youtube(self, fonte):
        self.voz.falar("Qual vídeo você deseja ver?", aguardar=True)
        print("[AGUARDANDO NOME DO VÍDEO...]")
        video = self.microfone.escutar(fonte, timeout=7, phrase_time_limit=10)
        if not video:
            self.voz.falar("Não consegui ouvir o nome do vídeo. Busca cancelada.")
            return
        print(f"[VÍDEO TRANSCRITO]: \"{video}\"")
        self.voz.falar(f"Abrindo o YouTube para pesquisar por: {video}")
        query = urllib.parse.quote(video)
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

    def buscar_google(self, fonte):
        self.voz.falar("O que você deseja pesquisar no Google?", aguardar=True)
        print("[AGUARDANDO TERMO DE BUSCA...]")
        termo = self.microfone.escutar(fonte, timeout=7, phrase_time_limit=10)
        if not termo:
            self.voz.falar("Não escutei nada. Pesquisa cancelada.")
            return
            
        print(f"[TERMO TRANSCRITO]: \"{termo}\"")
        self.voz.falar("Verificando a segurança da sua pesquisa, um instante...")
        
        # Faz a validação chamando a IA
        prompt = f"Avalie a segurança do termo de pesquisa: '{termo}'. Se contiver pornografia, violência explícita, apologia a crimes ou conteúdo ilegal, responda APENAS 'BLOQUEAR'. Caso seja seguro, responda APENAS 'PERMITIR'."
        resposta_seguranca = self.ia.perguntar(prompt).strip().upper()
        
        # Se a IA se recusar a responder (filtro próprio dela) ou responder BLOQUEAR, nós bloqueamos.
        if "PERMITIR" not in resposta_seguranca or "BLOQUEAR" in resposta_seguranca:
            self.voz.falar("Desculpe, não posso pesquisar isso. O termo viola as políticas de segurança.")
        else:
            self.voz.falar("Tudo certo, abrindo o Google.")
            query = urllib.parse.quote(termo)
            webbrowser.open(f"https://www.google.com/search?q={query}")

    def abrir_portal_fiap(self):
        self.voz.falar("Abrindo o portal da faculdade FIAP.")
        webbrowser.open("https://on.fiap.com.br/")

    # ==========================================
    # CLIMA E COTAÇÃO (APIS)
    # ==========================================

    def obter_clima(self, fonte):
        self.voz.falar("De qual cidade você quer saber a temperatura?", aguardar=True)
        print("[AGUARDANDO NOME DA CIDADE...]")
        cidade = self.microfone.escutar(fonte, timeout=5, phrase_time_limit=7)
        if not cidade:
            self.voz.falar("Não entendi a cidade. Busca de clima cancelada.")
            return

        print(f"[CIDADE TRANSCRITA]: \"{cidade}\"")
        if not OPENWEATHER_API_KEY:
            self.voz.falar("A chave da API de clima não está configurada no sistema.")
            return
            
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
            res = requests.get(url).json()
            if res.get("cod") != 200:
                self.voz.falar("Não consegui encontrar os dados de temperatura para essa cidade.")
                return
            temp = round(res["main"]["temp"])
            desc = res["weather"][0]["description"]
            self.voz.falar(f"A temperatura atual em {cidade} é de {temp} graus, com {desc}.")
        except Exception as e:
            print(f"[ERRO CLIMA]: {e}")
            self.voz.falar("Houve um erro ao consultar o servidor de clima.")

    def obter_cotacao_dolar(self):
        try:
            url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
            res = requests.get(url).json()
            valor = float(res["USDBRL"]["bid"])
            valor_formatado = f"{valor:.2f}".replace(".", ",")
            self.voz.falar(f"A cotação atual do dólar é de {valor_formatado} reais.")
        except Exception as e:
            print(f"[ERRO COTAÇÃO]: {e}")
            self.voz.falar("Não consegui acessar a cotação do dólar no momento.")

    # ==========================================
    # CONTROLE DE SISTEMA (VOLUME)
    # ==========================================

    def controlar_volume(self, comando: str):
        if any(t in comando for t in ["aumentar", "aumente", "sobe", "subir", "mais alto"]):
            pyautogui.press('volumeup', presses=5) # ~10% de aumento (cada press é 2%)
            self.voz.falar("Aumentando o volume em 10%.")
        elif any(t in comando for t in ["diminuir", "diminua", "abaixa", "abaixar", "mais baixo"]):
            pyautogui.press('volumedown', presses=5) # ~10% de redução
            self.voz.falar("Diminuindo o volume em 10%.")
        elif any(t in comando for t in ["mutar", "mudo", "silenciar"]):
            pyautogui.press('volumemute')
            self.voz.falar("Volume mutado.")
        elif any(t in comando for t in ["desmutar", "voltar som", "tirar mudo"]):
            pyautogui.press('volumemute')
            self.voz.falar("Som restaurado.")
        else:
            self.voz.falar("Não entendi se devo aumentar, diminuir ou mutar o volume.")


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
            " 14. 'Bruxo, Alanzoka' (Easter Egg)\n"
            " 15. 'Bruxo, <qualquer pergunta>' (Groq IA)\n"
            " 16. 'Bruxo, tchau' (ou 'desligar')\n"
            f"{separador}\n"
        )
        print(menu)
        texto_voz = "Meus novos comandos incluem clima, dólar, volume, abrir portal, google, youtube, agenda e inteligência artificial."
        self.voz.falar(texto_voz)

    # ==========================================
    # PROCESSAMENTO DE COMANDOS
    # ==========================================

    def processar_comando(self, comando: str, fonte) -> str | None:
        comando = comando.strip().lower()

        if not comando:
            self.voz.falar("Fala comigo! O que o Bruxo pode fazer por você?")
            return None

        # LISTAR COMANDOS
        if any(t in comando for t in ["comando", "comandos", "ajuda", "menu"]):
            self.listar_comandos()

        # CLIMA
        elif any(t in comando for t in ["clima", "temperatura", "previsão", "previsao", "tempo"]):
            self.obter_clima(fonte)

        # COTAÇÃO DO DÓLAR
        elif any(t in comando for t in ["dólar", "dolar", "cotação"]):
            self.obter_cotacao_dolar()

        # VOLUME
        elif any(t in comando for t in ["volume", "mutar", "mudo", "som", "desmutar"]):
            self.controlar_volume(comando)

        # ABRIR PORTAL DA FACULDADE
        elif any(t in comando for t in ["portal", "faculdade", "fiap", "on fiap", "portal do aluno"]):
            self.abrir_portal_fiap()

        # PESQUISAR NO GOOGLE
        elif any(t in comando for t in ["google", "pesquisar na internet"]):
            self.buscar_google(fonte)

        # LIMPAR FOTOS
        elif any(t in comando for t in ["limpar fotos", "apagar fotos", "limpar prints"]):
            self.limpar_fotos()

        # TIRAR PRINT
        elif any(t in comando for t in ["print", "captura de tela", "tirar foto da tela"]):
            self.tirar_print()

        # CADASTRAR EVENTO
        elif any(t in comando for t in ["cadastrar", "novo evento", "agendar"]):
            self.cadastrar_evento(fonte)

        # LER AGENDA
        elif any(t in comando for t in ["ler agenda", "ver agenda"]):
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
        elif any(t in comando for t in ["alanzoka", "alan zoka"]):
            self.voz.falar("Nextage, bebê!")

        # YOUTUBE
        elif any(t in comando for t in ["youtube", "vídeo", "video", "assistir", "clipe"]):
            self.buscar_video_youtube(fonte)

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
