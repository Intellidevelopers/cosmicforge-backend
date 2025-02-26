"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.RatingsAndReviewsModel = void 0;
const mongoose_1 = __importDefault(require("mongoose"));
const RatingsAndReviewsSchema = new mongoose_1.default.Schema({
    doctorReviewed: {
        type: mongoose_1.default.SchemaTypes.ObjectId,
        ref: 'users'
    },
    patientReviewing: {
        type: mongoose_1.default.SchemaTypes.ObjectId,
        ref: 'users'
    },
    patientProfile: {
        type: mongoose_1.default.SchemaTypes.String,
    },
    patienFullName: {
        type: mongoose_1.default.SchemaTypes.String,
    },
    rating: {
        type: mongoose_1.default.SchemaTypes.Number,
        min: [0, 'ratings can not be lesser than 0'],
        max: [5, 'ratings can not be greater than 5'],
        required: [true, 'rating is needed.']
    },
    rewiew: {
        type: mongoose_1.default.SchemaTypes.String,
    },
    createdAt: {
        type: mongoose_1.default.SchemaTypes.Date,
        default: Date.now()
    }
});
exports.RatingsAndReviewsModel = mongoose_1.default.model('ratings-and-reviews', RatingsAndReviewsSchema);
