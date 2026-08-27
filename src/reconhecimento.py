import cv2
import os
import time

class GerenciadorFacial:
    """
    Classe responsável por lidar com o reconhecimento e cadastro facial usando OpenCV.
    Por enquanto, realiza o cadastro de novas faces salvando imagens em uma pasta.
    """
    def __init__(self, diretorio="rostos"):
        # Garante que salva na pasta raiz do projeto "bruxo"
        raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.diretorio = os.path.join(raiz_projeto, diretorio)
        if not os.path.exists(self.diretorio):
            os.makedirs(self.diretorio)

    def _obter_cascade(self) -> str:
        """Garante que o arquivo haarcascade exista, baixando-o se necessário."""
        import os
        import urllib.request
        
        nome_arquivo = "haarcascade_frontalface_default.xml"
        caminho_local = os.path.join(self.diretorio, nome_arquivo)
        
        # 1. Tenta o arquivo local (baixado previamente)
        if os.path.exists(caminho_local):
            return caminho_local
            
        # 2. Tenta o caminho padrão do pacote cv2 (que deu erro na sua máquina)
        try:
            caminho_cv2 = os.path.join(cv2.data.haarcascades, nome_arquivo)
            if os.path.exists(caminho_cv2):
                return caminho_cv2
        except Exception:
            pass
            
        # 3. Baixa do GitHub oficial do OpenCV e salva na pasta rostos
        print("[SISTEMA] Baixando classificador de rosto (haarcascade)...")
        url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
        try:
            urllib.request.urlretrieve(url, caminho_local)
            return caminho_local
        except Exception as e:
            print(f"[ERRO] Falha ao baixar classificador: {e}")
            return caminho_cv2

    def capturar_rosto(self, nome: str) -> bool:
        """Abre a webcam, localiza o rosto e salva algumas amostras."""
        pasta_usuario = os.path.join(self.diretorio, nome.lower().strip().replace(" ", "_"))
        if not os.path.exists(pasta_usuario):
            os.makedirs(pasta_usuario)

        # Usando CAP_DSHOW no Windows para a câmera abrir instantaneamente
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            # Fallback caso DSHOW falhe
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("[ERRO CÂMERA] Não foi possível acessar a webcam.")
                return False

        # Carrega o classificador padrão do OpenCV
        cascade_path = self._obter_cascade()
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if face_cascade.empty():
            print("[ERRO] Arquivo de detecção de rosto ausente ou corrompido.")
            return False

        fotos_tiradas = 0
        max_fotos = 10
        tempo_ultima_foto = time.time()
        
        print(f"[CÂMERA] Capturando fotos para: {nome}. Olhe para a lente...")
        
        while fotos_tiradas < max_fotos:
            ret, frame = cap.read()
            if not ret:
                break

            # Criar uma cópia do frame para desenhar por cima sem alterar a foto que será salva
            tela = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100))

            for (x, y, w, h) in faces:
                # Desenha o retângulo na tela de preview
                cv2.rectangle(tela, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(tela, f"Cadastrando: {fotos_tiradas}/{max_fotos}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                agora = time.time()
                # Salva uma foto a cada 0.5 segundos para dar tempo da pessoa se mexer
                if agora - tempo_ultima_foto > 0.5:
                    rosto_recortado = gray[y:y+h, x:x+w]
                    caminho_foto = os.path.join(pasta_usuario, f"foto_{fotos_tiradas}.jpg")
                    cv2.imwrite(caminho_foto, rosto_recortado)
                    
                    fotos_tiradas += 1
                    tempo_ultima_foto = agora
                    break # Salva apenas 1 rosto por frame para não bugar o contador

            # Exibir a câmera em tempo real para o usuário se ver
            cv2.imshow("Cadastro Facial do Bruxo", tela)
            
            # O waitKey(30) atualiza a janela (rodando a ~30 fps) e checa o botão 'q'
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        
        return fotos_tiradas >= max_fotos

    def treinar_modelo(self) -> bool:
        """Lê as fotos da pasta rostos, treina o LBPH e cria o modelo em memória."""
        import numpy as np
        
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
        except AttributeError:
            print("[ERRO] O módulo cv2.face falhou. Tente rodar: pip uninstall opencv-python opencv-contrib-python -y e depois pip install opencv-contrib-python")
            return False
            
        faces = []
        ids = []
        self.mapeamento_nomes = {}
        id_atual = 1
        
        # Lê cada pasta de pessoa
        if not os.path.exists(self.diretorio):
            return False
            
        for nome_pasta in os.listdir(self.diretorio):
            caminho_pasta = os.path.join(self.diretorio, nome_pasta)
            if not os.path.isdir(caminho_pasta): 
                continue
                
            self.mapeamento_nomes[id_atual] = nome_pasta.replace("_", " ").title()
            
            # Lê as fotos
            for arquivo in os.listdir(caminho_pasta):
                if arquivo.endswith('.jpg'):
                    img_path = os.path.join(caminho_pasta, arquivo)
                    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        faces.append(img)
                        ids.append(id_atual)
            id_atual += 1
            
        if len(faces) == 0:
            return False
            
        # Treina o reconhecedor
        recognizer.train(faces, np.array(ids))
        self.modelo = recognizer
        return True

    def reconhecer_rosto(self) -> str:
        """Abre a câmera, procura por um rosto e tenta adivinhar quem é."""
        if getattr(self, 'modelo', None) is None:
            sucesso = self.treinar_modelo()
            if not sucesso:
                return None
                
        # Usando CAP_DSHOW no Windows para a câmera abrir instantaneamente
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened(): 
                return None
            
        cascade_path = self._obter_cascade()
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if face_cascade.empty():
            print("[ERRO] Arquivo de detecção de rosto ausente ou corrompido.")
            return None
        
        start_time = time.time()
        nome_reconhecido = None
        
        print("[CÂMERA] Tentando reconhecer o rosto. Olhe para a lente...")
        
        # Tenta reconhecer por no máximo 8 segundos
        while time.time() - start_time < 8:
            ret, frame = cap.read()
            if not ret: 
                break
                
            tela = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(100, 100))
            
            for (x, y, w, h) in faces:
                rosto_recortado = gray[y:y+h, x:x+w]
                
                # O LBPH retorna a distância (confiança). Quanto menor, mais parecido.
                id_previsto, confianca = self.modelo.predict(rosto_recortado)
                
                # Se a distância for menor que ~65, consideramos que é a pessoa
                if confianca < 65:
                    nome = self.mapeamento_nomes.get(id_previsto, "Desconhecido")
                    cv2.rectangle(tela, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(tela, f"{nome} ({int(confianca)})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    nome_reconhecido = nome
                else:
                    cv2.rectangle(tela, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(tela, f"Desconhecido ({int(confianca)})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            cv2.imshow("Reconhecimento Facial do Bruxo", tela)
            
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
                
            # Se já achou com confiança, pausa um segundinho para o usuário ver a tela verde e finaliza
            if nome_reconhecido:
                cv2.waitKey(1000)
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        return nome_reconhecido

    def apagar_cadastro(self, nome: str = None) -> tuple[bool, str]:
        """Apaga a pasta de um usuário específico ou todas as pastas de rostos."""
        import shutil
        if not os.path.exists(self.diretorio):
            return False, "O banco de rostos está vazio."
            
        if nome:
            pasta_usuario = os.path.join(self.diretorio, nome.lower().strip().replace(" ", "_"))
            if os.path.exists(pasta_usuario):
                try:
                    shutil.rmtree(pasta_usuario)
                    return True, f"O cadastro facial de {nome} foi excluído com sucesso."
                except Exception as e:
                    return False, "Houve um erro ao tentar excluir a pasta do sistema."
            else:
                return False, f"Não encontrei nenhum rosto cadastrado para {nome}."
        else:
            apagados = 0
            for item in os.listdir(self.diretorio):
                caminho_item = os.path.join(self.diretorio, item)
                if os.path.isdir(caminho_item):
                    try:
                        shutil.rmtree(caminho_item)
                        apagados += 1
                    except Exception:
                        pass
            
            # Removemos também o arquivo do haarcascade se ele foi baixado, ou ignoramos
            # Mas vamos focar em remover apenas as pastas (que representam usuários)
            
            if apagados > 0:
                return True, "Todos os rostos cadastrados foram apagados do banco de dados."
            else:
                return False, "O banco de dados já estava vazio. Ninguém foi apagado."
