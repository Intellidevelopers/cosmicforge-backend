"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.userTempRoleModel = void 0;
const mongoose_1 = __importDefault(require("mongoose"));
const userTempRoleModelSchema = new mongoose_1.default.Schema({
    userRole: {
        type: mongoose_1.default.SchemaTypes.String
    }
});
exports.userTempRoleModel = mongoose_1.default.model('user-role-temp', userTempRoleModelSchema);
