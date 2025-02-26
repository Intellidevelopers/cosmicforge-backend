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
exports.getSpecificDoctorAppointments = exports.bookAppointment = void 0;
const mongoose_1 = __importDefault(require("mongoose"));
const CODE_1 = __importDefault(require("../../../util/interface/CODE"));
const UserRole_1 = require("../../../util/interface/UserRole");
const newUserModel_1 = __importDefault(require("../../newUser/model/newUserModel"));
const bookAppointmentModel_1 = __importDefault(require("../model/bookAppointmentModel"));
const bookAppointment = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = req.user;
        if (!user) {
            res.status(CODE_1.default.Forbidden).json({
                title: "Book Appointment Message.",
                status: CODE_1.default.Forbidden,
                successful: false,
                message: "You are not authorized"
            });
            return;
        }
        if (user.role !== UserRole_1.USER_ROLES.CLIENT.toString()) {
            res.status(CODE_1.default.UNAUTHORIZED).json({
                title: "Book Appointment Message.",
                status: CODE_1.default.UNAUTHORIZED,
                successful: false,
                message: "you are not authorized"
            });
            return;
        }
        const { doctorId, day, month, year, meridianType, hour, minutes, appointmentType, payment } = req.body;
        if (!doctorId || !day || !month || !month || !year || !meridianType || !hour || !minutes || !appointmentType) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Book Appointment Message.",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "doctorId,day,month,year,meridianType,hour,minutes and appointmentType fields are needed to continue."
            });
            return;
        }
        const isPaymentObjectEmpty = Object.entries(payment).every(([key, value]) => {
            if (payment['consultationFee'] === '') {
                return true;
            }
            if (payment['total'] === '') {
                return true;
            }
        });
        if (isPaymentObjectEmpty) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Book Appointment Message.",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Atleast consultationFee and total is needed to continue."
            });
            return;
        }
        const isDoctorIdValid = mongoose_1.default.Types.ObjectId.isValid(doctorId);
        if (!isDoctorIdValid) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Book Appointment Message.",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Invalid id provided."
            });
            return;
        }
        const isDoctorRegistered = yield newUserModel_1.default.findOne({ _id: user._id });
        if (!isDoctorRegistered) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Book Appointment Message.",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Invalid id provided."
            });
            return;
        }
        let createCustomDate = null;
        if (meridianType === 'pm') {
            createCustomDate = new Date(Number(year), Number(Number(month) - 1), Number(day), Number(Number(hour) + 12), Number(minutes), 0, 0);
        }
        else {
            createCustomDate = new Date(Number(year), Number(Number(month) - 1), Number(day), Number(hour), Number(minutes), 0, 0);
        }
        const newAppointment = new bookAppointmentModel_1.default({
            medicalPersonelID: doctorId,
            patientID: user._id,
            appointmentType: appointmentType,
            appointmentDate: createCustomDate.getTime(),
            payment
        });
        yield newAppointment.save();
        res.status(CODE_1.default.SUCCESS).json({
            title: "Book Appointment Message.",
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: "Successfully booked appointment.",
            data: newAppointment.toObject()
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: "Book Appointment Message.",
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "Internal Server Error.",
            error: error.message
        });
    }
});
exports.bookAppointment = bookAppointment;
const getSpecificDoctorAppointments = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = req.user;
        if (!user) {
            res.status(CODE_1.default.Forbidden).json({
                title: "Book Appointment Message.",
                status: CODE_1.default.Forbidden,
                successful: false,
                message: "You are not authorized"
            });
            return;
        }
        if (user.role !== UserRole_1.USER_ROLES.DOCTOR.toString()) {
            res.status(CODE_1.default.UNAUTHORIZED).json({
                title: "Book Appointment Message.",
                status: CODE_1.default.UNAUTHORIZED,
                successful: false,
                message: "you are not authorized"
            });
            return;
        }
        const appointments = yield bookAppointmentModel_1.default.find({ medicalPersonelID: user._id }).sort('-1');
        res.status(CODE_1.default.SUCCESS).json({
            title: "Book Appointment Message.",
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: "Successfully fetched.",
            data: {
                totalAppointments: appointments.length,
                appointments
            }
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: "Book Appointment Message.",
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "Internal Server Error.",
            error: error.message
        });
    }
});
exports.getSpecificDoctorAppointments = getSpecificDoctorAppointments;
