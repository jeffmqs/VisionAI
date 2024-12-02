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
        /*no fetch está o link que usamos quando demos o run no back do collab. toda vez que for dado um run novo no collab, deve-se colar novamente no campo fetch LINK/process-image */
        const response = await fetch(`https://7b7c-35-230-88-174.ngrok-free.app/process-image`, {
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
