import { askGemini } from "../models/models.js";

export const interview = async (req, res) => {
  const { role, conversation } = req.body;

  if (!role || !conversation) {
    console.log("Role or conversation is missing:");
    return res
      .status(400)
      .json({ error: "Role and conversation are required" });
  }

  const instructions = `Act as a strict interviewer conducting job interviews for a competitive position. Your role is to assess candidates rigorously, looking for any signs of insincerity, dishonesty, or attempts to fake qualifications. Develop a series of challenging, open-ended questions that gauge not only the candidates' technical skills but also their character and authenticity. Provide insights on how to interpret their responses, identify potential red flags, and ensure a fair evaluation process. Include tips on how to create an atmosphere that encourages genuine responses while also maintaining a firm and professional demeanor. Enable me to fully understand the interviewing techniques and psychological considerations involved in detecting dishonesty.
      You must only ask 5-6 questions. And after that acknowledge the candidate's response and just tell them that you will get back to them with the results.
      The interviews is for the position of: ${role}. Now start the interview with the first question.
      `;
  // const messages = [
  //   {
  //     role: "user",
  //     content: `Act as a strict interviewer conducting job interviews for a competitive position. Your role is to assess candidates rigorously, looking for any signs of insincerity, dishonesty, or attempts to fake qualifications. Develop a series of challenging, open-ended questions that gauge not only the candidates' technical skills but also their character and authenticity. Provide insights on how to interpret their responses, identify potential red flags, and ensure a fair evaluation process. Include tips on how to create an atmosphere that encourages genuine responses while also maintaining a firm and professional demeanor. Enable me to fully understand the interviewing techniques and psychological considerations involved in detecting dishonesty.
  //     You must only ask 5-6 questions. And after that acknowledge the candidate's response and just tell them that you will get back to them with the results.
  //     The interviews is for the position of: ${role}. Now start the interview with the first question.
  //     `
  //   },
  //   ...conversation
  // ];

  const format = {
    type: "object",
    properties: {
      reply: {
        type: "string",
      },
      candidate_confidence_percentage: {
        type: "number",
      },
      lying_percentage: {
        type: "number",
      },
    },
    required: [
      "candidates_previous_response",
      "candidate_confidence_percentage",
      "lying_percentage",
    ],
  };

  const response = await askGemini(instructions, conversation, format);
  res.json({ success: true, message: response });
};
