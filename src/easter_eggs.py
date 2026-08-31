import webbrowser


class GerenciadorEasterEggs:
    """
    Classe responsável por gerenciar e responder aos Easter Eggs e piadas do Bruxo.
    Isola conteúdos de humor da lógica de negócio e orquestração do assistente.
    """

    def processar(self, comando: str, voz) -> bool:
        """
        Verifica se o comando corresponde a um Easter Egg registrado.
        Retorna True se processou um Easter Egg, ou False caso contrário.
        """
        comando_limpo = comando.strip().lower()

        # 1. EASTER EGG: ALANZOKA
        if any(t in comando_limpo for t in ["alanzoka", "alan zoka", "alanzo", "alan", "allan"]):
            voz.falar("Nextage, bebê!")
            return True

        # 2. EASTER EGG: PEGA NO BREU
        elif any(t in comando_limpo for t in [
            "pega no breu", "gaitaço", "gaitaco", "ronaldo",
            "agro pesca jacaré", "agro pesca jacare", "pega no bre"
        ]):
            webbrowser.open("https://www.youtube.com/watch?v=TFdO7oqkMzI")
            return True

        # 3. EASTER EGG: AXT VS SKIPINHO (DISCUSSÃO DOS GAMES)
        elif any(t in comando_limpo for t in [
            "skipinho", "skpinho", "axt", "yetz", "crucificaram o yetz",
            "e aí não", "e ai nao", "eae não", "eae nao", "e aí o que", "e ai o que",
            "e aí mano", "e ai mano", "e aí ué", "e ai ue", "e aí skipinho", "e ai skipinho"
        ]) or comando_limpo in ["iai", "e aí", "e ai", "eae", "e aí?", "e ai?"]:
            dialogo = (
                "E aí Skipinho? E aí o que mano? E aí ué! "
                "Não, e aí não! Como e aí não? Ué e aí o que? "
                "E aí mano, e aí ué! Não tem e aí, e aí o que? "
                "Ué eu tô falando e aí mano! Mas e aí o que cara? "
                "Não, e aí não! A gente sempre jogou junto quando crucificaram o Yetz. "
                "Você não é criança e nem eu sou. Xiu é o caralho! "
                "Uma vez você me desrespeitou e falou da minha família e agora eu tô falando contigo igual homem! "
                "É? Então beleza. Então foda-se seu merda, seu babaca, seu criança, seu merda!"
            )
            print("\n[CLÁSSICO]: Axt vs Skipinho\n" + dialogo + "\n")
            voz.falar(dialogo, velocidade="+25%")
            return True

        return False
