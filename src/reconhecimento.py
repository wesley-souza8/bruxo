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
        """Garante que o arquivo haarcascade exista e retorne um caminho compatível com OpenCV no Windows."""
        import os
        import urllib.request
        import tempfile
        import shutil
        
        nome_arquivo = "haarcascade_frontalface_default.xml"
        caminho_local = os.path.join(self.diretorio, nome_arquivo)
        caminho_temp = os.path.join(tempfile.gettempdir(), nome_arquivo)
        
        # 1. Garante que o arquivo existe localmente (baixa do GitHub se necessário)
        if not os.path.exists(caminho_local) or os.path.getsize(caminho_local) == 0:
            print("[SISTEMA] Baixando classificador de rosto (haarcascade)...")
            url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
            try:
                urllib.request.urlretrieve(url, caminho_local)
            except Exception as e:
                print(f"[ERRO] Falha ao baixar classificador: {e}")
        
        # 2. Converte para caminho curto 8.3 do Windows se possível
        try:
            import ctypes
            buf = ctypes.create_unicode_buffer(500)
            ctypes.windll.kernel32.GetShortPathNameW(caminho_local, buf, 500)
            if buf.value and os.path.exists(buf.value):
                # Testa se o OpenCV consegue carregar
                teste = cv2.CascadeClassifier(buf.value)
                if not teste.empty():
                    return buf.value
        except Exception:
            pass

        # 3. Fallback seguro: copia para a pasta TEMP do Windows (caminho garantido em ANSI/ASCII)
        try:
            if os.path.exists(caminho_local):
                shutil.copy2(caminho_local, caminho_temp)
                teste = cv2.CascadeClassifier(caminho_temp)
                if not teste.empty():
                    return caminho_temp
        except Exception:
            pass
            
        return caminho_local

    def _detectar_faces(self, gray_equalized, face_cascade):
        """
        Executa a detecção facial de alta velocidade usando downscale 0.5x.
        Retorna a lista de retângulos (x, y, w, h) na escala original.
        """
        pequeno = cv2.resize(gray_equalized, (0, 0), fx=0.5, fy=0.5)
        faces_pequenas = face_cascade.detectMultiScale(
            pequeno,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(35, 35)
        )
        faces_originais = []
        for (x, y, w, h) in faces_pequenas:
            faces_originais.append((x * 2, y * 2, w * 2, h * 2))
        return faces_originais

    def capturar_rosto(self, nome: str) -> bool:
        """Abre a webcam, localiza o rosto e salva amostras padronizadas rapidamente."""
        pasta_usuario = os.path.join(self.diretorio, nome.lower().strip().replace(" ", "_"))
        if not os.path.exists(pasta_usuario):
            os.makedirs(pasta_usuario)

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("[ERRO CÂMERA] Não foi possível acessar a webcam.")
                return False

        # Configura resolução 640x480 para rodar com alta performance em qualquer notebook
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        cascade_path = self._obter_cascade()
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if face_cascade.empty():
            print("[ERRO] Arquivo de detecção de rosto ausente ou corrompido.")
            return False

        fotos_tiradas = 0
        max_fotos = 15
        tempo_ultima_foto = time.time()
        
        print(f"[CÂMERA] Capturando fotos para: {nome}. Olhe para a lente...")
        
        while fotos_tiradas < max_fotos:
            ret, frame = cap.read()
            if not ret:
                break

            tela = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Equalização de histograma para neutralizar sombras, luz forte e reflexos de óculos
            gray_eq = cv2.equalizeHist(gray)
            
            faces = self._detectar_faces(gray_eq, face_cascade)

            for (x, y, w, h) in faces:
                cv2.rectangle(tela, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(tela, f"Cadastrando {nome}: {fotos_tiradas}/{max_fotos}", (x, max(20, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                agora = time.time()
                # Tira foto a cada 0.25s para captura rápida e responsiva
                if agora - tempo_ultima_foto >= 0.25:
                    rosto_recortado = gray_eq[y:y+h, x:x+w]
                    if rosto_recortado.size > 0:
                        # Padroniza todas as fotos em 160x160 pixels
                        rosto_padrao = cv2.resize(rosto_recortado, (160, 160))
                        caminho_foto = os.path.join(pasta_usuario, f"foto_{fotos_tiradas}.jpg")
                        
                        sucesso_enc, buf_img = cv2.imencode('.jpg', rosto_padrao)
                        if sucesso_enc:
                            buf_img.tofile(caminho_foto)
                        
                        fotos_tiradas += 1
                        tempo_ultima_foto = agora
                    break

            # Barra de progresso no topo da tela
            progresso = int((fotos_tiradas / max_fotos) * 640)
            cv2.rectangle(tela, (0, 0), (progresso, 8), (0, 255, 0), -1)

            cv2.imshow("Cadastro Facial do Bruxo", tela)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        
        # Invalida modelo em cache para forçar retreinamento
        self.modelo = None
        return fotos_tiradas >= max_fotos

    def treinar_modelo(self) -> bool:
        """Lê as fotos da pasta rostos, treina o LBPH e cria o modelo em memória."""
        import numpy as np
        
        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
        except AttributeError:
            print("[ERRO] O módulo cv2.face falhou. Certifique-se de que opencv-contrib-python está instalado.")
            return False
            
        faces = []
        ids = []
        self.mapeamento_nomes = {}
        id_atual = 1
        
        if not os.path.exists(self.diretorio):
            return False
            
        for nome_pasta in os.listdir(self.diretorio):
            caminho_pasta = os.path.join(self.diretorio, nome_pasta)
            if not os.path.isdir(caminho_pasta): 
                continue
                
            self.mapeamento_nomes[id_atual] = nome_pasta.replace("_", " ").title()
            
            for arquivo in os.listdir(caminho_pasta):
                if arquivo.endswith('.jpg'):
                    img_path = os.path.join(caminho_pasta, arquivo)
                    try:
                        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    except Exception:
                        img = None
                    if img is not None:
                        if img.shape != (160, 160):
                            img = cv2.resize(img, (160, 160))
                        faces.append(img)
                        ids.append(id_atual)
            id_atual += 1
            
        if len(faces) == 0:
            return False
            
        recognizer.train(faces, np.array(ids))
        self.modelo = recognizer
        return True

    def reconhecer_rosto(self) -> str:
        """Abre a câmera, procura por um rosto e tenta adivinhar quem é de forma rápida."""
        if getattr(self, 'modelo', None) is None:
            sucesso = self.treinar_modelo()
            if not sucesso:
                return None
                
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
            if not cap.isOpened(): 
                return None
            
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        cascade_path = self._obter_cascade()
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if face_cascade.empty():
            print("[ERRO] Arquivo de detecção de rosto ausente ou corrompido.")
            return None
        
        start_time = time.time()
        nome_reconhecido = None
        consecutivas = 0
        ultimo_nome_visto = None
        
        print("[CÂMERA] Tentando reconhecer o rosto. Olhe para a lente...")
        
        while time.time() - start_time < 8:
            ret, frame = cap.read()
            if not ret: 
                break
                
            tela = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_eq = cv2.equalizeHist(gray)
            
            faces = self._detectar_faces(gray_eq, face_cascade)
            
            for (x, y, w, h) in faces:
                rosto_recortado = gray_eq[y:y+h, x:x+w]
                if rosto_recortado.size == 0:
                    continue
                    
                rosto_padrao = cv2.resize(rosto_recortado, (160, 160))
                
                id_previsto, confianca = self.modelo.predict(rosto_padrao)
                
                # Limiar calibrado para fotos normalizadas e equalizadas
                if confianca < 78:
                    nome = self.mapeamento_nomes.get(id_previsto, "Desconhecido")
                    cv2.rectangle(tela, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(tela, f"{nome} ({int(confianca)})", (x, max(20, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    
                    if nome == ultimo_nome_visto:
                        consecutivas += 1
                    else:
                        ultimo_nome_visto = nome
                        consecutivas = 1
                        
                    if consecutivas >= 3:
                        nome_reconhecido = nome
                else:
                    cv2.rectangle(tela, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    cv2.putText(tela, f"Desconhecido ({int(confianca)})", (x, max(20, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    consecutivas = 0

            cv2.imshow("Reconhecimento Facial do Bruxo", tela)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            if nome_reconhecido:
                cv2.waitKey(800)
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        return nome_reconhecido

    def apagar_cadastro(self, nome: str = None) -> tuple[bool, str]:
        """Apaga a pasta de um usuário específico ou todas as pastas de rostos."""
        import shutil
        import stat
        
        def _remover_forcar(caminho):
            def onerror(func, path, exc_info):
                try:
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                except Exception:
                    pass
            shutil.rmtree(caminho, onerror=onerror)

        if not os.path.exists(self.diretorio):
            return False, "O banco de dados de rostos já está vazio."
            
        # Invalida o modelo treinado na memória RAM
        self.modelo = None
        self.mapeamento_nomes = {}

        if nome:
            nome_normalizado = nome.lower().strip().replace(" ", "_")
            pasta_usuario = os.path.join(self.diretorio, nome_normalizado)
            
            # Se não encontrou caminho exato, procura por correspondência parcial
            if not os.path.exists(pasta_usuario):
                for p in os.listdir(self.diretorio):
                    caminho_p = os.path.join(self.diretorio, p)
                    if os.path.isdir(caminho_p) and (nome_normalizado in p or p in nome_normalizado):
                        pasta_usuario = caminho_p
                        nome = p.replace("_", " ").title()
                        break

            if os.path.exists(pasta_usuario) and os.path.isdir(pasta_usuario):
                try:
                    _remover_forcar(pasta_usuario)
                    return True, f"O cadastro facial de {nome} foi excluído com sucesso."
                except Exception as e:
                    return False, f"Houve um erro ao tentar excluir o cadastro de {nome}."
            else:
                return False, f"Não encontrei nenhum rosto cadastrado com o nome {nome}."
        else:
            apagados = 0
            for item in os.listdir(self.diretorio):
                caminho_item = os.path.join(self.diretorio, item)
                if os.path.isdir(caminho_item):
                    try:
                        _remover_forcar(caminho_item)
                        apagados += 1
                    except Exception:
                        pass

            if apagados > 0:
                return True, f"Foram excluídos todos os {apagados} cadastros faciais do sistema."
            else:
                return False, "O banco de dados já estava vazio. Ninguém foi apagado."
