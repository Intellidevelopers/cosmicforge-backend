"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = __importDefault(require("mongoose"));
const resetPasswordOtpVerificationSchema = new mongoose_1.default.Schema({
    userDetails: {
        email: {
            type: mongoose_1.default.SchemaTypes.String
        },
        fullName: {
            type: mongoose_1.default.SchemaTypes.String
        }
    },
    otpCode: {
        type: mongoose_1.default.SchemaTypes.Number,
        min: [6, "Otp code should not exceed 6 digit"]
    },
    expiringTime: {
        type: Date
    },
    isOtpValidated: {
        type: mongoose_1.default.SchemaTypes.Boolean,
        default: false
    }
});
exports.default = mongoose_1.default.model('resetPassword', resetPasswordOtpVerificationSchema);
