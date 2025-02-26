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
exports.updateVitalSigns = exports.updatePatientProfile = void 0;
const CODE_1 = __importDefault(require("../../../../util/interface/CODE"));
const UserRole_1 = require("../../../../util/interface/UserRole");
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const newUserModel_1 = __importDefault(require("../../../newUser/model/newUserModel"));
const patientProfileModel_1 = __importDefault(require("../model/patientProfileModel"));
const cloudinary_1 = __importDefault(require("../../../../config/cloudinary/cloudinary"));
var profileType;
(function (profileType) {
    profileType[profileType["personal"] = 0] = "personal";
    profileType[profileType["family"] = 1] = "family";
})(profileType || (profileType = {}));
const updatePatientProfile = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    var _a;
    try {
        const user = req.user;
        if (!user || user.role !== UserRole_1.USER_ROLES.CLIENT) {
            res.status(CODE_1.default.Forbidden).json({
                title: 'Update Profile Message',
                status: CODE_1.default.Forbidden,
                successful: false,
                message: 'UnAuthorized access.'
            });
            return;
        }
        const { email, mobileNo, homeAddress, workAddress, profilePicture } = req.body;
        if (!email && !mobileNo && !homeAddress && !workAddress && !profilePicture) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Update Profile Message',
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: 'Either email,mobileNo,homeAddress,workAddress,profilePicture is needed to continue .'
            });
            return;
        }
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
        let userProfile = yield patientProfileModel_1.default.findOne({ userId: user._id });
        const userAccount = yield newUserModel_1.default.findOne({ _id: user._id });
        if (userProfile) {
            let profileUrl = null;
            if (profilePicture) {
                profileUrl = yield new Promise((resolve, reject) => {
                    cloudinary_1.default.upload(profilePicture, {
                        folder: user._id.concat('/profile')
                    }, (error, uploadedResult) => {
                        if (error) {
                            reject(error);
                        }
                        resolve(uploadedResult === null || uploadedResult === void 0 ? void 0 : uploadedResult.secure_url);
                    });
                });
            }
            yield userProfile.updateOne({
                profilePicture: profileUrl !== null && profileUrl !== void 0 ? profileUrl : userProfile.profilePicture,
                homeAddress: homeAddress !== null && homeAddress !== void 0 ? homeAddress : userProfile.homeAddress,
                mobileNo: mobileNo !== null && mobileNo !== void 0 ? mobileNo : userProfile.mobileNo,
                workAddress: workAddress !== null && workAddress !== void 0 ? workAddress : userProfile.workAddress,
            }, {
                new: true,
                returnDocument: 'after'
            });
            userProfile = yield patientProfileModel_1.default.findOne({ userId: user._id });
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
            const updatedProfile = Object.assign(Object.assign({}, userAccount === null || userAccount === void 0 ? void 0 : userAccount.toObject()), { profile: userProfile });
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
                        reject(error);
                    }
                    resolve(uploadedResult === null || uploadedResult === void 0 ? void 0 : uploadedResult.secure_url);
                });
            });
        }
        let createProfileforUser = new patientProfileModel_1.default({
            userId: user._id,
            profilePicture: profileUrl,
            mobileNo,
            homeAddress,
            workAddress,
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
exports.updatePatientProfile = updatePatientProfile;
const updateVitalSigns = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = req.user;
        if (!user || user.role !== UserRole_1.USER_ROLES.CLIENT) {
            res.status(CODE_1.default.Forbidden).json({
                title: 'Update Profile Message',
                status: CODE_1.default.Forbidden,
                successful: false,
                message: 'UnAuthorized access.'
            });
            return;
        }
        const { bloodPressure, bodyTemperature, oxygenSaturation, weight, height, profileType, dateOfBirth, gender } = req.body;
        if (!bloodPressure || !bodyTemperature || !oxygenSaturation || !weight || !height || !profileType || !dateOfBirth || !gender) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: 'Update Vital Signs Message',
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: 'bloodPressure,bodyTemperature,oxygenSaturation,weight,height,profileType,dateOfBirth,gender fields are needed to '
            });
            return;
        }
        let userProfile = yield patientProfileModel_1.default.findOne({ userId: user._id });
        const userAccount = yield newUserModel_1.default.findOne({ _id: user._id });
        if (userProfile) {
            yield userProfile.updateOne({ vitalSigns: {
                    bloodPressure,
                    bodyTemperature,
                    oxygenSaturation,
                    weight,
                    height,
                    gender,
                    dateOfBirth
                },
                profileType }, {
                new: true
            });
            userProfile = yield patientProfileModel_1.default.findOne({ userId: user._id });
            res.status(CODE_1.default.SUCCESS).json({
                title: 'Update Vital Signs Message',
                status: CODE_1.default.SUCCESS,
                successful: true,
                message: 'successfully updated vital signs. ',
                data: Object.assign(Object.assign({}, userAccount === null || userAccount === void 0 ? void 0 : userAccount.toObject()), { profile: userProfile })
            });
            return;
        }
        const newProfile = new patientProfileModel_1.default({
            vitalSigns: {
                bloodPressure,
                bodyTemperature,
                oxygenSaturation,
                weight,
                height,
                gender,
                dateOfBirth
            },
            profileType
        });
        yield newProfile.save();
        res.status(CODE_1.default.SUCCESS).json({
            title: 'Update Vital Signs Message',
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: 'successfully updated vital signs. ',
            data: Object.assign(Object.assign({}, userAccount === null || userAccount === void 0 ? void 0 : userAccount.toObject()), { profile: newProfile })
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: 'Update Vital Signs Message',
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: 'An error occured.',
            error: error.message
        });
    }
});
exports.updateVitalSigns = updateVitalSigns;
