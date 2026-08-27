# 🧙‍♂️ Assistente Virtual Bruxo

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq AI](https://img.shields.io/badge/AI-Groq%20Cloud%20LPU-orange.svg)](https://groq.com/)
[![Edge-TTS](https://img.shields.io/badge/TTS-Microsoft%20Neural-purple.svg)](https://github.com/rany2/edge-tts)
[![OpenCV](https://img.shields.io/badge/Vision-OpenCV-red.svg)](https://opencv.org/)

## 👥 Integrantes do Grupo

* Deivison Pertel – RM 550803
* Eduardo Akira Murata – RM 98713
* Wesley Souza de Oliveira – RM 97874

---

> **Turma:** 4ESR  
> **Matéria:** Project-Based Maker Lab  
> **Professor:** Hellynson Cassio Lana  
>   
> Aplicação orientada a objetos para reconhecimento de comandos de voz, síntese neural, gerenciamento de agenda, captura de tela, controle de sistema, inteligência artificial generativa e visão computacional (biometria e OCR).

---

## 📌 Sobre o Projeto

Inspirado na assistente **F.R.I.D.A.Y. (Sexta-Feira)** do Homem de Ferro, o **Bruxo** é um assistente virtual inteligente capaz de escutar o usuário continuamente em segundo plano, filtrando comandos através de uma **palavra de ativação (*Wake Word*)** e respondendo por voz masculina grave neural de forma assíncrona. O projeto implementa desde integrações com APIs Web até reconhecimento facial avançado usando IA.

---

## 🏗️ Arquitetura Orientada a Objetos (POO)

O projeto foi estruturado seguindo os princípios de modularidade, separação de responsabilidades (SOLID) e Orientação a Objetos:

```text
bruxo/
│
├── .env                       # Variáveis de ambiente e chaves de API (ignorado pelo git)
├── .gitignore                 # Arquivos e pastas ignorados no repositório
├── requirements.txt           # Lista de dependências do projeto
├── main.py                    # Ponto de entrada (Entrypoint) da aplicação
├── agenda.txt                 # Armazenamento persistente de eventos da agenda
├── README.md                  # Documentação completa do projeto
│
├── img/                       # Diretório onde os prints da tela são salvos
├── rostos/                    # Diretório onde os datasets de biometria facial são salvos
│
└── src/                       # Código-fonte modular do assistente
    ├── __init__.py            
    ├── config.py              # Configurações globais, caminhos e constantes
    ├── voz.py                 # SintetizadorVoz (Edge-TTS Neural + Pygame em RAM sem bloqueio)
    ├── microfone.py           # OuvinteMicrofone (SpeechRecognition + Wake Word)
    ├── agenda.py              # GerenciadorAgenda (CRUD persistente de eventos)
    ├── captura.py             # GerenciadorCaptura (Screenshot e Limpeza)
    ├── ia_groq.py             # ClienteIA (Integração com Groq Cloud LPU / Filtro de Conteúdo)
    ├── servicos.py            # ServicosWeb e ControleSistema (Integração Spotify, Navegador, APIs)
    ├── reconhecimento.py      # GerenciadorFacial (OpenCV, Captura Dinâmica, Treino LBPH)
    ├── leitura.py             # LeitorTexto (Escaneamento de texto com EasyOCR)
    └── assistente.py          # AssistenteBruxo (Classe Orquestradora principal)
```

---

## 🚀 Funcionalidades e Tabela de Comandos

O assistente só responde quando acionado pela palavra de ativação: **"Bruxo"** (ou variações como *"O Bruxo"* / *"Bruxão"*). Frases ditas sem a palavra de ativação são ignoradas e exibidas no terminal apenas para monitoramento.

| # | Comando Falado | Ação Executada |
|---|---|---|
| 1 | **"Bruxo, que horas são?"** | Informa as horas e minutos atuais por voz. |
| 2 | **"Bruxo, que dia é hoje?"** | Informa o dia, mês e ano atuais por voz. |
| 3 | **"Bruxo, cadastrar na agenda"** | Pergunta o evento, transcreve a resposta e salva em `agenda.txt`. Diferencia do cadastro facial inteligentemente. |
| 4 | **"Bruxo, ler agenda"** | Lê todos os eventos salvos no arquivo `agenda.txt`. |
| 5 | **"Bruxo, limpar agenda"** | Esvazia o conteúdo do arquivo `agenda.txt` sem deletá-lo. |
| 6 | **"Bruxo, tirar um print da tela"** | Captura a tela e salva automaticamente com timestamp na pasta `img/`. |
| 7 | **"Bruxo, limpar fotos"** | Apaga todas as imagens e fotos salvas na pasta `img/`. |
| 8 | **"Bruxo, previsão do tempo"** | Pergunta a cidade desejada e consulta a API da OpenWeather. |
| 9 | **"Bruxo, cotação do dólar"** | Consulta a AwesomeAPI e informa o valor atual do dólar. |
| 10 | **"Bruxo, aumentar/mutar volume"**| Controla o volume geral e play/pause de mídia do Windows simulando teclas. |
| 11 | **"Bruxo, pesquisar no google"** | Faz busca no navegador **após** a IA Groq validar se o termo é seguro/SFW. |
| 12 | **"Bruxo, pesquisar vídeo"** | Pergunta o nome e pesquisa vídeos diretamente no YouTube. |
| 13 | **"Bruxo, tocar no Spotify"** | Abre o Spotify Desktop via URI, pesquisa a música/artista e dá o play. |
| 14 | **"Bruxo, abrir portal da faculdade"**| Abre diretamente o site da FIAP no navegador. |
| 15 | **"Bruxo, cadastrar rosto"** | Liga a webcam, coleta 30 amostras do rosto do usuário e gera o dataset em `rostos/`. |
| 16 | **"Bruxo, quem sou eu?"** | Treina o modelo sob demanda e usa o HaarCascade + LBPH para dizer o seu nome. |
| 17 | **"Bruxo, apagar rosto"** | Remove o dataset biométrico de pessoas específicas ou apaga o sistema todo. |
| 18 | **"Bruxo, escanear texto"** | Abre a câmera, capta texto ou números da imagem e fala usando IA (EasyOCR). |
| 19 | **"Bruxo, [qualquer dúvida]"** | Consulta a IA Generativa (Llama-3) e responde por voz em < 1s, atuando como LLAma/ChatGPT. |
| 20 | **"Bruxo, tchau"** (ou *"desliga"*) | Responde *"Bruxo saindo... KABUUUM!"* e encerra a aplicação de forma segura. |

---

## 🛠️ Tecnologias e Bibliotecas

* **Linguagem:** Python 3.10+
* **Visão Computacional e OCR:** `opencv-contrib-python`, `numpy`, `easyocr`
* **Reconhecimento de Fala (STT):** `SpeechRecognition` + `PyAudio`
* **Síntese de Voz (TTS):** `edge-tts` (Microsoft Neural Voice `pt-BR-AntonioNeural` ajustado) + `gTTS` (fallback)
* **Inteligência Artificial Generativa:** `groq` (Groq Cloud LPU API - Llama 3)
* **Reprodução de Áudio:** `pygame` (execução 100% em memória RAM via `io.BytesIO`)
* **Captura de Tela e Controle de Sistema:** `pyautogui` + `Pillow`
* **Requisições e Automação Web:** `requests`, `pywhatkit`, `webbrowser`
* **Gerenciamento de Ambiente:** `python-dotenv`

---

## ⚙️ Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/wesley-souza8/bruxo.git
cd bruxo
```

### 2. Criar e ativar um ambiente virtual (Recomendado)
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
> **Nota de compatibilidade:** Assegure-se de usar a biblioteca `opencv-contrib-python`. Instalar apenas as versões básicas ou 'headless' do OpenCV impossibilitará o uso do módulo `cv2.face` (reconhecimento facial) e a abertura das janelas da webcam no sistema operacional.

### 4. Configurar as Chaves de API
Crie um arquivo `.env` na raiz do projeto e adicione suas chaves (use as APIs em sua cota gratuita):
```env
GROQ_API_KEY=sua_chave_groq_aqui
OPENWEATHER_API_KEY=sua_chave_openweathermap_aqui
```

---

## ▶️ Como Executar

Execute o arquivo principal:
```powershell
python main.py
```

1. Aguarde a calibração do ruído ambiente do microfone (cerca de 1 segundo).
2. Diga: *"Bruxo, listar comandos"* ou faça qualquer solicitação da tabela acima!
3. Para encerrar o programa, diga: *"Bruxo, tchau"* ou pressione `Ctrl + C` no terminal.
