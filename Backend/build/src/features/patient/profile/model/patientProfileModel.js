"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = __importDefault(require("mongoose"));
const patientVitalSignsSchema = new mongoose_1.default.Schema({
    bodyTemperature: {
        type: mongoose_1.default.SchemaTypes.String
    },
    bloodPressure: {
        type: mongoose_1.default.SchemaTypes.String
    },
    oxygenSaturation: {
        type: mongoose_1.default.SchemaTypes.String
    },
    weight: {
        type: mongoose_1.default.SchemaTypes.String
    },
    height: {
        type: mongoose_1.default.SchemaTypes.String
    },
    gender: {
        type: mongoose_1.default.SchemaTypes.String,
        enum: ['male', 'female']
    },
    dateOfBirth: {
        type: mongoose_1.default.SchemaTypes.String,
    },
});
const patientProfileSchema = new mongoose_1.default.Schema({
    userId: {
        type: mongoose_1.default.SchemaTypes.ObjectId,
        ref: 'users'
    },
    profileType: {
        type: mongoose_1.default.SchemaTypes.String,
        enum: ['personal', 'family']
    },
    mobileNo: {
        type: mongoose_1.default.SchemaTypes.String
    },
    homeAddress: {
        type: mongoose_1.default.SchemaTypes.String
    },
    workAddress: {
        type: mongoose_1.default.SchemaTypes.String
    },
    profilePicture: {
        type: mongoose_1.default.SchemaTypes.String
    },
    vitalSigns: {
        type: patientVitalSignsSchema
    }
});
const PatientProfileModel = mongoose_1.default.model('patientProfile', patientProfileSchema);
exports.default = PatientProfileModel;
