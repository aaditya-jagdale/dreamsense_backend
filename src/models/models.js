import fetch from "node-fetch";

const API_URL = process.env.OLLAMA_API_URL || "http://localhost:11434/api/chat"; // Corrected endpoint
const LLAMA_MODEL = process.env.OLLAMA_MODEL || "llama3.2:3b"; // Ensure the model exists
const REQUEST_TIMEOUT = process.env.REQUEST_TIMEOUT || 10000;
const MAX_RETRIES = process.env.MAX_RETRIES || 3;

export async function askAI(messages, format) {
    if (!Array.isArray(messages) || messages.length === 0) {
        console.error("askAI: Invalid messages array provided.");
        return null;
    }

    const payload = {
        model: LLAMA_MODEL,
        messages: messages,
        stream: false,
        format: format,
    };

    let attempt = 0;
    while (attempt < MAX_RETRIES) {
        attempt++;
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

            const response = await fetch(API_URL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload),
                signal: controller.signal
            });

            clearTimeout(timeout);
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`askAI: HTTP Error ${response.status} - ${errorText}`);
                throw new Error(`API Error: ${response.status} - ${errorText}`);
            }
            //remove all the extra text from the response
            const response_json = await response.json();
            console.log("--------Response from the API", response_json);
            const response_text = response_json['message']['content'];
            const response_text_clean = response_text.replace(/```json\n|```/g, '');
            return JSON.parse(response_text_clean);
        } catch (error) {
            if (error.name === "AbortError") {
                console.error(`askAI: Request timed out (Attempt ${attempt}/${MAX_RETRIES})`);
            } else {
                console.error(`askAI: Error (Attempt ${attempt}/${MAX_RETRIES}):`, error.message);
            }

            if (attempt >= MAX_RETRIES) {
                console.error("askAI: Max retry attempts reached. Returning null.");
                return null;
            }
        }
    }
}