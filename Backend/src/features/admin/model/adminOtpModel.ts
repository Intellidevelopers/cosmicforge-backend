import mongoose from "mongoose";

const adminOtpSchema = new mongoose.Schema({
  adminDetails: {
    email: {
      type: mongoose.SchemaTypes.String,
      required: true,
      lowercase: true,
      trim: true,
    },
  },
  otpCode: {
    type: mongoose.SchemaTypes.Number,
    required: true,
    min: [100000, "OTP code must be 6 digits"],
    max: [999999, "OTP code must be 6 digits"],
  },
  expiringTime: {
    type: Date,
    required: true,
  },
}, { timestamps: true });

// Optional: auto-delete expired OTPs using TTL index
adminOtpSchema.index({ expiringTime: 1 }, { expireAfterSeconds: 0 });

export default mongoose.model("admin_otp", adminOtpSchema);
