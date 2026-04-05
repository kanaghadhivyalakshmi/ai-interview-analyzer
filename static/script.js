async function analyzeCandidate() {
    const jd = document.getElementById("jd").value.trim();
    const transcript = document.getElementById("transcript").value.trim();
    const resultDiv = document.getElementById("result");

    const response = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ jd, transcript })
    });

    const data = await response.json();

    console.log("Backend response:", data);

    resultDiv.innerText = data.result || "❌ No result returned";
}