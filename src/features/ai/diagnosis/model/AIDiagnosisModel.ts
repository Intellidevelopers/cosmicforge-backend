
import mongoose from "mongoose";


 const AIDiagnosisSchema = new mongoose.Schema({
    userID:{
        type:mongoose.SchemaTypes.ObjectId,
        ref:""
    },
    messages:[{
        sender:{
            type:mongoose.SchemaTypes.String,
            enum:['bot','user']
        },
        message:{
            type:mongoose.SchemaTypes.String
        },
        timeStamp:{
            type:mongoose.SchemaTypes.Date
        }
    }]
 })


 const AIDiagnosisModel = mongoose.model('diagnosis',AIDiagnosisSchema)


 export default AIDiagnosisModel