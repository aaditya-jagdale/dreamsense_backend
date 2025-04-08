import { askGemini, titleGenerator } from "../models/models.js";
import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";

dotenv.config();

// Create a single supabase client for interacting with your database
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_API_KEY
);

export const dreamsense = async (req, res) => {
  console.log("🌙 [Dreamsense] Received request");
  const { conversation } = req.body;

  if (!conversation) {
    console.log("❌ [Dreamsense] Error: Missing conversation body");
    return res.status(400).json({ error: "Conversation is required" });
  }

  let { data: prompt, error } = await supabase
    .from("daily_read")
    .select()
    .eq("id", 1)
    .single();

  if (error) {
    console.error("❌ [Dreamsense] Supabase Error:", error);
    return res.status(500).json({ error: "Failed to fetch chat data" });
  }

  if (!prompt) {
    console.log("❌ [Dreamsense] No chat data found with id 1");
    return res.status(404).json({ error: "Chat data not found" });
  }

  console.log("📝 [Dreamsense] Processing request with conversation:");

  const instructions = prompt.contents;

  console.log("🚀 [Dreamsense] Sending request to Gemini model", prompt);
  try {
    const response = await askGemini(instructions, conversation);
    console.log("✅ [Dreamsense] Successfully received response from Gemini");
    res.json({ success: true, message: response });
  } catch (error) {
    console.error("💥 [Dreamsense] Error processing request:", error);
    res.status(500).json({ success: false, error: "Internal server error" });
  }
};

export const getChatInfo = async (req, res) => {
  const { answer } = req.body;

  if (!answer) {
    console.log("❌ [Dreamsense] Error: Missing answer body");
    return res.status(400).json({ error: "Answer is required" });
  }

  const instructions = `
  Your job is to analyze the given paragraph and find then summarize the contents in the required format properly. All the values must be accurate and properly analyzed.
  `;

  const conversation = {
    conversation: [
      {
        role: "user",
        parts: [
          {
            text: answer,
          },
        ],
      },
    ],
  };

  const format = {
    type: "object",
    properties: {
      dream_title: {
        type: "string",
      },
      dream_summary: {
        type: "array",
        items: {
          type: "string",
        },
      },
      hidden_meanings: {
        type: "array",
        items: {
          type: "string",
        },
      },
    },
    required: ["dream_title", "dream_summary", "hidden_meanings"],
  };

  try {
    const response = await titleGenerator({ answer, instructions, format });
    console.log("✅ [Dreamsense] Successfully received response from Gemini");
    res.json({ success: true, message: response });
  } catch (error) {
    console.error("💥 [Dreamsense] Error processing request:", error);
    res.status(500).json({ success: false, error: "Internal server error" });
  }
};
