import os
from src.config import ARQUIVO_AGENDA


class GerenciadorAgenda:
    """
    Classe responsável pelas operações de persistência de eventos na agenda (agenda.txt).
    Atende aos itens 2, 3 e 8 do Checkpoint 4.
    """

    def __init__(self, caminho_arquivo: str = ARQUIVO_AGENDA):
        self.caminho = caminho_arquivo
        self._garantir_arquivo()

    def _garantir_arquivo(self):
        """Garante que o arquivo agenda.txt exista no disco."""
        if not os.path.exists(self.caminho):
            with open(self.caminho, "w", encoding="utf-8") as f:
                pass

    def cadastrar_evento(self, evento: str) -> bool:
        """Adiciona um novo evento ao arquivo agenda.txt."""
        try:
            with open(self.caminho, "a", encoding="utf-8") as f:
                f.write(f"{evento}\n")
            return True
        except Exception as e:
            print(f"[ERRO AGENDA]: Falha ao salvar evento: {e}")
            return False

    def ler_eventos(self) -> list[str]:
        """Lê e retorna a lista de todos os eventos cadastrados."""
        try:
            if not os.path.exists(self.caminho):
                return []
            with open(self.caminho, "r", encoding="utf-8") as f:
                return [linha.strip() for linha in f.readlines() if linha.strip()]
        except Exception as e:
            print(f"[ERRO AGENDA]: Falha ao ler agenda: {e}")
            return []

    def limpar_agenda(self) -> bool:
        """Apaga o conteúdo da agenda sem deletar o arquivo do disco."""
        try:
            with open(self.caminho, "w", encoding="utf-8") as f:
                pass
            return True
        except Exception as e:
            print(f"[ERRO AGENDA]: Falha ao limpar agenda: {e}")
            return False
