document.getElementById("feedbackButton").addEventListener("click", async function () {
    try {
        let iframe = document.getElementById("drawioFrame").contentWindow;
        let diagramData = await getDiagramXML(iframe);

        if (!diagramData) {
            alert("Failed to retrieve UML diagram data.");
            return;
        }

        const response = await fetch("http://127.0.0.1:8000/get_ai_feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ diagramData: diagramData }),
        });

        const result = await response.json();
        document.getElementById("feedbackResult").innerText = result.feedback || result.error;
    } catch (error) {
        console.error("Error fetching AI feedback:", error);
        document.getElementById("feedbackResult").innerText = "An error occurred. Check the console for details.";
    }
});

// Function to extract UML diagram data from Draw.io
function getDiagramXML(iframe) {
    return new Promise((resolve) => {
        const messageListener = (event) => {
            try {
                let data = JSON.parse(event.data);
                if (data.event === "export") {
                    window.removeEventListener("message", messageListener);
                    resolve(data.data);
                }
            } catch (err) {
                console.error("Error parsing message from Draw.io:", err);
            }
        };

        window.addEventListener("message", messageListener, { once: true });
        iframe.postMessage(JSON.stringify({ action: "export", format: "xml" }), "*");
    });
}
