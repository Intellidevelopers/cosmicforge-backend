"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.errorHandler = void 0;
const CODE_1 = __importDefault(require("../util/interface/CODE"));
const errorHandler = (err, req, res, next) => {
    res.status(CODE_1.default.INTERNAL_SERVER_ERROR).json({
        title: "Server Error",
        status: CODE_1.default.INTERNAL_SERVER_ERROR,
        successful: false,
        message: 'An error occurred.',
        error: err.message
    });
    next();
};
exports.errorHandler = errorHandler;
