# Importar módulos necessários
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from PIL import Image
from transformers import MllamaForConditionalGeneration, AutoProcessor
from pyngrok import ngrok
import re  # Biblioteca para limpar a resposta do modelo

# Configuração do aplicativo Flask
app = Flask(__name__)
CORS(app)  # Permitir CORS para todas as origens

print("Carregando o modelo...")

# Definir detalhes do modelo e token
model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"
hf_token = "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"  # Seu token Hugging Face

# Configurar diretório de offload (para uso de CPU)
offload_folder = "./offload"

try:
    # Carregar o modelo com suporte a GPU ou CPU
    if torch.cuda.is_available():
        print("GPU disponível. Carregando o modelo na GPU...")
        model = MllamaForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.float16,  # Reduzir consumo de memória
            device_map="auto",
            use_auth_token=hf_token
        )
    else:
        print("CUDA indisponível. Carregando no CPU...")
        model = MllamaForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            offload_folder=offload_folder,  # Configuração para offload na CPU
            offload_state_dict=True,
            use_auth_token=hf_token
        )

    # Carregar o processador
    processor = AutoProcessor.from_pretrained(
        model_id,
        use_auth_token=hf_token
    )
    print("Modelo e processador carregados com sucesso.")

except Exception as e:
    print(f"Erro ao carregar o modelo ou o processador: {e}")
    exit(1)

# Rota inicial para verificar se o backend está rodando


@app.route("/")
def index():
    return jsonify({"message": "VisionAI Assist Backend is running."})

# Rota para processar imagem e texto


@app.route("/process-image", methods=["POST"])
def process_image():
    try:
        # Receber a imagem e o texto do frontend
        image_file = request.files["image"]
        user_text = request.form["text"]

        # Abrir a imagem
        print("Abrindo a imagem recebida...")
        image = Image.open(image_file)

        # Preparar entrada para o modelo
        messages = [
            {"role": "user", "content": [
                {"type": "image"},
                {"type": "text", "text": user_text}
            ]}
        ]
        input_text = processor.apply_chat_template(
            messages, add_generation_prompt=True)
        inputs = processor(
            image,
            input_text,
            add_special_tokens=False,
            return_tensors="pt"
        ).to(model.device)

        # Gerar resposta do modelo
        print("Gerando resposta do modelo...")
        # Aumentado para evitar corte
        output = model.generate(**inputs, max_new_tokens=100)
        response_text = processor.decode(output[0])

        # Limpar a resposta para remover metadados e palavras específicas
        cleaned_response = re.sub(r"<\|.*?\|>", "", response_text).strip()
        cleaned_response = cleaned_response.replace(
            "user ", "").replace("assistant ", "")

        # Retornar pergunta e resposta separadamente
        return jsonify({
            "question": user_text.strip(),
            "response": cleaned_response
        })

    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
        return jsonify({"error": str(e)}), 500


# Configuração do ngrok para expor o backend
if __name__ == "__main__":
    # Configurar o token do ngrok
    ngrok.set_auth_token("2pH1NtNqwrZnC0BgUo8ZEDELD9q_7FCxVEjEPuRzeHJZyyyi6")

    # Criar um túnel público
    public_url = ngrok.connect(5000, bind_tls=True)
    print(f"Servidor backend exposto em: {public_url}")

    # Iniciar o servidor Flask
    app.run(host="0.0.0.0", port=5000)
