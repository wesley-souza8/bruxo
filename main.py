"""
Projeto F.R.I.D.A.Y. - Assistente Virtual Bruxo
Checkpoint 4 - Engenharia de Software (2º Semestre)

Ponto de entrada da aplicação.
"""

from src.assistente import AssistenteBruxo

def main():
    assistente = AssistenteBruxo()
    assistente.iniciar()

if __name__ == "__main__":
    main()
