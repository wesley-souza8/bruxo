import speech_recognition as sr
from src.config import NOMES_GATILHO, TIMEOUT_PADRAO_ESCUTA, LIMITE_FALA_PADRAO


class OuvinteMicrofone:
    """
    Classe responsável pelo gerenciamento de áudio do microfone,
    calibração de ruído ambiente, transcrição e detecção da Wake Word.
    """

    def __init__(self):
        self.reconhecedor = sr.Recognizer()
        self.reconhecedor.energy_threshold = 300
        self.reconhecedor.dynamic_energy_threshold = True
        self.reconhecedor.pause_threshold = 1.0

    def calibrar(self, fonte, duracao: int = 1):
        """Ajusta os níveis de sensibilidade para o ruído ambiente."""
        self.reconhecedor.adjust_for_ambient_noise(fonte, duration=duracao)
        if self.reconhecedor.energy_threshold < 300:
            self.reconhecedor.energy_threshold = 300

    def escutar(self, fonte, timeout: int = TIMEOUT_PADRAO_ESCUTA, phrase_time_limit: int = LIMITE_FALA_PADRAO) -> str:
        """
        Escuta o microfone e transcreve a fala em texto (pt-BR).
        Retorna string vazia caso não haja fala ou ruído inaudível.
        """
        try:
            audio = self.reconhecedor.listen(fonte, timeout=timeout, phrase_time_limit=phrase_time_limit)
            texto = self.reconhecedor.recognize_google(audio, language="pt-BR")
            return texto.strip()
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except sr.RequestError as e:
            print(f"[AVISO MICROFONE]: Erro no serviço de voz: {e}")
            return ""

    def verificar_wake_word(self, texto: str) -> tuple[bool, str]:
        """
        Verifica se alguma variação do nome do assistente está presente no texto.
        Retorna (True, comando_extraido) se detectado, ou (False, texto_original).
        """
        texto_lower = texto.lower()
        for gatilho in NOMES_GATILHO:
            if gatilho in texto_lower:
                partes = texto_lower.split(gatilho, 1)
                comando = partes[1].strip() if len(partes) > 1 else ""
                return True, comando

        return False, texto
