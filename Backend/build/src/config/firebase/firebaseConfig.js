"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
var _a;
Object.defineProperty(exports, "__esModule", { value: true });
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
const app_1 = require("firebase-admin/app");
const storage_1 = require("firebase-admin/storage");
const serviceJson = (_a = process === null || process === void 0 ? void 0 : process.env) === null || _a === void 0 ? void 0 : _a.firebaseService;
(0, app_1.initializeApp)({
    credential: (0, app_1.cert)(JSON.parse(serviceJson)),
    storageBucket: ""
});
const storage = (0, storage_1.getStorage)();
exports.default = storage;
