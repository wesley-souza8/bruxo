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
> Aplicação orientada a objetos para reconhecimento de comandos de voz, síntese neural, gerenciamento de agenda, captura de tela, controle de sistema, inteligência artificial generativa e visão computacional (biometria facial e OCR).

---

## 📌 Sobre o Projeto

Inspirado na assistente **F.R.I.D.A.Y. (Sexta-Feira)** do Homem de Ferro, o **Bruxo** é um assistente virtual inteligente capaz de escutar o usuário continuamente em segundo plano, filtrando comandos através de uma **palavra de ativação (*Wake Word*)** e respondendo por voz masculina grave neural de forma assíncrona. O projeto combina inteligência artificial generativa, automação de sistema operacional, serviços web e visão computacional em tempo real.

---

## 🏗️ Arquitetura Orientada a Objetos (POO)

O projeto foi estruturado seguindo os princípios de modularidade, separação de responsabilidades (SOLID) e o padrão de projeto **Dispatcher Pattern**:

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
    ├── config.py              # Constantes globais, caminhos, timeouts e configurações
    ├── voz.py                 # SintetizadorVoz (Edge-TTS Neural + Velocidade Dinâmica + Pygame em RAM)
    ├── microfone.py           # OuvinteMicrofone (SpeechRecognition + Calibração + Wake Word)
    ├── agenda.py              # GerenciadorAgenda (CRUD resiliente e autônomo de compromissos)
    ├── captura.py             # GerenciadorCaptura (Screenshots com timestamp e Limpeza)
    ├── ia_groq.py             # ClienteIA (Groq Cloud LPU API / LLaMA 3 com fallback)
    ├── servicos.py            # ServicosWeb e ControleSistema (Spotify, Navegador, APIs, Volume)
    ├── reconhecimento.py      # GerenciadorFacial (OpenCV, Equalização, Downscale 0.5x, LBPH)
    ├── leitura.py             # LeitorTexto (Escaneamento OCR de texto com EasyOCR)
    ├── easter_eggs.py         # GerenciadorEasterEggs (Piadas, memes e diálogos clássicos)
    └── assistente.py          # AssistenteBruxo (Classe Orquestradora e Dispatcher Central)
