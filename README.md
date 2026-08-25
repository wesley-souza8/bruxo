# 🧙‍♂️ Assistente Virtual Bruxo

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq AI](https://img.shields.io/badge/AI-Groq%20Cloud%20LPU-orange.svg)](https://groq.com/)
[![Edge-TTS](https://img.shields.io/badge/TTS-Microsoft%20Neural-purple.svg)](https://github.com/rany2/edge-tts)

## 👥 Integrantes do Grupo

* Deivison Pertel – RM 550803
* Eduardo Akira Murata – RM 98713
* Wesley Souza de Oliveira – RM 97874

---

> **Turma:** 4ESR  
> **Matéria:** Project-Based Maker Lab  
> **Professor:** Hellynson Cassio Lana  
>   
> Aplicação orientada a objetos para reconhecimento de comandos de voz, síntese neural, gerenciamento de agenda, captura de tela, controle de sistema e inteligência artificial generativa.

---

## 📌 Sobre o Projeto

Inspirado na assistente **F.R.I.D.A.Y. (Sexta-Feira)** do Homem de Ferro, o **Bruxo** é um assistente virtual inteligente capaz de escutar o usuário continuamente em segundo plano, filtrando comandos através de uma **palavra de ativação (*Wake Word*)** e respondendo por voz masculina grave neural de forma não-bloqueante (*assíncrona / barge-in*).

---

## 🏗️ Arquitetura Orientada a Objetos (POO)

O projeto foi estruturado seguindo os princípios de modularidade, separação de responsabilidades (SOLID) e Orientação a Objetos:

```text
assistente/
│
├── .env                       # Variáveis de ambiente e chaves de API (ignorado pelo git)
├── .gitignore                 # Arquivos e pastas ignorados no repositório
├── requirements.txt           # Lista de dependências do projeto
├── main.py                    # Ponto de entrada (Entrypoint) da aplicação
├── agenda.txt                 # Armazenamento persistente de eventos da agenda
├── README.md                  # Documentação completa do projeto
│
├── img/                       # Diretório onde os prints da tela são salvos
│
└── src/                       # Código-fonte modular do assistente
    ├── __init__.py            # Inicializador do pacote Python
    ├── config.py              # Configurações globais, caminhos e constantes
    ├── voz.py                 # Classe SintetizadorVoz (Edge-TTS Neural + Pygame em memória RAM)
    ├── microfone.py           # Classe OuvinteMicrofone (SpeechRecognition + Wake Word)
    ├── agenda.py              # Classe GerenciadorAgenda (CRUD de eventos em agenda.txt)
    ├── captura.py             # Classe GerenciadorCaptura (Screenshot e Limpeza de fotos)
    ├── ia_groq.py             # Classe ClienteIA (Integração com Groq Cloud LPU)
    └── assistente.py          # Classe AssistenteBruxo (Orquestradora principal)
```

---

## 🚀 Funcionalidades e Tabela de Comandos

O assistente só responde quando acionado pela palavra de ativação: **"Bruxo"** (ou variações como *"O Bruxo"* / *"Bruxão"*). Frases ditas sem a palavra de ativação são apenas exibidas no terminal para monitoramento, sem executar ações.

| # | Comando Falado | Ação Executada |
|---|---|---|
| 1 | **"Bruxo, que horas são?"** | Informa as horas e minutos atuais por voz. |
| 2 | **"Bruxo, que dia é hoje?"** | Informa o dia, mês e ano atuais por voz. |
| 3 | **"Bruxo, cadastrar evento na agenda"** | Pergunta o evento, transcreve a resposta e salva em `agenda.txt`. |
| 4 | **"Bruxo, ler agenda"** | Lê todos os eventos salvos no arquivo `agenda.txt`. |
| 5 | **"Bruxo, limpar agenda"** | Esvazia o conteúdo do arquivo `agenda.txt` sem deletá-lo. |
| 6 | **"Bruxo, tirar um print da tela"** | Captura a tela e salva automaticamente com timestamp na pasta `img/`. |
| 7 | **"Bruxo, limpar fotos"** | Apaga todas as imagens salvas na pasta `img/`. |
| 8 | **"Bruxo, qual a temperatura?"** | Consulta a API OpenWeatherMap da cidade informada. |
| 9 | **"Bruxo, cotação do dólar"** | Consulta a AwesomeAPI e informa o valor atual do dólar. |
| 10 | **"Bruxo, aumentar/mutar volume"** | Controla o volume geral do Windows simulando teclas. |
| 11 | **"Bruxo, pesquisar no google"** | Faz busca no Google após IA validar se o termo é seguro/SFW. |
| 12 | **"Bruxo, pesquisar vídeo"** | Pergunta o nome e pesquisa vídeos diretamente no YouTube. |
| 13 | **"Bruxo, abrir portal da faculdade"**| Abre diretamente o site da FIAP no navegador. |
| 14 | **"Bruxo, Alanzoka"** | Responde *"Nextage, bebê!"* (Easter Egg). |
| 15 | **"Bruxo, [qualquer dúvida]"** | Consulta a IA Generativa (Groq Cloud) e responde por voz em < 1s. |
| 16 | **"Bruxo, tchau"** (ou *"desliga"*) | Responde *"Bruxo saindo... KABUUUM!"* e encerra a aplicação. |

---

## 🛠️ Tecnologias e Bibliotecas

* **Linguagem:** Python 3.10+
* **Reconhecimento de Fala (STT):** `SpeechRecognition` + `PyAudio`
* **Síntese de Voz (TTS):** `edge-tts` (Microsoft Neural Voice `pt-BR-AntonioNeural` com tom grave ajustado) + `gTTS` (fallback)
* **Reprodução de Áudio:** `pygame` (execução 100% em memória RAM via `io.BytesIO` sem bloqueio de arquivos)
* **Inteligência Artificial Generativa:** `groq` (Groq Cloud LPU API)
* **Requisições de APIs Externas:** `requests` (OpenWeatherMap, AwesomeAPI)
* **Captura de Tela e Controle de Sistema:** `pyautogui` + `Pillow`
* **Gerenciamento de Ambiente:** `python-dotenv`

---

## ⚙️ Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/wesley-souza8/bruxo.git
cd bruxo
```

### 2. Criar e ativar um ambiente virtual (Opcional, mas recomendado)
```bash
python -m venv venv

# No Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# No Linux/Mac:
source venv/bin/activate
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar as Chaves de API
Crie um arquivo `.env` na raiz do projeto e adicione suas chaves:
```env
GROQ_API_KEY=sua_chave_groq_aqui
OPENWEATHER_API_KEY=sua_chave_openweathermap_aqui
AWESOME_API_KEY=sua_chave_awesomeapi_aqui
```

---

## ▶️ Como Executar

Execute o comando principal:
```powershell
python main.py
```

1. Aguarde a calibração de 1 segundo do ruído ambiente do microfone.
2. Diga: *"Bruxo, listar comandos"* ou faça qualquer solicitação!
3. Para encerrar, diga: *"Bruxo, tchau"* ou pressione `Ctrl + C` no terminal.
