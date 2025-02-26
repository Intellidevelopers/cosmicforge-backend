"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const mongoose_1 = __importDefault(require("mongoose"));
const UserConnectionsSchema = new mongoose_1.default.Schema({
    userId: {
        type: mongoose_1.default.SchemaTypes.String
    },
    connectionId: {
        type: mongoose_1.default.SchemaTypes.String
    }
});
const UserConnectionsModel = mongoose_1.default.model('user-connections', UserConnectionsSchema);
exports.default = UserConnectionsModel;
