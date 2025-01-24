import mongoose from "mongoose";

const  otpVerificationSchema =  new mongoose.Schema({
    userDetails:{
        email:{
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
        
    
})


export default  mongoose.model('otp',otpVerificationSchema)