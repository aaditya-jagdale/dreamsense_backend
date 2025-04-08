import { dreamsense, getChatInfo } from "../controller/dreamsense.js";
import { Router } from "express";
import express from "express";

const router = Router();

// Move middleware to before routes
router.use(express.json());
router.use(express.urlencoded({ extended: true }));

router.get("/", (req, res) => {
  res.send("Hello World!");
});

//AI Chat
router.post("/dreamsense", dreamsense);

//Get Chat Info
router.post("/get-chat-info", getChatInfo);

export default router;
