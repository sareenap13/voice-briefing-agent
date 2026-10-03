const button = document.getElementById("generate");
const articleInput = document.getElementById("article");
const summary = document.getElementById("summary");
const audio = document.getElementById("audio");
const status = document.getElementById("status");

button.addEventListener("click", async () => {
    const article = articleInput.value;
    if (article.trim() === "") {
        summary.textContent = "Please enter an article first.";
        return;
    }

    button.textContent = "Generating...";
    button.disabled = true;
    audio.removeAttribute("src");
    audio.load();
    status.textContent = "Generating briefing...";
    summary.textContent = "";

    try {
        const response = await fetch("/brief", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                article: article
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail?.[0]?.msg || "Request failed");
        }

        const data = await response.json();
        summary.textContent = data.summary;
        status.textContent = "Briefing ready.";

        if (data.audio_file) {
            audio.src = "/static/briefing.mp3?t=" + Date.now();
            audio.load();
        }

        if (data.error) {
            status.textContent = "Audio unavailable.";
            summary.textContent += "\n\n" + data.error;
        }
    }

    catch (error) {
        summary.textContent = error.message;
        console.error(error);
    }
    button.textContent = "Generate Briefing";
    button.disabled = false;
});

articleInput.addEventListener("input", () => {
    audio.removeAttribute("src");
    audio.load();
    summary.textContent = "";
    status.textContent = "";
});