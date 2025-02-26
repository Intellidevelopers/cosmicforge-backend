"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const ratingsAndReviewscontroller_1 = require("../controller/ratingsAndReviewscontroller");
const userAuthenticationMiddleware_1 = __importDefault(require("../../../middleware/userAuthenticationMiddleware"));
const rateAndReviewRouter = express_1.default.Router();
/**
 * @swagger
 * /api/v1/cosmicforge/user/patient/rate-and-review:
 *     put:
 *        summary: A user gives ratings and reviews to doctor.
 *        tags: [Patient]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     rating:
 *                                       type: string
 *                                       format: string
 *                                       description: rating.
 *                                     review:
 *                                       type: string
 *                                       format: string
 *                                       description: review.
 *                                     doctorId:
 *                                       type: string
 *                                       format: string
 *                                       description: doctorId.
 *
 *        responses:
 *                200:
 *                 description: Update user profile.
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
/**
 * @swagger
 * /api/v1/cosmicforge/user/patient/ratings-and-reviews:
 *     get:
 *        summary: Get all ratings.
 *        tags: [Patient]
 *
 *        responses:
 *                200:
 *                 description: Update user profile.
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
/**
 * @swagger
 * /api/v1/cosmicforge/user/patient/ratings-and-reviews/one-star:
 *     get:
 *        summary: Get one star ratings.
 *        tags: [Patient]
 *
 *        responses:
 *                200:
 *                 description: Update user profile.
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
/**
 * @swagger
 * /api/v1/cosmicforge/user/patient/ratings-and-reviews/two-stars:
 *     get:
 *        summary: Get two star ratings.
 *        tags: [Patient]
 *
 *        responses:
 *                200:
 *                 description: Update user profile.
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
/**
 * @swagger
 * /api/v1/cosmicforge/user/patient/ratings-and-reviews/three-stars:
 *     get:
 *        summary: Get three star ratings.
 *        tags: [Patient]
 *
 *        responses:
 *                200:
 *                 description: Update user profile.
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
/**
 * @swagger
 * /api/v1/cosmicforge/user/patient/ratings-and-reviews/four-stars:
 *     get:
 *        summary: Get four star ratings.
 *        tags: [Patient]
 *
 *        responses:
 *                200:
 *                 description: Update user profile.
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
/**
 * @swagger
 * /api/v1/cosmicforge/user/patient/ratings-and-reviews/five-stars:
 *     get:
 *        summary: Get  five star ratings.
 *        tags: [Patient]
 *
 *        responses:
 *                200:
 *                 description: Update user profile.
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *
 *
 *
 *
 *
 *
 */
rateAndReviewRouter.put('/rate-and-review', userAuthenticationMiddleware_1.default, ratingsAndReviewscontroller_1.rate_and_review_a_doctor);
rateAndReviewRouter.get('/ratings-and-reviews/all', userAuthenticationMiddleware_1.default, ratingsAndReviewscontroller_1.getRatings);
rateAndReviewRouter.get('/ratings-and-reviews/one-star', userAuthenticationMiddleware_1.default, ratingsAndReviewscontroller_1.get_1_star_ratings);
rateAndReviewRouter.get('/ratings-and-reviews/two-stars', userAuthenticationMiddleware_1.default, ratingsAndReviewscontroller_1.get_2_star_ratings);
rateAndReviewRouter.get('/ratings-and-reviews/three-stars', userAuthenticationMiddleware_1.default, ratingsAndReviewscontroller_1.get_3_star_ratings);
rateAndReviewRouter.get('/ratings-and-reviews/four-stars', userAuthenticationMiddleware_1.default, ratingsAndReviewscontroller_1.get_4_star_ratings);
rateAndReviewRouter.get('/ratings-and-reviews/five-stars', userAuthenticationMiddleware_1.default, ratingsAndReviewscontroller_1.get_5_star_ratings);
exports.default = rateAndReviewRouter;
