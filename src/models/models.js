import dotenv from "dotenv";
import fetch from "node-fetch";
import {
  GoogleGenerativeAI,
  HarmCategory,
  HarmBlockThreshold,
} from "@google/generative-ai";

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
    model: "gemini-2.0-flash-thinking-exp-01-21",
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
const genAI = new GoogleGenerativeAI(CONFIG.gemini.apiKey);

/**
 * Makes a request to the Ollama API with retry logic
 * @param {Array} messages - Array of message objects
 * @param {Object} format - Expected response format
 * @returns {Promise<Object|null>} Parsed response or null on failure
 */
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

/**
 * Makes a request to the Gemini API
 * @param {string} instructions - System instructions
 * @param {Array} messages - Array of previous messages
 * @param {Object} format - Expected response format
 * @returns {Promise<string>} Response text
 */
export async function askGemini(instructions, messages, format) {
  console.log("🤖 [Gemini] Initializing request with instructions:");
  try {
    const model = genAI.getGenerativeModel({
      model: CONFIG.gemini.model,
      systemInstruction: instructions,
    });

    console.log("💬 [Gemini] Starting chat session");
    // Ensure messages is an array and format it properly for Gemini
    const history = Array.isArray(messages)
      ? messages.map((msg) => ({
          role: msg.role === "AI" ? "model" : "user",
          parts: [{ text: msg.content }],
        }))
      : [];

    const chatSession = model.startChat({
      generationConfig: CONFIG.gemini.config,
      history: history,
    });

    console.log("📤 [Gemini] Sending message to Gemini API");
    const result = await chatSession.sendMessage(instructions);
    console.log("📥 [Gemini] Successfully received response from Gemini API");
    return result.response.text();
  } catch (error) {
    console.error("⚠️ [Gemini] API error:", error.message);
    throw new Error(`Gemini API error: ${error.message}`);
  }
}

export async function titleGenerator({ answer, instructions, format }) {
  console.log("🤖 [Gemini] Initializing request with instructions:");
  try {
    const model = genAI.getGenerativeModel({
      model: "gemini-2.0-flash",
      systemInstruction: instructions,
    });

    console.log("💬 [Gemini] Starting chat session");
    const chatSession = model.startChat({
      generationConfig: {
        temperature: 1.4,
        topP: 0.8,
        topK: 64,
        maxOutputTokens: 4096,
        responseMimeType: "application/json",
        responseSchema: format,
      },
      history: [],
    });

    console.log("📤 [Gemini] Sending message to Gemini API");
    const result = await chatSession.sendMessage(answer);
    console.log("📥 [Gemini] Successfully received response from Gemini API");

    try {
      const responseText = result.response.text();
      console.log("Raw response:", responseText);
      const response = JSON.parse(responseText);
      return response;
    } catch (parseError) {
      console.error("Failed to parse JSON response:", parseError);
      throw new Error(`Failed to parse Gemini response: ${parseError.message}`);
    }
  } catch (error) {
    console.error("⚠️ [Gemini] API error:", error.message);
    throw new Error(`Gemini API error: ${error.message}`);
  }
}

export async function generateBlogPost({ instructions, conversation }) {
  console.log("🤖 [Gemini] Initializing request with instructions:");
  try {
    const model = genAI.getGenerativeModel({
      model: "gemini-2.0-flash",
      systemInstruction: instructions.contents,
    });

    const blogFormat = {
      type: "object",
      properties: {
        title: {
          type: "string",
          description: "The title of the blog post",
        },
        content: {
          type: "string",
          description: "The main content of the blog post",
        },
      },
      required: ["title", "content"],
    };

    console.log("💬 [Gemini] Starting chat session");
    const chatSession = model.startChat({
      generationConfig: {
        ...CONFIG.gemini.config,
        responseMimeType: "application/json",
        responseSchema: blogFormat,
      },
      history: conversation.conversation.map((msg) => ({
        role: msg.role === "AI" ? "model" : "user",
        parts: msg.parts,
      })),
    });

    console.log("📤 [Gemini] Sending message to Gemini API");
    const result = await chatSession.sendMessage(instructions.contents);
    console.log("📥 [Gemini] Successfully received response from Gemini API");

    try {
      const responseText = result.response.text();
      console.log("Raw response:", responseText);
      const response = JSON.parse(responseText);
      return response;
    } catch (parseError) {
      console.error("Failed to parse JSON response:", parseError);
      throw new Error(`Failed to parse Gemini response: ${parseError.message}`);
    }
  } catch (error) {
    console.error("⚠️ [Gemini] API error:", error.message);
    throw new Error(`Gemini API error: ${error.message}`);
  }
}
