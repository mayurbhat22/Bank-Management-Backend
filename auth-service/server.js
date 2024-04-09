const express = require("express");
const bodyParser = require("body-parser");
const nodemailer = require("nodemailer");
const speakeasy = require("speakeasy");
const dotenv = require("dotenv");
dotenv.config();
const app = express();
const port = process.env.PORT;
const cors = require("cors");
const qrcode = require("qrcode");
// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// CORS
app.use(
  cors({
    origin: "*",
    credentials: true,
  })
);

// In-memory storage for email verification codes
const emailVerificationCodes = {};
const userSecrets = {};
// Nodemailer configuration
const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: process.env.EMAIL,
    pass: process.env.APP_PASSWORD,
  },
});
transporter.verify(function (error, success) {
  if (error) {
    console.log(error);
  } else {
    console.log("SMTP server is ready to take our messages");
  }
});
// Route to request email verification
app.post("/verify-email", (req, res) => {
  const email = req.body.email;
  if (!email) {
    return res.status(400).send("Email is required.");
  }

  // Generate random OTP
  const otp = speakeasy.totp({
    secret: speakeasy.generateSecret().base32,
    digits: 6,
  });

  // Store OTP with email
  emailVerificationCodes[email] = otp;

  // Send email with OTP
  const mailOptions = {
    from: process.env.EMAIL,
    to: email,
    subject: "Email Verification OTP",
    text: `Your OTP is: ${otp}`,
  };

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
      console.log(error);
      return res.status(500).send("Error sending email.");
    }
    console.log("Email sent: " + info.response);
    res.status(200).send("Email sent successfully.");
  });
});

// Route to verify OTP
app.post("/verify-otp", (req, res) => {
  const email = req.body.email;
  const otp = req.body.otp;

  if (!email || !otp) {
    return res.status(400).send("Email and OTP are required.");
  }

  // Check if OTP matches
  if (emailVerificationCodes[email] === otp) {
    delete emailVerificationCodes[email];
    return res.status(200).send("Email verified successfully.");
  } else {
    return res.status(400).send("Invalid OTP.");
  }
});
app.post("/enable-2fa", (req, res) => {
  const username = req.body.username; // Assuming you have a userId for the user
  const secret = speakeasy.generateSecret({ length: 20 });
  userSecrets[username] = secret;

  // Generate QR code
  qrcode.toDataURL(secret.otpauth_url, (err, dataUrl) => {
    if (err) {
      console.error("Error generating QR code:", err);
      return res.status(500).send("Error generating QR code");
    }
    res.json({ secret: secret.base32, qrCode: dataUrl });
  });
});

// Route to verify OTP
app.post("/verify-secret", (req, res) => {
  const username = req.body.username;
  const clientSecret = req.body.clientSecret;

  const secret = userSecrets[username];
  if (!secret) {
    return res.status(400).send("2FA not enabled for this user");
  }

  const verified = speakeasy.totp.verify({
    secret: secret.base32,
    encoding: "base32",
    token: clientSecret,
    window: 1, // Allow for time drift of 1 interval (30 seconds by default)
  });

  if (verified) {
    // Clear secret after successful verification
    delete userSecrets[username];
    return res.status(200).send("OTP verified successfully");
  } else {
    return res.status(400).send("Invalid OTP");
  }
});
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
