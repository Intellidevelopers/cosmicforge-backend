"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = __importDefault(require("mongoose"));
var workingDays;
(function (workingDays) {
    workingDays["mondays-only"] = "mondays-only";
    workingDays["tuesdays-only"] = "tuesdays-only";
    workingDays["wednessdays-only"] = "wednessdays-only";
    workingDays["thursdays-only"] = "thursdays-only";
    workingDays["fridays-only"] = "fridays-only";
    workingDays["saturdays-only"] = "saturdays-only";
    workingDays["monday-tuesday"] = "monday-tuesday";
    workingDays["monday-wednessday"] = "monday-wednessday";
    workingDays["monday-thurdays"] = "monday-thursday";
    workingDays["monday-friday"] = "monday-friday";
    workingDays["monday-saturday"] = "monday-saturday";
    workingDays["tuesday-wednessday"] = "tuesday-wednessday";
    workingDays["tuesday-thursday"] = "tuesday-thursday";
    workingDays["tuesday-friday"] = "tuesday-friday";
    workingDays["tuesday-saturday"] = "tuesday-saturday";
    workingDays["wednessday-thursday"] = "wednessday-thursday";
    workingDays["wedness-friday"] = "wednessday-friday";
    workingDays["wednessday-saturday"] = "wednessday-saturday";
    workingDays["thursday-friday"] = "thursday-friday";
    workingDays["thursday-saturday"] = "thursday-saturday";
    workingDays["friday-saturday"] = "friday-saturday";
})(workingDays || (workingDays = {}));
const workingHourSchema = new mongoose_1.default.Schema({
    workingDays: { type: mongoose_1.default.SchemaTypes.String,
        enum: workingDays
    },
    workingTime: { type: mongoose_1.default.SchemaTypes.String }
});
const experienceSchema = new mongoose_1.default.Schema({
    hospitalName: {
        type: mongoose_1.default.SchemaTypes.String
    },
    specializationOrDepartment: {
        type: mongoose_1.default.SchemaTypes.String
    },
    noOfPatientTreated: {
        type: mongoose_1.default.SchemaTypes.String
    },
    date: {
        type: mongoose_1.default.SchemaTypes.String
    },
});
const mapLocationSchema = new mongoose_1.default.Schema({
    latitude: { type: mongoose_1.default.SchemaTypes.String },
    longitude: { type: mongoose_1.default.SchemaTypes.String }
});
const medicalPersonnelProfileSchema = new mongoose_1.default.Schema({
    userId: {
        type: mongoose_1.default.SchemaTypes.ObjectId,
        ref: 'users'
    },
    mobileNo: {
        type: mongoose_1.default.SchemaTypes.String
    },
    professionalTitle: {
        type: mongoose_1.default.SchemaTypes.String
    },
    specializationTitle: {
        type: mongoose_1.default.SchemaTypes.String
    },
    currentClinic: {
        type: mongoose_1.default.SchemaTypes.String
    },
    department: {
        type: mongoose_1.default.SchemaTypes.String
    },
    location: {
        type: mongoose_1.default.SchemaTypes.String
    },
    profilePicture: {
        type: mongoose_1.default.SchemaTypes.String
    },
    mapLocation: mapLocationSchema,
    experience: {
        type: experienceSchema
    },
    bio: {
        type: mongoose_1.default.SchemaTypes.String
    },
    workTime: workingHourSchema,
    pricing: {
        type: mongoose_1.default.SchemaTypes.BigInt,
        default: 0,
        min: [0, 'pricing can not be less than zero.']
    },
    earlistAvailability: {
        type: mongoose_1.default.SchemaTypes.Date
    }
});
const MedicalPersonnelProfileModel = mongoose_1.default.model('medicalPersonnelProfile', medicalPersonnelProfileSchema);
exports.default = MedicalPersonnelProfileModel;
