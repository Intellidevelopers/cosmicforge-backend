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
exports.googleSignUpSignInAuthcontroller = void 0;
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const tempRoleModel_1 = require("../model/tempRoleModel");
const CODE_1 = __importDefault(require("../../util/interface/CODE"));
const newUserModel_1 = __importDefault(require("../../features/newUser/model/newUserModel"));
const UserRole_1 = require("../../util/interface/UserRole");
const patientProfileModel_1 = __importDefault(require("../../features/patient/profile/model/patientProfileModel"));
const profileModel_1 = __importDefault(require("../../features/medicalPersonnel/profile/model/profileModel"));
const bcryptjs_1 = __importDefault(require("bcryptjs"));
const googleSignUpSignInAuthcontroller = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const savedData = yield tempRoleModel_1.userTempRoleModel.find();
    const salt = yield bcryptjs_1.default.genSalt(10);
    const secretKey = yield bcryptjs_1.default.hash(process.env.JWT_SECRET, salt);
    const userRole = savedData[0].userRole;
    console.log(userRole);
    if (!userRole) {
        res.status(CODE_1.default.BAD_REQUEST).json({
            message: 'Something went wrong try again.'
        });
        return;
    }
    const userDetails = req.user._json;
    const userAccount = yield newUserModel_1.default.findOne({
        email: userDetails.email
    });
    if (userAccount) {
        yield tempRoleModel_1.userTempRoleModel.deleteMany();
        if (userAccount.role === UserRole_1.USER_ROLES.CLIENT.toString()) {
            const userProfile = yield patientProfileModel_1.default.findOne({
                userId: userAccount._id
            });
            const token = jsonwebtoken_1.default.sign(Object.assign({}, userAccount.toJSON()), process.env.JWT_SECRET, { expiresIn: '30d' });
            const encode = jsonwebtoken_1.default.sign(Object.assign(Object.assign({}, userAccount.toJSON()), { userProfile: userProfile === null || userProfile === void 0 ? void 0 : userProfile.toJSON(), token,
                secretKey }), process.env.JWT_SECRET, { expiresIn: Math.floor(Date.now() / 1000) + 300 });
            console.log(process.env.JWT_SECRET);
            res.redirect(`${process.env.web_base_url}account?token=${encode}`);
            return;
        }
        else if (userAccount.role === UserRole_1.USER_ROLES.DOCTOR.toString()) {
            const userProfile = yield profileModel_1.default.findOne({
                userId: userAccount._id
            });
            const token = jsonwebtoken_1.default.sign(Object.assign({}, userAccount.toJSON()), process.env.JWT_SECRET, { expiresIn: '30d' });
            const encode = jsonwebtoken_1.default.sign(Object.assign(Object.assign({}, userAccount.toJSON()), { userProfile: userProfile === null || userProfile === void 0 ? void 0 : userProfile.toJSON(), token,
                secretKey }), process.env.JWT_SECRET, { expiresIn: '5mins' });
            yield tempRoleModel_1.userTempRoleModel.deleteMany();
            res.redirect(`${process.env.web_base_url}account?token=${encode}`);
            return;
        }
        return;
    }
    const newAccount = yield new newUserModel_1.default({
        email: userDetails.email,
        fullName: userDetails.name.split(' ')[1],
        lastName: userDetails.name.split(' ')[0],
        role: userRole
    }).save();
    const token = jsonwebtoken_1.default.sign(Object.assign({}, newAccount.toJSON()), process.env.JWT_SECRET, { expiresIn: '30d' });
    const encode = jsonwebtoken_1.default.sign(Object.assign(Object.assign({}, newAccount.toJSON()), { token,
        secretKey }), process.env.JWT_SECRET, { expiresIn: '5mins' });
    yield tempRoleModel_1.userTempRoleModel.deleteMany();
    res.redirect(`${process.env.web_base_url}account?token=${encode}`);
});
exports.googleSignUpSignInAuthcontroller = googleSignUpSignInAuthcontroller;
