"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const login_1 = require("../controller/login");
/**
 * @swagger
 * /api/v1/cosmicforge/user/login:
 *     post:
 *        summary: Complete the registration process with validated otp.
 *        tags: [Login]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     email:
 *                                       type: email
 *                                       description: fullName required.
 *
 *                                     password:
 *                                       type: string
 *                                       description: password required .
 *
 *                             required:
 *                               -email
 *                               -password
 *
 *        responses:
 *                200:
 *                 description: Login user after providing valid details.
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
/**
 * @swagger
 * /api/v1/cosmicforge/user/reset-password-otp:
 *     post:
 *        summary: A user provide email  and he/she is sent an otp code.
 *        tags: [Forgot Password]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     email:
 *                                       type: string
 *                                       format: email
 *                                       description: A email required to send otp for reseting password.
 *                           required:
 *                               -email
 *        responses:
 *                200:
 *                 description: User sent otp after providing a valid email
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
/**
 * @swagger
 * /api/v1/cosmicforge/user/resend-reset-password-otp:
 *     post:
 *        summary: This will resend otp to user.
 *        tags: [Forgot Password]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     email:
 *                                       type: string
 *                                       format: email
 *                                       description: A email required to send otp for reseting password.
 *                           required:
 *                               -email
 *        responses:
 *                200:
 *                 description: User sent otp after providing a valid email
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
/**
 * @swagger
 * /api/v1/cosmicforge/user/validate-reset-password-otp:
 *     post:
 *        summary: This will validate the otp for reserting user password.
 *        tags: [Forgot Password]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     email:
 *                                       type: string
 *                                       format: email
 *                                       description: A email required to send otp for verification.
 *                                     otp:
 *                                       type: number
 *                                       format: password
 *                                       description: Otp needed to continue.
 *
 *                             required:
 *                               -email
 *        responses:
 *                200:
 *                 description: User sent otp after providing a valid email
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
/**
 * @swagger
 * /api/v1/cosmicforge/user/reset-password:
 *     post:
 *        summary: Reset usr password when valid otp is provided.
 *        tags: [Forgot Password]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     password:
 *                                       type: string
 *                                       description: password required .
 *                                     otp:
 *                                       type: number
 *                                       description: otp validated otp
 *                             required:
 *                               -password
 *                               -otp
 *        responses:
 *                200:
 *                 description: User sent a successful response message.
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
const loginRouter = express_1.default.Router();
loginRouter.post("/login", (req, res) => {
    (0, login_1.loginUser)(req, res);
});
loginRouter.post('/reset-password-otp', login_1.sendOtpToResetPassword);
loginRouter.post('/resend-reset-password-otp', login_1.resendOtpToResetPassword);
loginRouter.post('/validate-reset-password-otp', login_1.validateResetPasswordOTP);
loginRouter.post('/reset-password', login_1.resetPassword);
exports.default = loginRouter;
