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
exports.updateProfile = void 0;
const CODE_1 = __importDefault(require("../../../../util/interface/CODE"));
const newUserModel_1 = __importDefault(require("../../../newUser/model/newUserModel"));
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const profileModel_1 = __importDefault(require("../model/profileModel"));
const UserRole_1 = require("../../../../util/interface/UserRole");
const cloudinary_1 = __importDefault(require("../../../../config/cloudinary/cloudinary"));
const updateProfile = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    var _a;
    try {
        const user = req.user;
        if (!user._id || user._id === undefined || user._id === "") {
            res.status(CODE_1.default.Forbidden).json({
                title: 'Update Profile Message',
                status: CODE_1.default.Forbidden,
                successful: false,
                message: 'You not authorized to continue.'
            });
            return;
        }
        if (user.role != UserRole_1.USER_ROLES.DOCTOR) {
            res.status(CODE_1.default.Forbidden).json({
                title: 'Update Profile Message',
                status: CODE_1.default.Forbidden,
                successful: false,
                message: 'You not authorized to continue.'
            });
            return;
        }
        const { email, mobileNo, professionalTitle, specialization, currentClinic, department, location, profilePicture } = req.body;
        if (!email && !mobileNo && !professionalTitle && !specialization && !currentClinic && !location && !profilePicture && !department) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Update Profile Message',
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: 'Either email,mobileNo,professionalTitle,specialization,currentClinic,department,location,profilePicture field is needed to continue.'
            });
            return;
        }
        //update token if email is channged
        let token = null;
        if (email && email !== user.email) {
            yield newUserModel_1.default.findOneAndUpdate({ _id: user._id }, {
                email
            });
            const updatedTokenObject = {
                _id: user._id,
                email,
                password: user.password,
                fullName: user.fullName,
                lastName: user.lastName,
                role: user.role
            };
            token = jsonwebtoken_1.default.sign(updatedTokenObject, (_a = process.env) === null || _a === void 0 ? void 0 : _a.JWT_SECRET, { expiresIn: '30d' });
        }
        let userProfile = yield profileModel_1.default.findOne({ _id: user._id });
        const userAccount = yield newUserModel_1.default.findOne({ _id: user._id });
        if (profilePicture) {
            const regex = /^data:image\/(png|jpg|jpeg|gif);base64,/i;
            if (!regex.test(profilePicture)) {
                res.status(CODE_1.default.BAD_REQUEST).json({
                    title: 'Update Profile Message',
                    status: CODE_1.default.BAD_REQUEST,
                    successful: false,
                    message: 'Invalid profile picture format provided.'
                });
                return;
            }
        }
        if (userProfile) {
            let profileUrl = null;
            if (profilePicture) {
                profileUrl = yield new Promise((resolve, reject) => {
                    cloudinary_1.default.upload(profilePicture, {
                        folder: user._id.concat('/profile')
                    }, (error, uploadedResult) => {
                        if (error) {
                            reject(error.message);
                        }
                        resolve(uploadedResult === null || uploadedResult === void 0 ? void 0 : uploadedResult.secure_url);
                    });
                });
            }
            yield userProfile.updateOne({
                profilePicture: profileUrl !== null && profileUrl !== void 0 ? profileUrl : userProfile.profilePicture,
                professionalTitle: professionalTitle !== null && professionalTitle !== void 0 ? professionalTitle : userProfile.professionalTitle,
                mobileNo: mobileNo !== null && mobileNo !== void 0 ? mobileNo : userProfile.mobileNo,
                specializationTitle: specialization !== null && specialization !== void 0 ? specialization : userProfile.specializationTitle,
                currentClinic: currentClinic !== null && currentClinic !== void 0 ? currentClinic : userProfile.currentClinic,
                department: department !== null && department !== void 0 ? department : userProfile.department,
                location: location !== null && location !== void 0 ? location : userProfile.location
            }, {
                returnOriginal: false
            });
            userProfile = yield profileModel_1.default.findOne({ _id: user._id });
            if (token) {
                const updatedProfile = Object.assign(Object.assign({}, userAccount), { profile: userProfile, token });
                res.status(CODE_1.default.SUCCESS).json({
                    title: 'Update Profile Message',
                    status: CODE_1.default.SUCCESS,
                    successful: true,
                    message: 'Successfully Updated Profile',
                    data: updatedProfile
                });
                return;
            }
            const convertToObject = userProfile === null || userProfile === void 0 ? void 0 : userProfile.toObject();
            const updatedProfile = Object.assign(Object.assign({}, userAccount === null || userAccount === void 0 ? void 0 : userAccount.toObject()), { profile: convertToObject });
            res.status(CODE_1.default.SUCCESS).json({
                title: 'Update Profile Message',
                status: CODE_1.default.SUCCESS,
                successful: true,
                message: 'Successfully Updated Profile',
                data: updatedProfile
            });
            return;
        }
        let profileUrl = null;
        if (profilePicture) {
            profileUrl = yield new Promise((resolve, reject) => {
                cloudinary_1.default.upload(profilePicture, {
                    folder: user._id.concat('/profile')
                }, (error, uploadedResult) => {
                    if (error) {
                        reject(error.message);
                    }
                    resolve(uploadedResult === null || uploadedResult === void 0 ? void 0 : uploadedResult.secure_url);
                });
            });
        }
        let createProfileforUser = new profileModel_1.default({
            userId: user._id,
            profilePicture: profileUrl,
            mobileNo,
            professionalTitle,
            specialization,
            currentClinic,
            department,
            location
        });
        yield createProfileforUser.save();
        if (token) {
            const updatedProfile = Object.assign(Object.assign({}, userAccount), { profile: createProfileforUser, token });
            res.status(CODE_1.default.SUCCESS).json({
                title: 'Update Profile Message',
                status: CODE_1.default.SUCCESS,
                successful: true,
                message: 'Successfully Updated Profile',
                data: updatedProfile
            });
            return;
        }
        const updatedProfile = Object.assign(Object.assign({}, userAccount === null || userAccount === void 0 ? void 0 : userAccount.toObject()), { profile: createProfileforUser });
        res.status(CODE_1.default.SUCCESS).json({
            title: 'Update Profile Message',
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: 'Successfully Updated Profile',
            data: updatedProfile
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: 'Update Profile Message',
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: true,
            message: 'An error occured.',
            error: error.message
        });
    }
});
exports.updateProfile = updateProfile;
