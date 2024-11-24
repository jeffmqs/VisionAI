from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from PIL import Image
from transformers import MllamaForConditionalGeneration, AutoProcessor

# Configuração do aplicativo Flask
app = Flask(__name__)
CORS(app)

# Mensagem de status para indicar o carregamento do modelo
print("Carregando o modelo...")

# Definir o ID do modelo e o token Hugging Face
model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"
token = "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"  # Substitua pelo token correto

# Configurar o diretório de offloading
offload_folder = "./offload"

try:
    # Carregar o modelo com configuração de dispositivo e offloading
    if torch.cuda.is_available():
        print("CUDA disponível. Carregando o modelo na GPU...")
        model = MllamaForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            token=token
        )
    else:
        print("CUDA não disponível. Carregando o modelo usando CPU...")
        model = MllamaForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            offload_folder=offload_folder,  # Diretório para offloading
            offload_state_dict=True,
            token=token
        )

    # Carregar o processador
    processor = AutoProcessor.from_pretrained(
        model_id,
        token=token
    )

    print("Modelo e processador carregados com sucesso!")

except Exception as e:
    print("Erro ao carregar o modelo ou o processador:", str(e))
    exit(1)

# Rota para processar imagem e texto
@app.route("/process-image", methods=["POST"])
def process_image():
    try:
        print("Requisição recebida no backend!")

        # Validar se os dados estão presentes
        if "image" not in request.files or "text" not in request.form:
            return jsonify({"error": "Faltam dados na requisição (image ou text)."}), 400

        # Receber a imagem e o texto do frontend
        image_file = request.files["image"]
        user_text = request.form["text"]

        # Abrir a imagem
        print("Abrindo imagem recebida...")
        image = Image.open(image_file)

        # Preparar entrada para o modelo
        print("Preparando entrada para o modelo...")
        messages = [
            {"role": "user", "content": [
                {"type": "image"},
                {"type": "text", "text": user_text}
            ]}
        ]
        input_text = processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = processor(
            image,
            input_text,
            add_special_tokens=False,
            return_tensors="pt"
        ).to(model.device)

        # Gerar resposta
        print("Gerando resposta do modelo...")
        output = model.generate(**inputs, max_new_tokens=30)
        response_text = processor.decode(output[0])

        print("Resposta gerada com sucesso!")
        return jsonify({"response": response_text})

    except Exception as e:
        print("Erro ao processar a imagem:", str(e))
        return jsonify({"error": str(e)}), 500

# Rota inicial para verificar se o backend está rodando
@app.route("/")
def index():
    return jsonify({"message": "VisionAI Assist Backend is running."})

# Executar o aplicativo Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
