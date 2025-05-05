 import {Passport} from 'passport'

 import {Strategy} from 'passport-google-oauth20'

 

console.log(process.env.base_callback_url)

let passport = new Passport().use(new Strategy({
    clientID:process.env.client_id!!,
    clientSecret:process.env.client_secret!!,
    callbackURL:`${process.env.base_callback_url!!}auth/google/callback`
 },(refreshTokenToken,accessToken,profile,cb)=>{



    return cb(null,profile)
 }))

 passport.serializeUser((user,cb)=>{
  cb(null,user!!)
 })

passport.deserializeUser((user,cb)=>{
    cb(null,user!!)
 })






 export const passportSetup = passport