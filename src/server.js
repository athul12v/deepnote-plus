const express = require("express");
const fs = require("fs");
const path = require("path");
const cors = require("cors");
const app = express();

app.use(cors());
app.use(express.json());

// Directory where transcriptions will be saved
const TRANSCRIPTIONS_DIR = path.join(__dirname, "transcriptions");

// Ensure directory exists
if (!fs.existsSync(TRANSCRIPTIONS_DIR)) {
  fs.mkdirSync(TRANSCRIPTIONS_DIR, { recursive: true });
}

// Save transcription endpoint
app.post("/save-transcription", (req, res) => {
  const { text, filename } = req.body;

  if (!text) {
    return res.status(400).json({ error: "No text provided." });
  }

  try {
    const sanitizedFilename = filename.replace(/[^a-z0-9-_.]/gi, "_"); // Prevent path traversal
    const filePath = path.join(TRANSCRIPTIONS_DIR, sanitizedFilename);
    fs.writeFileSync(filePath, text);
    res.json({ success: true, path: filePath });
  } catch (err) {
    res.status(500).json({ error: "Failed to save file." });
  }
});

// Summarization endpoint (existing)
app.post("/transcribe", (req, res) => {
  // Your existing summarization logic here
  res.json({ summary: "This is a placeholder summary." });
});

const PORT = 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));