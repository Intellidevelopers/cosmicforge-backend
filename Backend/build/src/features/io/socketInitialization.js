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
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const newUserModel_1 = __importDefault(require("../newUser/model/newUserModel"));
const UserConnections_1 = __importDefault(require("./model/UserConnections"));
exports.default = (socketIO) => {
    socketIO.use((socket, next) => __awaiter(void 0, void 0, void 0, function* () {
        var _a, _b;
        const authorization = socket.handshake.headers.authorization || socket.handshake.auth.token;
        if (!authorization) {
            next(Error('you are not authorized to continue.'));
            return;
        }
        try {
            const token = (_a = authorization.split(" ")[1]) !== null && _a !== void 0 ? _a : authorization;
            const validatedToken = jsonwebtoken_1.default.verify(token, (_b = process.env) === null || _b === void 0 ? void 0 : _b.JWT_SECRET);
            const user = yield newUserModel_1.default.findOne({ _id: validatedToken._id });
            if (!user) {
                next(Error('you are not authorized to continue.'));
                return;
            }
            socket.user = validatedToken;
            next();
        }
        catch (error) {
            next(Error(error.message));
        }
    })).on('connection', (socket) => __awaiter(void 0, void 0, void 0, function* () {
        var _a, _b, _c;
        let userConnection = yield UserConnections_1.default.findOne({ userId: (_a = socket.user) === null || _a === void 0 ? void 0 : _a._id });
        if (!userConnection) {
            userConnection = new UserConnections_1.default({
                userId: (_b = socket.user) === null || _b === void 0 ? void 0 : _b._id,
                connectionId: socket.id
            });
            yield userConnection.save();
            socket.emit('message', JSON.stringify(userConnection));
            return;
        }
        yield userConnection.updateOne({
            connectionId: socket.id,
        }, {
            new: true,
            returnDocument: 'after'
        });
        userConnection = yield UserConnections_1.default.findOne({ userId: (_c = socket.user) === null || _c === void 0 ? void 0 : _c._id });
        console.log('updating....');
        console.log(socket.id);
        socket.emit('message', JSON.stringify(userConnection));
    }));
};
