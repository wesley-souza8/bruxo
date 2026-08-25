# 🧙‍♂️ Assistente Virtual Bruxo (Projeto F.R.I.D.A.Y.)

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Groq AI](https://img.shields.io/badge/AI-Groq%20Cloud%20LPU-orange.svg)](https://groq.com/)
[![Edge-TTS](https://img.shields.io/badge/TTS-Microsoft%20Neural-purple.svg)](https://github.com/rany2/edge-tts)

## 👥 Integrantes do Grupo (CP4 - 4ESR)

* Deivison Pertel – RM 550803
* Eduardo Akira Murata – RM 98713
* Wesley Souza de Oliveira – RM 97874

---

> **Checkpoint 4 — Engenharia de Software (2º Semestre)**  
> Aplicação orientada a objetos para reconhecimento de comandos de voz, síntese neural, gerenciamento de agenda, captura de tela e inteligência artificial generativa.

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

| # | Comando Falado | Ação Executada | Critério de Avaliação |
|---|---|---|---|
| 1 | **"Bruxo, que horas são?"** | Informa as horas e minutos atuais por voz. | Item 4 |
| 2 | **"Bruxo, que dia é hoje?"** | Informa o dia, mês e ano atuais por voz. | Item 5 |
| 3 | **"Bruxo, cadastrar evento na agenda"** | Pergunta o evento, transcreve a resposta e salva em `agenda.txt`. | Item 2 |
| 4 | **"Bruxo, ler agenda"** | Lê todos os eventos salvos no arquivo `agenda.txt`. | Item 3 |
| 5 | **"Bruxo, limpar agenda"** | Esvazia o conteúdo do arquivo `agenda.txt` sem deletá-lo. | Item 8 |
| 6 | **"Bruxo, tirar um print da tela"** | Captura a tela e salva automaticamente com timestamp na pasta `img/`. | Item 10 (Extra) |
| 7 | **"Bruxo, limpar fotos"** | Apaga todas as imagens salvas na pasta `img/`. | Item 10 (Extra) |
| 8 | **"Bruxo, Alanzoka"** | Responde *"Nextage, bebê!"* (Easter Egg). | Item 10 (Extra) |
| 9 | **"Bruxo, [qualquer dúvida/pergunta]"** | Consulta a IA Generativa (Groq Cloud) e responde por voz em < 1s. | Item 9 |
| 10 | **"Bruxo, listar comandos"** | Exibe a lista formatada no terminal e resume as opções por voz. | Usabilidade |
| 11 | **"Bruxo, tchau"** (ou *"desligar"*) | Responde *"Bruxo saindo... KABUUUM!"* e encerra a aplicação. | Usabilidade |

---

## 🛠️ Tecnologias e Bibliotecas

* **Linguagem:** Python 3.10+
* **Reconhecimento de Fala (STT):** `SpeechRecognition` + `PyAudio`
* **Síntese de Voz (TTS):** `edge-tts` (Microsoft Neural Voice `pt-BR-AntonioNeural` com tom grave ajustado) + `gTTS` (fallback)
* **Reprodução de Áudio:** `pygame` (execução 100% em memória RAM via `io.BytesIO` sem bloqueio de arquivos)
* **Inteligência Artificial Generativa:** `groq` (Groq Cloud LPU API)
* **Captura de Tela:** `pyautogui` + `Pillow`
* **Gerenciamento de Ambiente:** `python-dotenv`

---

## ⚙️ Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd assistente
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

### 4. Configurar a Chave da API (Groq Cloud)
Crie um arquivo `.env` na raiz do projeto e adicione sua chave da Groq:
```env
GROQ_API_KEY=gsk_sua_chave_aqui
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
