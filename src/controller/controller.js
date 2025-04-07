import { askGemini } from "../models/models.js";

export const dreamsense = async (req, res) => {
  console.log("🌙 [Dreamsense] Received request");
  const { conversation } = req.body;

  if (!conversation) {
    console.log("❌ [Dreamsense] Error: Missing conversation body");
    return res.status(400).json({ error: "Conversation is required" });
  }

  console.log(
    "📝 [Dreamsense] Processing request with conversation:",
    JSON.stringify(conversation)
  );

  const instructions = `Act as a old kind sympathatic man with the following context:
You have deep expertise in psychology, dreams, and human brain
You have an IQ of 180
You have to clarify things I see in my dreams and try to find meaning behind them
You are very kind and have a lot of wisdom
Dreams are means to hidden factors that are hapenning in ones life at the moment and you will help me find out those things

Your mission is to:
Analyse my dreams properly
Find deep meanings if there is any
Dont go too deep if the description is bulllshit
List down all possible hidden messages behind my dreams
Be Short and sweet

For response:
Be very sympathetic
Try to comfort user as much as you can
MUST LIST DOWN ALL POSSIBLE HIDDEN MEANINGS WITH ONE LINE DESCRIPTION
At the end try to provide value to the user in some way
If the dreams were negative give them hope
If the dreams were possitive give them assurance
At the end try to ask some relatable question about the message above, but dont force it.

Persona:
You are an old wise man
Your name is Mr. Oval
You are very intillegent 
You hold a lot of wisdom
You are very sympathetic
Use medium simple english
      `;
  const messages = conversation;
  // const format = {
  //   type: "object",
  //   properties: {
  //     reply: {
  //       type: "string",
  //     },
  //     candidate_confidence_percentage: {
  //       type: "number",
  //     },
  //     lying_percentage: {
  //       type: "number",
  //     },
  //   },
  //   required: [
  //     "candidates_previous_response",
  //     "candidate_confidence_percentage",
  //     "lying_percentage",
  //   ],
  // };

  console.log("🚀 [Dreamsense] Sending request to Gemini model");
  try {
    const response = await askGemini(instructions, conversation);
    console.log("✅ [Dreamsense] Successfully received response from Gemini");
    res.json({ success: true, message: response });
  } catch (error) {
    console.error("💥 [Dreamsense] Error processing request:", error);
    res.status(500).json({ success: false, error: "Internal server error" });
  }
};
