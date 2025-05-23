import dotenv from "dotenv";
import fetch from "node-fetch";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

// Configuration constants
const CONFIG = {
  ollama: {
    apiUrl: process.env.OLLAMA_API_URL || "http://localhost:11434/api/chat",
    model: process.env.OLLAMA_MODEL || "llama3.2:3b",
    requestTimeout: parseInt(process.env.REQUEST_TIMEOUT, 10) || 10000,
    maxRetries: parseInt(process.env.MAX_RETRIES, 10) || 3,
  },
  gemini: {
    apiKey: process.env.GEMINI_API_KEY,
    model: "gemini-2.0-flash",
    config: {
      temperature: 1.4,
      topP: 0.8,
      topK: 64,
      maxOutputTokens: 4096,
      responseMimeType: "text/plain",
    },
  },
};

// Initialize Gemini client
const ai = new GoogleGenAI({ apiKey: CONFIG.gemini.apiKey });

export async function askAI(messages, format) {
  if (!Array.isArray(messages) || messages.length === 0) {
    throw new Error("Invalid messages array provided");
  }

  const payload = {
    model: CONFIG.ollama.model,
    messages,
    stream: false,
    format,
  };

  for (let attempt = 1; attempt <= CONFIG.ollama.maxRetries; attempt++) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(
        () => controller.abort(),
        CONFIG.ollama.requestTimeout
      );

      const response = await fetch(CONFIG.ollama.apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }

      const responseJson = await response.json();
      const responseText = responseJson.message?.content;

      if (!responseText) {
        throw new Error("Invalid response format from API");
      }

      // Clean and parse the response
      const cleanText = responseText.replace(/```json\n|```/g, "");
      return JSON.parse(cleanText);
    } catch (error) {
      console.error(
        `Attempt ${attempt}/${CONFIG.ollama.maxRetries} failed:`,
        error.message
      );

      if (attempt === CONFIG.ollama.maxRetries) {
        throw new Error(
          `Failed after ${CONFIG.ollama.maxRetries} attempts: ${error.message}`
        );
      }
    }
  }
}

export async function askGemini(instructions, messages, format) {
  console.log("🤖 [Gemini] Initializing request with instructions:");
  try {
    console.log("💬 [Gemini] Starting chat session");
    // Ensure messages is an array and format it properly for Gemini
    const history = Array.isArray(messages)
      ? messages.map((msg) => ({
          role: msg.role === "AI" ? "model" : "user",
          parts: [{ text: msg.content }],
        }))
      : [];

    const chatSession = ai.chats.create({
      model: CONFIG.gemini.model,
      systemInstruction: instructions,
      history: history,
      config: CONFIG.gemini.config,
    });

    console.log("📤 [Gemini] Sending message to Gemini API");
    const result = await chatSession.sendMessage({
      message: messages[messages.length - 1].parts[0].text,
    });
    console.log(
      "📥 [Gemini] Successfully received response from Gemini API",
      result
    );
    return result.text;
  } catch (error) {
    console.error("⚠️ [Gemini] API error:", error.message);
    throw new Error(`Gemini API error: ${error.message}`);
  }
}

export async function titleGenerator({ answer, instructions, format }) {
  console.log("🤖 [Gemini] Initializing request with instructions:");
  console.log("📤 [Gemini] Sending message to Gemini API");
  const ai = new GoogleGenAI({
    vertexai: false,
    apiKey: process.env.GEMINI_API_KEY,
  });
  const response = await ai.models.generateContent({
    model: "gemini-2.0-flash",
    contents: answer,
    config: {
      responseMimeType: "application/json",
      responseSchema: format,
    },
  });
  console.log("📥 [Gemini] Successfully received response from Gemini API");

  try {
    const jsonResponse = JSON.parse(response.text);
    return jsonResponse;
  } catch (parseError) {
    console.error("Failed to parse JSON response:", parseError);
    throw new Error(`Failed to parse Gemini response: ${parseError.message}`);
  }
}

export async function generateBlogPost({ instructions, contents }) {
  console.log("🤖 [Gemini] Initializing request with instructions:");
  const ai = new GoogleGenAI({
    vertexai: false,
    apiKey: process.env.GEMINI_API_KEY,
  });
  const response = await ai.models.generateContent({
    model: "gemini-2.0-flash",
    contents: contents,
    config: {
      systemInstruction: instructions,
      responseMimeType: "text/plain",
      maxOutputTokens: 4096,
      temperature: 1.4,
      topP: 0.5,
      topK: 64,
    },
  });
  console.debug(response.text);
  console.log("📥 [Gemini] Successfully received response from Gemini API");
  return response.text;
}
