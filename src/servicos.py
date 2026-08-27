import urllib.parse
import urllib.request
import re
import requests
import webbrowser
import os
import time
import pyautogui
from src.config import OPENWEATHER_API_KEY

class ServicosWeb:
    """
    Classe responsável por integrações web.
    Lida com APIs (Clima, Dólar) e automação de navegação web (Google, YouTube, Spotify, Portal).
    """

    def obter_clima(self, cidade: str) -> str:
        if not OPENWEATHER_API_KEY:
            return "A chave da API de clima não está configurada no sistema."
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
            res = requests.get(url).json()
            if res.get("cod") != 200:
                return "Não consegui encontrar os dados de temperatura para essa cidade."
            temp = round(res["main"]["temp"])
            desc = res["weather"][0]["description"]
            return f"A temperatura atual em {cidade} é de {temp} graus, com {desc}."
        except Exception as e:
            print(f"[ERRO CLIMA]: {e}")
            return "Houve um erro ao consultar o servidor de clima."

    def obter_cotacao_dolar(self) -> str:
        try:
            url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
            res = requests.get(url).json()
            valor = float(res["USDBRL"]["bid"])
            return f"A cotação atual do dólar é de {valor:.2f} reais.".replace(".", ",")
        except Exception as e:
            print(f"[ERRO COTAÇÃO]: {e}")
            return "Não consegui acessar a cotação do dólar no momento."

    def tocar_youtube(self, video: str) -> str:
        try:
            query = urllib.parse.quote(video)
            url = f"https://www.youtube.com/results?search_query={query}"
            html = urllib.request.urlopen(url)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            if video_ids:
                webbrowser.open(f"https://www.youtube.com/watch?v={video_ids[0]}")
                return f"Pesquisando e abrindo o vídeo: {video}"
            return "Não encontrei nenhum vídeo com esse nome."
        except Exception as e:
            print(f"[ERRO YOUTUBE]: {e}")
            return "Ocorreu um erro ao tentar abrir o vídeo."

    def tocar_spotify(self, artista: str) -> str:
        try:
            query = urllib.parse.quote(artista)
            os.system(f"start spotify:search:{query}")
            
            # Aguarda o Spotify abrir e renderizar a busca
            time.sleep(5)
            
            pyautogui.FAILSAFE = False
            # Pressiona tab algumas vezes para sair da barra de busca e focar no 'Melhor Resultado'
            pyautogui.press('tab', presses=3, interval=0.3)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.press('enter') # Confirma o play no cartão selecionado
            
            return f"Abrindo o Spotify para tocar {artista}."
        except Exception as e:
            print(f"[ERRO SPOTIFY]: {e}")
            return "Houve um erro ao tentar controlar o Spotify."

    def pesquisar_google(self, termo: str, ia) -> str:
        prompt = f"Avalie a segurança do termo de pesquisa: '{termo}'. Se contiver pornografia, violência explícita, apologia a crimes ou conteúdo ilegal, responda APENAS 'BLOQUEAR'. Caso seja seguro, responda APENAS 'PERMITIR'."
        resposta = ia.perguntar(prompt).strip().upper()
        if "PERMITIR" not in resposta or "BLOQUEAR" in resposta:
            return "Desculpe, não posso pesquisar isso. O termo viola as políticas de segurança."
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(termo)}")
        return "Tudo certo, abrindo o Google."

    def abrir_portal_fiap(self):
        webbrowser.open("https://on.fiap.com.br/")


class ControleSistema:
    """
    Classe responsável por automação do sistema operacional (hardware/mídia).
    """
    def aumentar_volume(self):
        pyautogui.press('volumeup', presses=5)

    def diminuir_volume(self):
        pyautogui.press('volumedown', presses=5)

    def mutar_desmutar(self):
        pyautogui.press('volumemute')

    def pausar_despausar(self):
        pyautogui.press('playpause')
