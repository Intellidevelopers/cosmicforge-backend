"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const userAuthenticationMiddleware_1 = __importDefault(require("../../../../middleware/userAuthenticationMiddleware"));
const profileController_1 = require("../controller/profileController");
const medicalPersonnelProfileRouter = express_1.default.Router();
/**
 * @swagger
 * /api/v1/cosmicforge/user/medics/update-profile:
 *     put:
 *        summary: A user provides email, mobileNo, professionalTitle, specialization, currentClinic, department, location, profilePicture that he/she wants to update.
 *        tags: [Medics]
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
 *                                       description: new email to update.
 *                                     mobileNo:
 *                                       type: string
 *                                       format: phone
 *                                       pattern: '^\+234[0-9]{10}'
 *                                       description: mobile number to update.
 *                                     professionalTitle:
 *                                       type: string
 *                                       format: string
 *                                       description: professional title.
 *                                     specialization:
 *                                       type: string
 *                                       format: string
 *                                       description: professional.
 *                                     currentClinic:
 *                                       type: string
 *                                       format: string
 *                                       description: currentClinic.
 *                                     department:
 *                                       type: string
 *                                       format: string
 *                                       description: deparment.
 *                                     location:
 *                                       type: string
 *                                       format: string
 *                                       description: location.
 *                                     profilePicture:
 *                                       type: string
 *                                       format: string
 *                                       description: profilePicture.
 *
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
medicalPersonnelProfileRouter.put('/update-profile', userAuthenticationMiddleware_1.default, profileController_1.updateProfile);
exports.default = medicalPersonnelProfileRouter;
