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
const express_1 = __importDefault(require("express"));
const loginRouter_1 = __importDefault(require("../features/login/routes/loginRouter"));
const newUserRoute_1 = __importDefault(require("../features/newUser/routes/newUserRoute"));
const profileRoute_1 = __importDefault(require("../features/medicalPersonnel/profile/routes/profileRoute"));
const patientProfileController_1 = __importDefault(require("../features/patient/profile/routes/patientProfileController"));
const ratingsAndReviewsModel_1 = __importDefault(require("../features/ratings-and-reviews/routes/ratingsAndReviewsModel"));
const bookAppointmentRouter_1 = __importDefault(require("../features/appointment/routes/bookAppointmentRouter"));
const express_session_1 = __importDefault(require("express-session"));
const signup_signin_1 = require("../authenticateWithProviders/google/signup_signin");
const signup_signinController_1 = require("../authenticateWithProviders/google/signup_signinController");
const CODE_1 = __importDefault(require("../util/interface/CODE"));
const tempRoleModel_1 = require("../authenticateWithProviders/model/tempRoleModel");
const mainRouter = express_1.default.Router();
mainRouter.use((0, express_session_1.default)({
    secret: 'cosmicforge',
    resave: true,
    saveUninitialized: true,
    cookie: {
        secure: false
    },
    store: new express_session_1.default.MemoryStore()
}));
mainRouter.use('/user', newUserRoute_1.default);
mainRouter.use('/user', loginRouter_1.default);
mainRouter.use('/user/medics', profileRoute_1.default);
mainRouter.use('/user/patient', patientProfileController_1.default);
mainRouter.use('/user/patient', ratingsAndReviewsModel_1.default);
mainRouter.use('/user', bookAppointmentRouter_1.default);
mainRouter.use(signup_signin_1.passportSetup.initialize());
mainRouter.use(signup_signin_1.passportSetup.session());
mainRouter.get('/auth/google', signup_signin_1.passportSetup.authenticate('google', {
    scope: ['profile', 'email'],
}));
mainRouter.post('/auth/google/userRole', (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { userRole } = req.body;
    yield tempRoleModel_1.userTempRoleModel.deleteMany();
    yield new tempRoleModel_1.userTempRoleModel({
        userRole,
    }).save();
    res.sendStatus(CODE_1.default.SUCCESS);
}));
mainRouter.get('/auth/google/callback', signup_signin_1.passportSetup.authenticate('google', {}), signup_signinController_1.googleSignUpSignInAuthcontroller);
exports.default = mainRouter;
