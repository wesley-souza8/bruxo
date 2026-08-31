import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

# Caminhos base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_AGENDA = os.path.join(BASE_DIR, "agenda.txt")
PASTA_IMG = os.path.join(BASE_DIR, "img")

# Configurações do Assistente
NOME_ASSISTENTE = "bruxo"
NOMES_GATILHO = [NOME_ASSISTENTE, "o bruxo", "bruxão", "bruxao"]

# Configurações de Voz (Edge-TTS Neural)
VOZ_NEURAL = "pt-BR-AntonioNeural"
PITCH_GRAVE = "-12Hz"
VELOCIDADE_FALA = "+0%"

# Configurações de IA e APIs
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODELO_GROQ_PRINCIPAL = "openai/gpt-oss-120b"
MODELO_GROQ_FALLBACK = "qwen/qwen3.6-27b"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AWESOME_API_KEY = os.getenv("AWESOME_API_KEY")

# Configurações de Captação e Microfone (Timeouts em segundos)
TIMEOUT_PADRAO_ESCUTA = 5        # Timeout do loop contínuo de escuta (wake word)
TIMEOUT_RESPOSTA = 10            # Delay/tempo limite para o usuário responder a uma pergunta
LIMITE_FALA_PADRAO = 7           # Duração máxima de fala em escuta contínua
LIMITE_FALA_CURTA = 7            # Duração máxima para respostas curtas (ex: nomes, cidades, opções)
LIMITE_FALA_LONGA = 12           # Duração máxima para descrições longas (ex: eventos, buscas)
