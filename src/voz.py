import asyncio
import io
import threading
import time
import edge_tts
from gtts import gTTS
from pygame import mixer
from src.config import VOZ_NEURAL, PITCH_GRAVE, VELOCIDADE_FALA


class SintetizadorVoz:
    """
    Classe responsável pela síntese e reprodução de voz do assistente.
    Utiliza Edge-TTS (voz neural masculina grave) com fallback para gTTS.
    Permite reprodução assíncrona (não-bloqueante) e interrupção imediata.
    """

    def __init__(self):
        mixer.init()
        self.lock_audio = threading.Lock()
        self.thread_fala = None

    async def _gerar_audio_edge(self, texto: str) -> io.BytesIO:
        """Gera o áudio usando o serviço Neural Edge-TTS da Microsoft."""
        comunicador = edge_tts.Communicate(
            text=texto,
            voice=VOZ_NEURAL,
            pitch=PITCH_GRAVE,
            rate=VELOCIDADE_FALA
        )
        buffer = io.BytesIO()
        async for chunk in comunicador.stream():
            if chunk["type"] == "audio":
                buffer.write(chunk["data"])
        buffer.seek(0)
        return buffer

    def parar(self):
        """Interrompe imediatamente qualquer áudio em reprodução."""
        try:
            if mixer.get_init() and mixer.music.get_busy():
                mixer.music.stop()
        except Exception:
            pass

    def _tocar_audio(self, texto: str):
        """Gera e toca o áudio diretamente na memória RAM."""
        with self.lock_audio:
            try:
                try:
                    buffer_audio = asyncio.run(self._gerar_audio_edge(texto))
                except Exception:
                    # Fallback gTTS
                    buffer_audio = io.BytesIO()
                    tts = gTTS(text=texto, lang="pt", tld="com.br")
                    tts.write_to_fp(buffer_audio)
                    buffer_audio.seek(0)

                mixer.music.load(buffer_audio, "mp3")
                mixer.music.play()

                while mixer.music.get_busy():
                    time.sleep(0.05)

            except Exception as e:
                print(f"[ERRO VOZ]: {e}")

    def falar(self, texto: str, prefixo: str = "BRUXO", aguardar: bool = False):
        """
        Fala um texto.
        - aguardar=False: Executa em segundo plano sem travar o microfone.
        - aguardar=True: Espera o término da reprodução.
        """
        texto_limpo = texto.strip()
        # Tratamento para evitar quebra do console com caracteres não reconhecidos (ex: hifens especiais)
        try:
            print(f"[{prefixo}]: \"{texto_limpo}\"")
        except UnicodeEncodeError:
            texto_ascii = texto_limpo.encode('ascii', 'replace').decode('ascii')
            print(f"[{prefixo}]: \"{texto_ascii}\"")
            
        if not texto_limpo:
            return

        self.parar()

        if aguardar:
            self._tocar_audio(texto_limpo)
        else:
            self.thread_fala = threading.Thread(
                target=self._tocar_audio,
                args=(texto_limpo,),
                daemon=True
            )
            self.thread_fala.start()
