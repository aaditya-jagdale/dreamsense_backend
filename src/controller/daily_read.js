import { createClient } from "@supabase/supabase-js";
import dotenv from "dotenv";
import {
  askGemini,
  generateBlogPost,
  titleGenerator,
} from "../models/models.js";

dotenv.config();

// Create a single supabase client for interacting with your database
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_API_KEY
);

export const generateDailyRead = async (req, res) => {
  console.log("🌙 [Daily Read] Received request");

  let { data: prompt, error } = await supabase
    .from("daily_read")
    .select()
    .eq("id", 2)
    .single();

  if (error) {
    console.error("❌ [Daily Read] Supabase Error:", error);
    return res.status(500).json({ error: "Failed to fetch prompt data" });
  }

  if (!prompt) {
    console.log("❌ [Daily Read] No prompt data found with id 2");
    return res.status(404).json({ error: "Prompt data not found" });
  }

  const contents =
    "Pick a random topic very carefully which is not too common and write a blog post on it";

  try {
    const blogContent = await generateBlogPost({
      instructions: prompt.contents,
      contents,
    });
    console.log("✅ [Dreamsense] Successfully received response from Gemini");

    const format = {
      type: "object",
      properties: {
        title: {
          type: "string",
        },
      },
      required: ["title"],
    };

    const title = await titleGenerator({
      answer: blogContent,
      instructions: prompt.contents,
      format,
    });

    try {
      const { data: insertData, error: insertError } = await supabase
        .from("daily_read")
        .insert({
          title: title.title,
          contents: blogContent,
        });

      if (insertError) {
        console.error(
          "❌ [Daily Read] Failed to upload to Supabase:",
          insertError
        );
        return res
          .status(500)
          .json({ success: false, error: "Failed to save daily read" });
      }

      res.json({
        success: true,
        data: {
          title: title.title,
          contents: blogContent,
        },
      });
    } catch (uploadError) {
      console.error(
        "❌ [Daily Read] Unexpected error during upload:",
        uploadError
      );
      res
        .status(500)
        .json({ success: false, error: "Failed to save daily read" });
    }
  } catch (error) {
    console.error("💥 [Dreamsense] Error processing request:", error);
    res.status(500).json({ success: false, error: "Internal server error" });
  }
};
