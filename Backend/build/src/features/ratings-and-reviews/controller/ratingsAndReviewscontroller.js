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
exports.getRatings = exports.get_5_star_ratings = exports.get_4_star_ratings = exports.get_3_star_ratings = exports.get_2_star_ratings = exports.get_1_star_ratings = exports.rate_and_review_a_doctor = void 0;
const mongoose_1 = __importDefault(require("mongoose"));
const CODE_1 = __importDefault(require("../../../util/interface/CODE"));
const patientProfileModel_1 = __importDefault(require("../../patient/profile/model/patientProfileModel"));
const ratingsAndReviewsModel_1 = require("../model/ratingsAndReviewsModel");
const newUserModel_1 = __importDefault(require("../../newUser/model/newUserModel"));
const UserRole_1 = require("../../../util/interface/UserRole");
const rate_and_review_a_doctor = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = req.user;
        if (!user) {
            res.status(CODE_1.default.Forbidden).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.Forbidden,
                successful: false,
                message: "You are not authorized"
            });
            return;
        }
        if (user.role !== UserRole_1.USER_ROLES.CLIENT.toString()) {
            res.status(CODE_1.default.UNAUTHORIZED).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.UNAUTHORIZED,
                successful: false,
                message: "you are not authorized"
            });
            return;
        }
        const { doctorId, rating, review } = req.body;
        if (!doctorId || !rating) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Atleast doctorId and rating  fields are needed to continue."
            });
            return;
        }
        const isDoctorIdValid = mongoose_1.default.Types.ObjectId.isValid(doctorId);
        if (!isDoctorIdValid) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Invalid id provided."
            });
            return;
        }
        const isDoctorRegistered = yield newUserModel_1.default.findOne({ _id: doctorId });
        if (!isDoctorRegistered || isDoctorRegistered.role !== UserRole_1.USER_ROLES.DOCTOR.toString()) {
            res.status(CODE_1.default.BAD_REQUEST).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.BAD_REQUEST,
                successful: false,
                message: "Account not registered."
            });
            return;
        }
        const userProfile = yield patientProfileModel_1.default.findOne({ userId: user._id });
        let isReviewedAlready = yield ratingsAndReviewsModel_1.RatingsAndReviewsModel.findOne({
            doctorReviewed: doctorId,
            patientReviewing: user._id
        });
        if (isReviewedAlready) {
            isReviewedAlready = yield isReviewedAlready.updateOne({
                rating: rating,
                rewiew: review !== null && review !== void 0 ? review : isReviewedAlready.rewiew,
            }, { new: true });
            res.status(CODE_1.default.SUCCESS).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.SUCCESS,
                successful: true,
                message: "Successfully.",
                data: isReviewedAlready
            });
            return;
        }
        const rateAndReview = new ratingsAndReviewsModel_1.RatingsAndReviewsModel({
            doctorReviewed: doctorId,
            patientReviewing: user._id,
            patienFullName: `${user.lastName} ${user.lastName}`,
            patientProfile: userProfile === null || userProfile === void 0 ? void 0 : userProfile.profilePicture,
            rewiew: review !== null && review !== void 0 ? review : '',
            rating: rating
        });
        yield rateAndReview.save();
        res.status(CODE_1.default.SUCCESS).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: "Successfully.",
            data: rateAndReview
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "Internal Server Error.",
            error: error.message
        });
    }
});
exports.rate_and_review_a_doctor = rate_and_review_a_doctor;
const get_1_star_ratings = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = req.user;
        if (!user) {
            res.status(CODE_1.default.Forbidden).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.Forbidden,
                successful: false,
                message: "You are not authorized"
            });
            return;
        }
        if (user.role !== UserRole_1.USER_ROLES.CLIENT.toString()) {
            res.status(CODE_1.default.UNAUTHORIZED).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.UNAUTHORIZED,
                successful: false,
                message: "you are not authorized"
            });
            return;
        }
        const OneStarRating = yield ratingsAndReviewsModel_1.RatingsAndReviewsModel.find({ rating: 1 });
        res.status(CODE_1.default.SUCCESS).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: "Successfully.",
            data: {
                total: OneStarRating.length,
                ratings: OneStarRating
            }
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "Internal Server Error.",
            error: error.message
        });
    }
});
exports.get_1_star_ratings = get_1_star_ratings;
const get_2_star_ratings = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = req.user;
        if (!user) {
            res.status(CODE_1.default.Forbidden).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.Forbidden,
                successful: false,
                message: "You are not authorized"
            });
            return;
        }
        if (user.role !== UserRole_1.USER_ROLES.CLIENT.toString()) {
            res.status(CODE_1.default.UNAUTHORIZED).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.UNAUTHORIZED,
                successful: false,
                message: "you are not authorized"
            });
            return;
        }
        const twoStarRatings = yield ratingsAndReviewsModel_1.RatingsAndReviewsModel.find({ rating: 2 });
        res.status(CODE_1.default.SUCCESS).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: "Successfully.",
            data: {
                total: twoStarRatings.length,
                ratings: twoStarRatings
            }
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "Internal Server Error.",
            error: error.message
        });
    }
});
exports.get_2_star_ratings = get_2_star_ratings;
const get_3_star_ratings = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = req.user;
        if (!user) {
            res.status(CODE_1.default.Forbidden).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.Forbidden,
                successful: false,
                message: "You are not authorized"
            });
            return;
        }
        if (user.role !== UserRole_1.USER_ROLES.CLIENT.toString()) {
            res.status(CODE_1.default.UNAUTHORIZED).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.UNAUTHORIZED,
                successful: false,
                message: "you are not authorized"
            });
            return;
        }
        const twoStarRatings = yield ratingsAndReviewsModel_1.RatingsAndReviewsModel.find({ rating: 3 });
        res.status(CODE_1.default.SUCCESS).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: "Successfully.",
            data: {
                total: twoStarRatings.length,
                ratings: twoStarRatings
            }
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "Internal Server Error.",
            error: error.message
        });
    }
});
exports.get_3_star_ratings = get_3_star_ratings;
const get_4_star_ratings = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = req.user;
        if (!user) {
            res.status(CODE_1.default.Forbidden).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.Forbidden,
                successful: false,
                message: "You are not authorized"
            });
            return;
        }
        if (user.role !== UserRole_1.USER_ROLES.CLIENT.toString()) {
            res.status(CODE_1.default.UNAUTHORIZED).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.UNAUTHORIZED,
                successful: false,
                message: "you are not authorized"
            });
            return;
        }
        const fourStarRatings = yield ratingsAndReviewsModel_1.RatingsAndReviewsModel.find({ rating: 4 });
        res.status(CODE_1.default.SUCCESS).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: "Successfully.",
            data: {
                total: fourStarRatings.length,
                ratings: fourStarRatings
            }
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "Internal Server Error.",
            error: error.message
        });
    }
});
exports.get_4_star_ratings = get_4_star_ratings;
const get_5_star_ratings = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = req.user;
        if (!user) {
            res.status(CODE_1.default.Forbidden).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.Forbidden,
                successful: false,
                message: "You are not authorized"
            });
            return;
        }
        if (user.role !== UserRole_1.USER_ROLES.CLIENT.toString()) {
            res.status(CODE_1.default.UNAUTHORIZED).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.UNAUTHORIZED,
                successful: false,
                message: "you are not authorized"
            });
            return;
        }
        const fiveStarRatings = yield ratingsAndReviewsModel_1.RatingsAndReviewsModel.find({ rating: 5 });
        res.status(CODE_1.default.SUCCESS).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: "Successfully.",
            data: {
                total: fiveStarRatings.length,
                ratings: fiveStarRatings
            }
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "Internal Server Error.",
            error: error.message
        });
    }
});
exports.get_5_star_ratings = get_5_star_ratings;
const getRatings = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const user = req.user;
        if (!user) {
            res.status(CODE_1.default.Forbidden).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.Forbidden,
                successful: false,
                message: "You are not authorized"
            });
            return;
        }
        if (user.role !== UserRole_1.USER_ROLES.CLIENT.toString()) {
            res.status(CODE_1.default.UNAUTHORIZED).json({
                title: "Ratings And Review Message.",
                status: CODE_1.default.UNAUTHORIZED,
                successful: false,
                message: "you are not authorized"
            });
            return;
        }
        const allRatings = yield ratingsAndReviewsModel_1.RatingsAndReviewsModel.find();
        res.status(CODE_1.default.SUCCESS).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.SUCCESS,
            successful: true,
            message: "Successfully.",
            data: {
                total: allRatings.length,
                ratings: allRatings
            }
        });
    }
    catch (error) {
        res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
            title: "Ratings And Review Message.",
            status: CODE_1.default.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "Internal Server Error.",
            error: error.message
        });
    }
});
exports.getRatings = getRatings;
