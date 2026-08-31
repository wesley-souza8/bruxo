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
        """Garante que o diretório e o arquivo agenda.txt existam no disco."""
        try:
            diretorio_pai = os.path.dirname(os.path.abspath(self.caminho))
            if diretorio_pai and not os.path.exists(diretorio_pai):
                os.makedirs(diretorio_pai, exist_ok=True)
            if not os.path.exists(self.caminho):
                with open(self.caminho, "w", encoding="utf-8") as f:
                    pass
        except Exception as e:
            print(f"[AVISO AGENDA]: Falha ao verificar/criar arquivo: {e}")

    def cadastrar_evento(self, evento: str) -> bool:
        """Adiciona um novo evento ao arquivo agenda.txt garantindo formatação correta."""
        try:
            self._garantir_arquivo()
            conteudo_existente = ""
            if os.path.exists(self.caminho):
                with open(self.caminho, "r", encoding="utf-8") as f:
                    conteudo_existente = f.read()

            evento_limpo = evento.strip()
            if not evento_limpo:
                return False

            with open(self.caminho, "a", encoding="utf-8") as f:
                if conteudo_existente and not conteudo_existente.endswith("\n"):
                    f.write("\n")
                f.write(f"{evento_limpo}\n")
            return True
        except Exception as e:
            print(f"[ERRO AGENDA]: Falha ao salvar evento: {e}")
            return False

    def ler_eventos(self) -> list[str]:
        """Lê e retorna a lista de todos os eventos cadastrados."""
        try:
            if not os.path.exists(self.caminho):
                self._garantir_arquivo()
                return []
            with open(self.caminho, "r", encoding="utf-8-sig") as f:
                return [linha.strip() for linha in f.readlines() if linha.strip()]
        except Exception as e:
            print(f"[ERRO AGENDA]: Falha ao ler agenda: {e}")
            return []

    def limpar_agenda(self) -> bool:
        """Apaga o conteúdo da agenda sem deletar o arquivo do disco."""
        try:
            self._garantir_arquivo()
            with open(self.caminho, "w", encoding="utf-8") as f:
                pass
            return True
        except Exception as e:
            print(f"[ERRO AGENDA]: Falha ao limpar agenda: {e}")
            return False
