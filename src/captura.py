import datetime
import os
import pyautogui
from src.config import PASTA_IMG


class GerenciadorCaptura:
    """
    Classe responsável pela captura de tela e gerenciamento da pasta img/.
    Atende ao item 10 do Checkpoint 4 e funções de limpeza de imagens.
    """

    def __init__(self, pasta_img: str = PASTA_IMG):
        self.pasta_img = pasta_img
        os.makedirs(self.pasta_img, exist_ok=True)

    def tirar_print(self) -> str | None:
        """
        Captura a tela inteira e salva com carimbo de data/hora em img/.
        Retorna o caminho do arquivo salvo ou None em caso de erro.
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nome_arquivo = f"print_{timestamp}.png"
            caminho_completo = os.path.join(self.pasta_img, nome_arquivo)

            screenshot = pyautogui.screenshot()
            screenshot.save(caminho_completo)

            print(f"[PRINT SALVO]: {caminho_completo}")
            return caminho_completo
        except Exception as e:
            print(f"[ERRO CAPTURA]: Falha ao tirar print: {e}")
            return None

    def limpar_fotos(self) -> tuple[int, bool]:
        """
        Apaga todas as imagens (.png, .jpg, .jpeg) contidas na pasta img/.
        Retorna (quantidade_arquivos_removidos, sucesso).
        """
        try:
            if not os.path.exists(self.pasta_img):
                return 0, True

            arquivos = os.listdir(self.pasta_img)
            removidos = 0

            for arq in arquivos:
                caminho = os.path.join(self.pasta_img, arq)
                if os.path.isfile(caminho):
                    extensao = arq.lower().split(".")[-1]
                    if extensao in ["png", "jpg", "jpeg", "bmp", "webp"]:
                        os.remove(caminho)
                        removidos += 1

            print(f"[FOTOS LIMPAS]: {removidos} imagem(ns) removida(s) da pasta img/.")
            return removidos, True
        except Exception as e:
            print(f"[ERRO CAPTURA]: Falha ao limpar fotos: {e}")
            return 0, False
