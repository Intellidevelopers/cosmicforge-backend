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
exports.completeRegistrationProcess = exports.validateOTP = exports.resendOTP = exports.registerNewUser = void 0;
const CODE_1 = __importDefault(require("../../../util/interface/CODE"));
const newUserModel_1 = __importDefault(require("../../../features/newUser/model/newUserModel"));
const otpVerificationModel_1 = __importDefault(require("../model/otpVerificationModel"));
const otpGenerator_1 = __importDefault(require("../../../util/otpGenerator"));
const nodeMailer_1 = __importDefault(require("../../../config/mail/nodeMailer"));
const bcryptjs_1 = __importDefault(require("bcryptjs"));
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const registerNewUser = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { email } = req.body;
        if (!email) {
            return res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Register User Message",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Email field is required to continue."
            });
        }
        // console.log(await UsersModel.deleteMany())
        const isEmailAlreadyRegistered = yield newUserModel_1.default.findOne({ email });
        if (isEmailAlreadyRegistered) {
            return res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Register User Message",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Email provided already registered."
            });
        }
        // await OTPModel.deleteMany()
        const isUserAlreadySentOtp = yield otpVerificationModel_1.default.findOne({ "userDetails.email": email });
        if (isUserAlreadySentOtp) {
            return res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Register User Message",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Already sent otp to email and verify otp and complete rigisteration."
            });
            return;
        }
        //send user otp
        const otp = yield (0, otpGenerator_1.default)();
        const storeOTP = new otpVerificationModel_1.default({
            userDetails: {
                email
            },
            expiringTime: new Date(Date.now() + 5 * 60 * 1000),
            otpCode: otp
        });
        yield storeOTP.save();
        (0, nodeMailer_1.default)({
            receiver: email,
            subject: "Otp Code For Registration",
            emailData: {
                email,
                otp
            },
            template: 'send-user-otp.ejs'
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
            title: 'Register new user message',
            successful: false,
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message
        });
    }
});
exports.registerNewUser = registerNewUser;
const resendOTP = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    var _a;
    const { email } = req.body;
    try {
        const isUserAlreadySentOtp = yield otpVerificationModel_1.default.findOne({ "userDetails.email": email });
        if (!isUserAlreadySentOtp) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Register new user message',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "No otp sent to user.",
            });
            return;
        }
        const otpExpiringTime = new Date(isUserAlreadySentOtp === null || isUserAlreadySentOtp === void 0 ? void 0 : isUserAlreadySentOtp.expiringTime).getTime();
        if (otpExpiringTime > Date.now()) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Register new user message',
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
            subject: "Otp Code For Registration",
            emailData: {
                email,
                otp
            },
            template: 'send-user-otp.ejs'
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
            title: 'Register new user message',
            successful: false,
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message
        });
    }
});
exports.resendOTP = resendOTP;
const validateOTP = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const { email, otp } = req.body;
        const isUserAlreadySentOtp = yield otpVerificationModel_1.default.findOne({ "userDetails.email": email });
        if (!isUserAlreadySentOtp) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Otp validation message',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "No otp sent to user.",
            });
            return;
        }
        if (otp !== isUserAlreadySentOtp.otpCode) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Otp validation message',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "Invalid otp provided.",
            });
            return;
        }
        const otpExpiringTime = new Date(isUserAlreadySentOtp === null || isUserAlreadySentOtp === void 0 ? void 0 : isUserAlreadySentOtp.expiringTime).getTime();
        if (otpExpiringTime < Date.now()) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Register new user message',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "Can not validate an expired otp.",
            });
            return;
        }
        yield isUserAlreadySentOtp.updateOne({
            isOtpValidated: true
        });
        res.status(CODE_1.default.SUCCESS).json({
            title: 'Otp validation message',
            successful: false,
            status: CODE_1.default.SUCCESS,
            message: "Validated otp you can continue with registration.",
            otp
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: 'Register new user message',
            successful: false,
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message
        });
    }
});
exports.validateOTP = validateOTP;
const completeRegistrationProcess = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    var _a, _b;
    try {
        const { fullName, lastName, password, role, otp } = req.body;
        const otpData = yield otpVerificationModel_1.default.findOne({ otpCode: otp });
        if (!otpData) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Complete registration message.',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "Invalid otp provided.",
            });
            return;
        }
        if (!otpData.isOtpValidated) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Complete registration message.',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "Otp not validated please validate otp.",
            });
            return;
        }
        const userEmail = (_a = otpData.userDetails) === null || _a === void 0 ? void 0 : _a.email;
        const userAlreadyExistWithEmail = yield newUserModel_1.default.find({
            email: userEmail
        });
        if (!userAlreadyExistWithEmail) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Complete registration message.',
                successful: false,
                status: CODE_1.default.BAD_REQUEST,
                message: "Can not register this email at this time.",
            });
            return;
        }
        const salt = yield bcryptjs_1.default.genSalt(10);
        const hashedPassword = yield bcryptjs_1.default.hash(password, salt);
        const newUser = new newUserModel_1.default({
            fullName,
            lastName,
            email: userEmail,
            password: hashedPassword,
            role
        });
        yield newUser.save();
        const token = jsonwebtoken_1.default.sign(Object.assign({}, newUser.toObject()), (_b = process === null || process === void 0 ? void 0 : process.env) === null || _b === void 0 ? void 0 : _b.JWT_SECRET, { expiresIn: '30d' });
        yield otpVerificationModel_1.default.deleteOne({ "userDetails.email": userEmail });
        yield (0, nodeMailer_1.default)({ receiver: newUser.email, subject: "Successfull Sign up.", emailData: {
                fullName: `${newUser.fullName} ${newUser.lastName}`
            }, template: "sign-up-success.ejs" });
        res.status(CODE_1.default.SUCCESS).json({
            title: 'Complete registration message.',
            successful: true,
            status: CODE_1.default.SUCCESS,
            message: "Successfully registered welcome on board!!!",
            data: Object.assign(Object.assign({}, newUser.toObject()), { token })
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: 'Complete registration message.',
            successful: false,
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message
        });
    }
});
exports.completeRegistrationProcess = completeRegistrationProcess;
