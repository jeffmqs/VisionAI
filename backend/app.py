# aqui está instalando dependências necessárias
#!pip install flask flask-cors transformers torch pillow pyngrok --quiet (para usar no collab. no vs code da erro por isso está comentado)
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from PIL import Image
from transformers import MllamaForConditionalGeneration, AutoProcessor
from pyngrok import ngrok
import re  

#configurando o flask
app = Flask(__name__)
CORS(app)  #e aqui to permitindoo o cors para todas as origens

print("Carregando o modelo...")

# aqui o modelo e o token pra liberar o modelo da ia
model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"
hf_token = "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" 

offload_folder = "./offload"

try:
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
            offload_folder=offload_folder, 
            offload_state_dict=True,
            use_auth_token=hf_token
        )

    processor = AutoProcessor.from_pretrained(
        model_id,
        use_auth_token=hf_token
    )
    print("Modelo e processador carregados com sucesso.")

except Exception as e:
    print(f"Erro ao carregar o modelo ou o processador: {e}")
    exit(1)

#rota inicial pra verificar se o back roda
@app.route("/")
def index():
    return jsonify({"message": "VisionAI Assist Backend is running."})

#processamento da imagem
@app.route("/process-image", methods=["POST"])
def process_image():
    try:
        #recebimento da imagem pelo front end e da pergunta tambem
        image_file = request.files["image"]
        user_text = request.form["text"]

        print("Abrindo a imagem recebida...")
        image = Image.open(image_file)

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

        #gerar respostta modelo (se você perceber, durante o processamento da imagem no frontend o backend entrega essa saída aqui no colab)
        print("Gerando resposta do modelo...")
        output = model.generate(**inputs, max_new_tokens=100)
        response_text = processor.decode(output[0])

        cleaned_response = re.sub(r"<\|.*?\|>", "", response_text).strip()
        cleaned_response = cleaned_response.replace("user ", "").replace("assistant ", "")

        return jsonify({
            "question": user_text.strip(),
            "response": cleaned_response
        })

    except Exception as e:
        print(f"Erro ao processar a imagem: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":

    ngrok.set_auth_token("2pH1NtNqwrZnC0BgUo8ZEDELD9q_7FCxVEjEPuRzeHJZyyyi6")


    public_url = ngrok.connect(5000, bind_tls=True)
    print(f"Servidor backend exposto em: {public_url}")


    app.run(host="0.0.0.0", port=5000)
