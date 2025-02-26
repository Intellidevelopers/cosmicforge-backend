"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.resetPassword = exports.validateResetPasswordOTP = exports.resendOtpToResetPassword = exports.sendOtpToResetPassword = exports.loginUser = void 0;
const CODE_1 = __importDefault(require("../../../util/interface/CODE"));
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const bcryptjs_1 = __importDefault(require("bcryptjs"));
const nodeMailer_1 = __importDefault(require("../../../config/mail/nodeMailer"));
const newUserModel_1 = __importDefault(require("../../newUser/model/newUserModel"));
const otpGenerator_1 = __importDefault(require("../../../util/otpGenerator"));
const resetPasswordModel_1 = __importDefault(require("../../newUser/model/resetPasswordModel"));
const bcryptjs_2 = __importDefault(require("bcryptjs"));
const UserRole_1 = require("../../../util/interface/UserRole");
const patientProfileModel_1 = __importDefault(require("../../patient/profile/model/patientProfileModel"));
const profileModel_1 = __importDefault(require("../../medicalPersonnel/profile/model/profileModel"));
const loginUser = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        // console.log(await newUserModel.find())
        const { email, password } = req.body;
        if (!email || !password) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Login Message",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "email and password fields are required to continue.",
            });
            return;
        }
        const userAccount = yield newUserModel_1.default.findOne({ email });
        if (!userAccount) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Login Message",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Invalid account detials provided.",
            });
            return;
        }
        const passwordValid = yield bcryptjs_1.default.compare(password, userAccount === null || userAccount === void 0 ? void 0 : userAccount.password);
        if (!passwordValid) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Login Message",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Invalid account detials provided.",
            });
            return;
        }
        const token = jsonwebtoken_1.default.sign(Object.assign({}, userAccount.toObject()), process.env.JWT_SECRET, { expiresIn: '30d' });
        yield (0, nodeMailer_1.default)({
            receiver: userAccount.email, subject: "Successfull Login.", emailData: {
                fullName: `${userAccount.fullName} ${userAccount.lastName}`
            }, template: "login-success.ejs"
        });
        switch (userAccount.role) {
            case UserRole_1.USER_ROLES.CLIENT.toString(): {
                const clientPtofile = yield patientProfileModel_1.default.findOne({ userId: userAccount._id });
                res.status(CODE_1.default.SUCCESS).json({
                    title: "Login Message",
                    status: CODE_1.default.SUCCESS,
                    successful: true,
                    message: "Welcome back to cosmic",
                    data: Object.assign(Object.assign({}, userAccount.toObject()), { profile: clientPtofile, token })
                });
                return;
            }
            case UserRole_1.USER_ROLES.DOCTOR.toString(): {
                const medicPtofile = yield profileModel_1.default.findOne({ userId: userAccount._id });
                res.status(CODE_1.default.SUCCESS).json({
                    title: "Login Message",
                    status: CODE_1.default.SUCCESS,
                    successful: true,
                    message: "Welcome back to cosmic",
                    data: Object.assign(Object.assign({}, userAccount.toObject()), { profile: medicPtofile, token })
                });
                return;
            }
            default: return res.status(CODE_1.default.UNAUTHORIZED).json({
                title: "Login Message",
                status: CODE_1.default.UNAUTHORIZED,
                successful: false,
                message: "Invalid account detials provided.",
            });
        }
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: "Login Message",
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "An error occured.",
            error: error.message
        });
    }
});
exports.loginUser = loginUser;
const sendOtpToResetPassword = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { email } = req.body;
        if (!email) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Password Message',
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Email is needed to continue."
            });
            return;
        }
        const userAccount = yield newUserModel_1.default.findOne({ email });
        const cachedOTP = yield resetPasswordModel_1.default.findOne({ "userDetails.email": email });
        if (cachedOTP) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Password Message',
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "User already on the process please use resend otp to get new otp if not gotten."
            });
            return;
        }
        if (!userAccount) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Password Message',
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Invalid email provided."
            });
            return;
        }
        const token = yield (0, otpGenerator_1.default)();
        //send otp to email
        yield (0, nodeMailer_1.default)({
            receiver: email, emailData: {
                fullName: `${userAccount.fullName} ${userAccount.lastName}`,
                token: token
            }, subject: "Reset Password", template: "reset-password.ejs"
        });
        const cacheOTP = new resetPasswordModel_1.default({
            userDetails: {
                email,
                fullName: `${userAccount.fullName} ${userAccount.lastName}`
            },
            otpCode: token,
            expiringTime: new Date(Date.now() + 5 * 60 * 1000),
        });
        yield cacheOTP.save();
        res.status(CODE_1.default.SUCCESS).json({
            title: 'Reset Password  Message',
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: "Otp sent to user email"
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: 'Reset Password  Message',
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "An error occured.",
            error: error.message
        });
    }
});
exports.sendOtpToResetPassword = sendOtpToResetPassword;
const resendOtpToResetPassword = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    var _a, _b;
    const { email } = req.body;
    try {
        const isUserAlreadySentOtp = yield resetPasswordModel_1.default.findOne({ "userDetails.email": email });
        if (!isUserAlreadySentOtp) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "No otp sent to user.",
            });
            return;
        }
        const otpExpiringTime = new Date(isUserAlreadySentOtp === null || isUserAlreadySentOtp === void 0 ? void 0 : isUserAlreadySentOtp.expiringTime).getTime();
        if (otpExpiringTime > Date.now()) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Pasword Message',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "Otp already sent to this user and will expire in th next 5mins.",
            });
            return;
        }
        //send user otp
        const otp = yield (0, otpGenerator_1.default)();
        yield isUserAlreadySentOtp.updateOne({
            otpCode: otp,
            expiringTime: new Date(Date.now() + 5 * 60 * 1000)
        });
        (0, nodeMailer_1.default)({
            receiver: (_a = isUserAlreadySentOtp.userDetails) === null || _a === void 0 ? void 0 : _a.email,
            subject: "Reset Password Otp",
            emailData: {
                fullName: (_b = isUserAlreadySentOtp.userDetails) === null || _b === void 0 ? void 0 : _b.fullName,
                token: otp
            },
            template: 'reset-password.ejs'
        }).then(result => {
            res.status(CODE_1.default.SUCCESS).json({
                title: 'Register new user message',
                successful: true,
                status: CODE_1.default.SUCCESS,
                message: "Otp sent to user.",
            });
        }).catch(err => {
            res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
                title: 'Register new user message',
                successful: false,
                status: CODE_1.default.INTERNAL_SERVER_ERROR,
                message: "An error occured.",
                error: err.message
            });
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: 'Reset Password Message',
            successful: false,
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message
        });
    }
});
exports.resendOtpToResetPassword = resendOtpToResetPassword;
const validateResetPasswordOTP = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { email, otp } = req.body;
        if (!email || !otp) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "email and otp field are needed to continue.",
            });
            return;
        }
        const isUserAlreadySentOtp = yield resetPasswordModel_1.default.findOne({ "userDetails.email": email });
        if (!isUserAlreadySentOtp) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Pssword Message.',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "No otp sent to user.",
            });
            return;
        }
        if (otp !== isUserAlreadySentOtp.otpCode) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Password Mssage',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "Invalid otp provided.",
            });
            return;
        }
        const otpExpiringTime = new Date(isUserAlreadySentOtp === null || isUserAlreadySentOtp === void 0 ? void 0 : isUserAlreadySentOtp.expiringTime).getTime();
        if (otpExpiringTime < Date.now()) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Password Mssage',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "Cannot validate an expired otp.",
            });
            return;
        }
        yield isUserAlreadySentOtp.updateOne({
            isOtpValidated: true
        });
        res.status(CODE_1.default.SUCCESS).json({
            title: 'Reset Password Message',
            successful: false,
            status: CODE_1.default.SUCCESS,
            message: "Validated otp you can continue with password reset.",
            otp
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: 'Reset Password Message',
            successful: false,
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message
        });
    }
});
exports.validateResetPasswordOTP = validateResetPasswordOTP;
const resetPassword = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    var _a;
    try {
        const { password, otp } = req.body;
        if (!password || !otp) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "password and otp  field are needed to continue.",
            });
            return;
        }
        //check if otp is validated
        const cachedOTP = yield resetPasswordModel_1.default.findOne({ otpCode: otp });
        if (!cachedOTP) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "User otp not valid.",
            });
            return;
        }
        //check if otp is  validated
        if (!cachedOTP.isOtpValidated) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "User otp not valid.",
            });
            return;
        }
        const strongPasswordPattern = /^(?=.*[A-Za-z])(?=.*[A-Z a-z\d ])(?=.*[@$!*#?.&])[A-Za-z\d@$!*.#?&]{10,}$/;
        if (!strongPasswordPattern.test(password)) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "Password must contain words, characters and numbers.",
            });
            return;
        }
        const salt = yield bcryptjs_2.default.genSalt(10);
        const newHashedPassword = yield bcryptjs_2.default.hash(password, salt);
        yield newUserModel_1.default.findOneAndUpdate({ email: (_a = cachedOTP.userDetails) === null || _a === void 0 ? void 0 : _a.email }, {
            password: newHashedPassword
        });
        yield resetPasswordModel_1.default.deleteOne({ otpCode: otp });
        res.status(CODE_1.default.SUCCESS).json({
            title: 'Reset Password Message',
            successful: true,
            status: CODE_1.default.SUCCESS,
            message: "Password successfully changed.",
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: 'Reset Password Message',
            successful: false,
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message
        });
    }
});
exports.resetPassword = resetPassword;
