import mongoose from "mongoose";

const  resetPasswordOtpVerificationSchema =  new mongoose.Schema({
    userDetails:{
        email:{
            type:mongoose.SchemaTypes.String
        },
      fullName:{
            type:mongoose.SchemaTypes.String
        }
    },
        otpCode:{
            type:mongoose.SchemaTypes.Number,
            min:[6,"Otp code should not exceed 6 digit"]
        },
        expiringTime:{
            type:Date
        },
        isOtpValidated:{
            type:mongoose.SchemaTypes.Boolean,
            default:false
        }
        
    
},{expires:'24h'})


export default  mongoose.model('resetPassword',resetPasswordOtpVerificationSchema)