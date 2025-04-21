import mongoose from "mongoose";



const SessionSchema = new  mongoose.Schema({

    sessionDate:{
        type:mongoose.SchemaTypes.Date
    },
    doctorID:{
        type:mongoose.SchemaTypes.ObjectId
    },
    patientID:{
        type:mongoose.SchemaTypes.ObjectId
    }


})



const sessionModel = mongoose.model('session',SessionSchema)

export default sessionModel