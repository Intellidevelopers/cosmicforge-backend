import mongoose from "mongoose";



const medicalPersonnelProfileSchema = new mongoose.Schema({
     userId:{
        type:mongoose.SchemaTypes.ObjectId,
        ref:'users'
    },
    mobileNo:{
        type:mongoose.SchemaTypes.String
    },
    professionalTitle:{
        type:mongoose.SchemaTypes.String
    },
    specializationTitle:{
        type:mongoose.SchemaTypes.String
    },
    currentClinic:{
        type:mongoose.SchemaTypes.String
    },
    department:{
        type:mongoose.SchemaTypes.String 
    },

    location:{
        type:mongoose.SchemaTypes.String 
    },
    profilePicture:{
        type:mongoose.SchemaTypes.String 
    }



})


const  MedicalPersonnelProfileModel =  mongoose.model('medicalPersonnelProfile',medicalPersonnelProfileSchema)

export default  MedicalPersonnelProfileModel