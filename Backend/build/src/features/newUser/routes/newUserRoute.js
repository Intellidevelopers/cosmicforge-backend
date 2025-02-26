"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const newUser_1 = require("../controller/newUser");
const route = express_1.default.Router();
/**
 * @swagger
 * /api/v1/cosmicforge/user/signup:
 *     post:
 *        summary: A user provide email  and he/she is sent an otp code.
 *        tags: [Registeration]
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
 * /api/v1/cosmicforge/user/resend-otp:
 *     post:
 *        summary: This will resend otp to user.
 *        tags: [Registeration]
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
 * /api/v1/cosmicforge/user/validate-otp:
 *     post:
 *        summary: This will validate the otp for completing registeration.
 *        tags: [Registeration]
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
 * /api/v1/cosmicforge/user/complete-registration:
 *     post:
 *        summary: Complete the registration process with validated otp.
 *        tags: [Registeration]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     fullName:
 *                                       type: string
 *                                       description: fullName required.
 *                                     lastName:
 *                                       type: string
 *                                       description: lastName of user.
 *                                     password:
 *                                       type: string
 *                                       pattern: '^[A-Za-z0-9\d@$!*.#?&]{12,2}'
 *                                       description: password required .
 *                                     role:
 *                                       type: string
 *                                       description: role required to continue.
 *                                     otp:
 *                                       type: string
 *                                       pattern: '^[0-9]{6}'
 *                                       description: otp validated otp
 *                             required:
 *                               -fullName
 *                               -lastName
 *                               -password
 *                               -role
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
 * /getData:
 *     get:
 *        summary: Receive user detail such as email and send user otp code.
 *        tags: [Admin]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:
 *                     application/json:
 *                           schema:
 *                             type: object
 *                           properties:
 *                                     email:
 *                                       type: string
 *                                       format: email
 *                                       description: A email required to send otp for verification.
 *                           required:
 *                               -email
 *
 *        responses:
 *                200:
 *                 description: User sent otp after providing a valid email
 *        content:
 *         application/json:
 *                shema:
 *                   type: object
 *         items:
 *           $ref:'#/component/schemas/User/signup
 *         parameters: ['email']
 *
 *
 *
 */
route.post('/signup', (req, res) => {
    (0, newUser_1.registerNewUser)(req, res);
});
route.post('/resend-otp', (req, res) => {
    (0, newUser_1.resendOTP)(req, res);
});
route.post('/validate-otp', (req, res) => {
    (0, newUser_1.validateOTP)(req, res);
});
route.post('/complete-registration', (req, res) => {
    (0, newUser_1.completeRegistrationProcess)(req, res);
});
exports.default = route;
