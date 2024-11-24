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
        const response = await fetch("https://fbe4-34-83-105-117.ngrok-free.app/process-image", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Erro ao processar a imagem.");
        }

        const data = await response.json();
        responseDiv.textContent = data.response || "Resposta não disponível.";
    } catch (error) {
        responseDiv.textContent = "Erro: " + error.message;
    }
});
