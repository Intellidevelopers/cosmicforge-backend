// const adminRoute = require('./src/features/adminAuth/routes/adminAuthRoute');


"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const app = (0, express_1.default)();


// app.use("/api/auth/admin", adminRoute);
app.listen(3010, () => {
    console.log('on port 3010');
});
