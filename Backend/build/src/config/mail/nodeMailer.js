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
const nodemailer_1 = __importDefault(require("nodemailer"));
const path_1 = __importDefault(require("path"));
const ejs_1 = __importDefault(require("ejs"));
const nodeMail = nodemailer_1.default.createTransport({
    service: 'gmail',
    auth: {
        user: "adeagbojosiah1@gmail.com",
        pass: "bvvmpoeglluldhwj"
    },
});
const sendMail = (data) => __awaiter(void 0, void 0, void 0, function* () {
    const emailTemplatePath = path_1.default.join(path_1.default.resolve(__dirname, '../../'), 'views', data.template);
    const htmltoSend = yield ejs_1.default.renderFile(emailTemplatePath, {
        data: data.emailData
    });
    return nodeMail.sendMail({
        sender: "adeagbojosiah1@gmail.com",
        to: data.receiver,
        subject: data.subject,
        html: htmltoSend
    });
});
exports.default = sendMail;