```

---

## 🚀 Funcionalidades e Tabela de Comandos

O assistente só responde quando acionado pela palavra de ativação: **"Bruxo"** (ou variações como *"O Bruxo"* / *"Bruxão"*). Frases ditas sem a palavra de ativação são ignoradas e exibidas no terminal apenas para monitoramento.

| # | Comando Falado | Ação Executada |
|---|---|---|
| 1 | **"Bruxo, que horas são?"** | Informa as horas e minutos atuais por voz. |
| 2 | **"Bruxo, que dia é hoje?"** | Informa o dia, mês e ano atuais por voz. |
| 3 | **"Bruxo, quem é você?"** / **"se apresente"** | Apresenta detalhadamente a identidade e todas as funcionalidades do assistente. |
| 4 | **"Bruxo, cadastrar na agenda"** | Pergunta o evento, transcreve e salva em `agenda.txt`. Diferencia inteligentemente da biometria facial. |
| 5 | **"Bruxo, ler agenda"** | Lê todos os compromissos salvos em `agenda.txt`. |
| 6 | **"Bruxo, limpar agenda"** | Esvazia o conteúdo do arquivo `agenda.txt` com prioridade máxima. |
| 7 | **"Bruxo, tirar um print da tela"** | Captura a tela inteira e salva com carimbo de data/hora na pasta `img/`. |
| 8 | **"Bruxo, limpar fotos"** | Apaga todas as imagens e prints salvos na pasta `img/`. |
| 9 | **"Bruxo, previsão do tempo"** | Pergunta a cidade desejada e consulta a temperatura e condições na OpenWeather API. |
| 10 | **"Bruxo, cotação do dólar"** | Consulta a AwesomeAPI e informa o valor atual da moeda em reais. |
| 11 | **"Bruxo, aumentar/diminuir volume"** | Ajusta o volume do Windows em passos graduais. |
| 12 | **"Bruxo, mutar / desmutar"** | Alterna entre silenciar o áudio e restaurar o som com fala correspondente. |
| 13 | **"Bruxo, pausar / despausar"** | Controla o play/pause de reprodutores de mídia e vídeos do sistema operacional. |
| 14 | **"Bruxo, pesquisar no Google"** | Realiza buscas no navegador **após** a IA Groq validar a segurança/SFW do termo. |
| 15 | **"Bruxo, pesquisar vídeo"** | Pergunta o nome e pesquisa vídeos diretamente no YouTube. |
| 16 | **"Bruxo, tocar no Spotify"** | Abre o Spotify Desktop via URI, pesquisa a música/artista e dá o play automático. |
| 17 | **"Bruxo, abrir portal da faculdade"** | Abre diretamente a plataforma de estudos da FIAP no navegador. |
| 18 | **"Bruxo, cadastrar rosto"** | Abre a webcam, coleta 15 amostras normalizadas com barra de progresso em tempo real e treina o LBPH. |
| 19 | **"Bruxo, quem sou eu?"** | Analisa a câmera com equalização de iluminação e identifica o usuário cadastrado pelo nome. |
| 20 | **"Bruxo, apagar rosto"** / **"apagar rosto do [Nome]"** | Exclui cadastros faciais específicos pelo nome falado ou esvazia todo o banco de biometria. |
| 21 | **"Bruxo, escanear texto"** | Liga a câmera, capta texto ou números de papéis/documentos físicos e lê com OCR (EasyOCR). |
| 22 | **"Bruxo, Alanzoka"** | *Easter Egg:* Responde com o clássico *"Nextage, bebê!"*. |
| 23 | **"Bruxo, pega no breu"** | *Easter Egg:* Abre instantaneamente o vídeo clássico no YouTube em silêncio. |
| 24 | **"Bruxo, Skipinho"** / **"Axt"** / **"Yetz"** | *Easter Egg:* Narra a famosa discussão gamer dos anos de ouro em velocidade acelerada (+25%). |
| 25 | **"Bruxo, [qualquer pergunta]"** | Envia a dúvida para a IA Generativa (Llama 3 via Groq) e responde em voz alta em menos de 1 segundo. |
| 26 | **"Bruxo, tchau"** (ou *"desligar"*) | Responde *"Bruxo saindo... KABUUUM!"* e encerra a aplicação com segurança. |

---

## 💡 Destaques de Engenharia e Robustez

* **Despachante Modular (*Dispatcher Pattern*):** Separação de fluxos de execução em métodos especializados, isolando a regra de negócio da manipulação direta de hardware.
* **Escuta Persistente e Sem Interferência de Alto-Falante:** O assistente conclui sua fala antes de abrir uma janela de escuta limpa de 10 segundos, eliminando cancelamentos falsos em notebooks.
* **Visão Computacional Otimizada (70% menos CPU):** A detecção facial opera em escala reduzida (*0.5x*), permitindo taxa de quadros fluida (~30 FPS) mesmo em notebooks com processadores modestos.
* **Equalização de Histograma (`equalizeHist`):** Neutraliza sombras laterais, luz forte de janelas e reflexos de óculos tanto no cadastro quanto no reconhecimento biométrico.
* **Compatibilidade Completa com Windows (Caminhos UTF-8):** Gravação e leitura de imagens e classificadores XML imunes a erros de caminhos com caracteres acentuados (como *"Área de Trabalho"*).
* **Velocidade de Voz Dinâmica:** Síntese Microsoft Neural com suporte a taxas de aceleração pontuais para respostas expressivas e Easter Eggs.

---

## 🛠️ Tecnologias e Bibliotecas

* **Linguagem:** Python 3.10+
* **Visão Computacional e OCR:** `opencv-contrib-python`, `numpy`, `easyocr`
* **Reconhecimento de Fala (STT):** `SpeechRecognition` + `PyAudio`
* **Síntese de Voz (TTS):** `edge-tts` (Microsoft Neural Voice `pt-BR-AntonioNeural` customizado) + `gTTS` (fallback)
* **Inteligência Artificial Generativa:** `groq` (Groq Cloud LPU API - Llama 3)
* **Reprodução de Áudio:** `pygame` (execução 100% em memória RAM via `io.BytesIO` sem travas de disco)
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

### 2. Criar e ativar o ambiente virtual (Recomendado)
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
Crie um arquivo `.env` na raiz do projeto e adicione suas credenciais:
```env
GROQ_API_KEY=sua_chave_groq_aqui
OPENWEATHER_API_KEY=sua_chave_openweathermap_aqui
AWESOME_API_KEY=sua_chave_awesomeapi_aqui
```

---

## ▶️ Como Executar

Execute o arquivo principal:
```powershell
python main.py
```

1. Aguarde a calibração do ruído ambiente do microfone (cerca de 1 segundo).
2. Diga: *"Bruxo, se apresente"* ou faça qualquer solicitação listada na tabela de comandos!
3. Para encerrar o programa, diga: *"Bruxo, tchau"* ou pressione `Ctrl + C` no terminal.
