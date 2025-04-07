import { dreamsense } from "../controller/controller.js";
import { Router } from "express";
import express from "express";

const router = Router();

// Move middleware to before routes
router.use(express.json());
router.use(express.urlencoded({ extended: true }));

router.get("/", (req, res) => {
  res.send("Hello World!");
});

//Test route
router.post("/dreamsense", dreamsense);


export default router;
