from groq import Groq
from src.config import GROQ_API_KEY, MODELO_GROQ_PRINCIPAL, MODELO_GROQ_FALLBACK


class ClienteIA:
    """
    Classe responsável pela comunicação com o modelo de IA generativa via Groq Cloud.
    Atende ao item 9 do Checkpoint 4.
    """

    def __init__(self, api_key: str = GROQ_API_KEY):
        self.api_key = api_key
        self.cliente = None
        self.modelo_principal = MODELO_GROQ_PRINCIPAL
        self.modelo_fallback = MODELO_GROQ_FALLBACK
        self._inicializar()

    def _inicializar(self):
        """Inicializa o cliente Groq se a chave estiver configurada."""
        if self.api_key:
            try:
                self.cliente = Groq(api_key=self.api_key)
                print("[GROQ IA]: Conexão com Groq Cloud ativada!")
            except Exception as e:
                print(f"[AVISO IA]: Erro ao inicializar Groq: {e}")

    def esta_disponivel(self) -> bool:
        """Verifica se o cliente Groq está pronto para uso."""
        return self.cliente is not None

    def perguntar(self, pergunta: str) -> str:
        """
        Envia uma pergunta para o modelo de linguagem e retorna a resposta formatada
        de maneira concisa para síntese de voz.
        """
        if not self.esta_disponivel():
            return "A inteligência artificial não está configurada no momento."

        prompt_sistema = (
            "Você é o Bruxo, um assistente virtual masculino, inteligente, direto e confiante. "
            "Responda à pergunta do usuário de forma clara e concisa (máximo 2 a 3 frases curtas), "
            "ideal para ser falada em voz alta por um sintetizador de voz. "
            "Nunca use formatações como asteriscos, markdown, tabelas ou emojis."
        )

        try:
            chat_completion = self.cliente.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": pergunta}
                ],
                model=self.modelo_principal,
                temperature=0.7,
                max_tokens=200
            )
            resposta = chat_completion.choices[0].message.content.strip()
            return self._limpar_markdown(resposta)

        except Exception:
            # Fallback para o modelo secundário
            try:
                chat_completion = self.cliente.chat.completions.create(
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": pergunta}
                    ],
                    model=self.modelo_fallback,
                    temperature=0.7,
                    max_tokens=200
                )
                resposta = chat_completion.choices[0].message.content.strip()
                return self._limpar_markdown(resposta)
            except Exception as e:
                print(f"[ERRO IA]: Falha na resposta da IA: {e}")
                return "Tive um problema ao consultar a inteligência artificial. Tente novamente."

    @staticmethod
    def _limpar_markdown(texto: str) -> str:
        """Remove símbolos que possam atrapalhar o sintetizador de voz."""
        return texto.replace("*", "").replace("#", "").replace("`", "").replace("~", "")
