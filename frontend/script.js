const NGROK_BACKEND_URL = "https://934b-34-87-25-210.ngrok-free.app";

document.getElementById("image").addEventListener("change", function(e) {
    const file = e.target.files[0];
    const previewImage = document.getElementById("image-preview");
    const previewContainer = document.getElementById("image-preview-container");

    if (file) {
        const reader = new FileReader();


        reader.onload = function(event) {
            previewImage.src = event.target.result;
            previewContainer.style.display = "block";  
        };

        reader.readAsDataURL(file); 
    }
});

document.getElementById("image-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const imageInput = document.getElementById("image");
    const questionInput = document.getElementById("question");
    const responseDiv = document.getElementById("response");

    if (!imageInput.files[0]) {
        responseDiv.textContent = "Por favor, selecione uma imagem.";
        return;
    }

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);
    formData.append("text", questionInput.value);

    responseDiv.textContent = "Processando...";

    try {
        const response = await fetch(`https://7dfd-34-87-106-188.ngrok-free.app/process-image`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Erro ao processar a imagem.");
        }

        const data = await response.json();


        responseDiv.innerHTML = `
            <p><strong>Resposta:</strong> ${data.response || "Resposta não disponível."}</p>
        `;
    } catch (error) {
        responseDiv.textContent = "Erro: " + error.message;
    }
});
