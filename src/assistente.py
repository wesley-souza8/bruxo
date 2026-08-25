import datetime
import time
import speech_recognition as sr
from src.agenda import GerenciadorAgenda
from src.captura import GerenciadorCaptura
from src.config import NOME_ASSISTENTE
from src.ia_groq import ClienteIA
from src.microfone import OuvinteMicrofone
from src.voz import SintetizadorVoz


class AssistenteBruxo:
    """
    Classe orquestradora da Assistente Virtual Bruxo (Projeto F.R.I.D.A.Y. - CP4)
    
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
        """Item 2: Pergunta o evento, escuta e cadastra em agenda.txt."""
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
        """Item 3: Abre agenda.txt e lê todos os eventos."""
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
        """Item 8: Apaga os eventos sem excluir o arquivo agenda.txt."""
        if self.agenda.limpar_agenda():
            self.voz.falar("Sua agenda foi limpa com sucesso.")
            print("[AGENDA LIMPA] Todos os eventos foram removidos.")
        else:
            self.voz.falar("Houve um erro ao limpar sua agenda.")

    # ==========================================
    # CAPTURA E LIMPEZA DE IMAGENS (Item 10)
    # ==========================================

    def tirar_print(self):
        """Item 10: Tira screenshot e salva na pasta img/."""
        caminho = self.captura.tirar_print()
        if caminho:
            self.voz.falar("Print da tela tirado e salvo com sucesso na pasta imagens.")
        else:
            self.voz.falar("Houve um erro ao tentar tirar o print da tela.")

    def limpar_fotos(self):
        """Apaga todas as imagens salvas dentro da pasta img/."""
        qtd, sucesso = self.captura.limpar_fotos()
        if sucesso:
            if qtd == 0:
                self.voz.falar("A pasta de imagens já está vazia.")
            else:
                self.voz.falar(f"Todas as {qtd} imagens foram apagadas da pasta.")
        else:
            self.voz.falar("Houve um erro ao limpar as imagens.")

    # ==========================================
    # LISTA DE COMANDOS / AJUDA
    # ==========================================

    def listar_comandos(self):
        """Exibe o menu no console e resume as opções por voz."""
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
            "  7. 'Bruxo, limpar fotos' (apaga imagens de img/)\n"
            "  8. 'Bruxo, Alanzoka' (Easter Egg)\n"
            "  9. 'Bruxo, <qualquer pergunta>' (Groq IA)\n"
            "  10. 'Bruxo, listar comandos' (ou 'ajuda')\n"
            "  11. 'Bruxo, tchau' (ou 'desligar')\n"
            f"{separador}\n"
        )
        print(menu)

        texto_voz = (
            "Meus comandos disponíveis são: você pode perguntar as horas, "
            "saber a data de hoje, gerenciar sua agenda, tirar ou limpar prints da tela, "
            "fazer qualquer pergunta para a inteligência artificial, "
            "ou dizer tchau para desligar. O que você manda?"
        )
        self.voz.falar(texto_voz)

    # ==========================================
    # PROCESSAMENTO DE COMANDOS
    # ==========================================

    def processar_comando(self, comando: str, fonte) -> str | None:
        comando = comando.strip().lower()

        if not comando:
            self.voz.falar("Fala comigo! O que o Bruxo pode fazer por você?")
            return None

        # 1. LISTAR COMANDOS / AJUDA
        if any(termo in comando for termo in [
            "comando", "comandos", "ajuda", "menu", "o que você pode fazer",
            "o que voce pode fazer", "o que você faz", "o que voce faz",
            "quais são seus", "quais sao seus", "opções", "opcoes"
        ]):
            self.listar_comandos()

        # 2. LIMPAR FOTOS / IMAGENS DE IMG/
        elif any(termo in comando for termo in [
            "limpar fotos", "limpar imagens", "limpar prints", "apagar fotos",
            "apagar imagens", "apagar prints", "deletar fotos", "deletar imagens",
            "limpar a pasta de imagens", "limpar pasta imagens"
        ]):
            self.limpar_fotos()

        # 3. TIRAR PRINT DA TELA (Item 10)
        elif any(termo in comando for termo in [
            "print", "tirar print", "foto da tela", "captura de tela",
            "capturar tela", "screenshot", "print da tela"
        ]):
            self.tirar_print()

        # 4. CADASTRAR EVENTO NA AGENDA (Item 2)
        elif any(termo in comando for termo in [
            "cadastrar", "gravar evento", "gravar na agenda", "anotar",
            "novo evento", "adicionar evento", "agendar"
        ]):
            self.cadastrar_evento(fonte)

        # 5. LER AGENDA (Item 3)
        elif any(termo in comando for termo in [
            "ler agenda", "lê agenda", "lê da agenda", "le da agenda", "ler da agenda",
            "ver agenda", "mostrar agenda", "minha agenda", "quais são os eventos",
            "quais sao os eventos", "eventos da agenda"
        ]):
            self.ler_agenda()

        # 6. LIMPAR AGENDA (Item 8)
        elif any(termo in comando for termo in [
            "limpar agenda", "apagar agenda", "esvaziar agenda", "deletar agenda", "limpar a agenda"
        ]):
            self.limpar_agenda()

        # 7. HORAS (Item 4)
        elif any(termo in comando for termo in [
            "hora", "horas", "que horas são", "que horas sao"
        ]):
            self.voz.falar(self.obter_horas())

        # 8. DATA (Item 5)
        elif any(termo in comando for termo in [
            "dia", "data", "que dia é hoje", "que dia e hoje"
        ]):
            self.voz.falar(self.obter_data())

        # 9. EASTER EGG ALANZOKA
        elif any(termo in comando for termo in ["alanzoka", "alan zoka", "alanzoca"]):
            self.voz.falar("Nextage, bebê!")

        # 10. ENCERRAR COM DESPEDIDA KABUM
        elif any(termo in comando for termo in [
            "tchau", "desligar", "sair", "encerrar", "fechar", "valeu"
        ]):
            self.voz.falar("Bruxo saindo... KABUUUM!", aguardar=True)
            return "sair"

        # 11. IA GENERATIVA (GROQ) - Responde qualquer dúvida! (Item 9)
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
            print("[INICIO] PROJETO F.R.I.D.A.Y. - ASSISTENTE VIRTUAL BRUXO")
            print(separador)
            print("[CALIBRANDO] Ajustando ruído ambiente do microfone... Aguarde 1s.")
            self.microfone.calibrar(fonte, duracao=1)
            print(f"[PRONTO] Bruxo pronto com voz masculina grave! Diga '{self.nome.capitalize()}'...")
            print("\nExemplos de comandos:")
            print("   - 'Bruxo, que horas são?'")
            print("   - 'Bruxo, tirar um print da tela'")
            print("   - 'Bruxo, limpar fotos' (apaga imagens salvas)")
            print("   - 'Bruxo, me conte uma curiosidade' (Groq IA)")
            print("   - 'Bruxo, Alanzoka' -> 'Nextage, bebê!'")
            print("   - 'Bruxo, tchau' -> 'Bruxo saindo... KABUUUM!'")
            print(separador)

            while True:
                try:
                    texto = self.microfone.escutar(fonte, timeout=5, phrase_time_limit=7)

                    if not texto:
                        continue

                    # REGRA DO CP4: Se não falar a wake word, apenas imprime na tela sem ação
                    gatilho_detectado, comando = self.microfone.verificar_wake_word(texto)

                    if not gatilho_detectado:
                        print(f"[OUVIDO (sem comando)]: \"{texto}\"")
                        continue

                    # Interrompe fala anterior
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
