"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.passportSetup = void 0;
const passport_1 = require("passport");
const passport_google_oauth20_1 = require("passport-google-oauth20");
console.log(process.env.base_callback_url);
let passport = new passport_1.Passport().use(new passport_google_oauth20_1.Strategy({
    clientID: process.env.client_id,
    clientSecret: process.env.client_secret,
    callbackURL: `${process.env.base_callback_url}auth/google/callback`
}, (refreshTokenToken, accessToken, profile, cb) => {
    return cb(null, profile);
}));
passport.serializeUser((user, cb) => {
    cb(null, user);
});
passport.deserializeUser((user, cb) => {
    cb(null, user);
});
exports.passportSetup = passport;
