"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = __importDefault(require("mongoose"));
const paymentSchema = new mongoose_1.default.Schema({
    consultationFee: {
        type: mongoose_1.default.SchemaTypes.String,
    },
    cardType: {
        type: mongoose_1.default.SchemaTypes.String,
        enum: ['individual', 'family']
    },
    cardFee: {
        type: mongoose_1.default.SchemaTypes.BigInt,
        default: 0,
        min: [0, 'can not be less than 0']
    },
    vat: {
        type: mongoose_1.default.SchemaTypes.Number,
        default: 0,
        min: [0, 'can not be less than 0']
    },
    total: {
        type: mongoose_1.default.SchemaTypes.Number,
        default: 0,
        min: [0, 'can not be less than 0']
    },
    paymentStatus: {
        type: mongoose_1.default.SchemaTypes.String,
        enum: ['pending', 'success', 'failed'],
        default: 'pending'
    }
});
const BookAppointmentSchema = new mongoose_1.default.Schema({
    medicalPersonelID: {
        type: mongoose_1.default.SchemaTypes.ObjectId,
        ref: 'medicalPersonnelProfile',
        required: [true, ' medicalPersonelID is needed to continue.']
    },
    patientID: {
        type: mongoose_1.default.SchemaTypes.ObjectId,
        ref: 'patientProfile',
        required: [true, ' medicalPersonelID is needed to continue.']
    },
    appointmentDate: {
        type: mongoose_1.default.SchemaTypes.Date
    },
    appointmentType: {
        type: mongoose_1.default.SchemaTypes.String,
        enum: ['Virtual', 'In-Person']
    },
    payment: paymentSchema,
    appointmentStatus: {
        type: mongoose_1.default.SchemaTypes.String,
        enum: ['booked', 'cancelled', 'resheduled', 'completed'],
        default: 'booked'
    },
    createdAt: {
        type: mongoose_1.default.SchemaTypes.Date,
    }
});
const BookAppointmentModel = mongoose_1.default.model('bookAppointment', BookAppointmentSchema);
exports.default = BookAppointmentModel;
