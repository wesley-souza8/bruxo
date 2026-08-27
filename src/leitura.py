import cv2

class LeitorTexto:
    """
    Classe responsável por extrair texto e números da webcam utilizando EasyOCR.
    """
    def __init__(self):
        self.leitor = None

    def _iniciar_leitor(self):
        # Carregamento preguiçoso (lazy load) para não atrasar a inicialização inicial do assistente
        if self.leitor is None:
            import sys
            import easyocr
            
            # Força o terminal a aceitar caracteres Unicode da barra de progresso do easyocr
            if sys.stdout.encoding.lower() != 'utf-8':
                sys.stdout.reconfigure(encoding='utf-8')
                
            print("[SISTEMA] Carregando modelo de leitura de texto (EasyOCR)... Pode levar alguns segundos na primeira vez.")
            # gpu=False garante compatibilidade em qualquer máquina sem precisar configurar drivers NVIDIA
            self.leitor = easyocr.Reader(['pt', 'en'], gpu=False, verbose=False)

    def escanear_texto(self) -> str:
        self._iniciar_leitor()
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("[ERRO CÂMERA] Não foi possível acessar a webcam para leitura.")
                return ""
        
        texto_detectado = ""
        print("[CÂMERA] Modo Escaneamento de Texto ativado. Pressione 'S' para capturar.")
        
        while True:
            ret, frame = cap.read()
            if not ret: 
                break
            
            tela = frame.copy()
            # Instruções na tela
            cv2.putText(tela, "Posicione o texto e aperte 'S' para escanear", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(tela, "Aperte 'Q' para cancelar", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            cv2.imshow("Escaneamento de Texto - Bruxo", tela)
            
            key = cv2.waitKey(30) & 0xFF
            if key == ord('s'):
                # Dá um feedback visual rápido de processamento
                cv2.putText(tela, "Processando OCR, aguarde...", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.imshow("Escaneamento de Texto - Bruxo", tela)
                cv2.waitKey(1) # Força a atualização da tela
                
                # O parâmetro detail=0 retorna apenas uma lista de strings encontradas
                print("[INFO] Lendo texto da imagem...")
                resultados = self.leitor.readtext(frame, detail=0)
                texto_detectado = " ".join(resultados)
                break
                
            elif key == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        return texto_detectado
