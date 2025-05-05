import mongoose from "mongoose";


const patientVitalSignsSchema = new mongoose.Schema({
  
     bodyTemperature:{
        type:mongoose.SchemaTypes.String
     },
     bloodPressure:{
        type:mongoose.SchemaTypes.String
     },
     oxygenSaturation:{
        type:mongoose.SchemaTypes.String
     },
     weight:{
        type:mongoose.SchemaTypes.String
     },
     height:{
        type:mongoose.SchemaTypes.String
     },
     gender:{
        type:mongoose.SchemaTypes.String ,
        enum:['male','female']
    },
    dateOfBirth:{
        type:mongoose.SchemaTypes.String ,  
    },

})


 const patientProfileSchema = new mongoose.Schema({
      userId:{
         type:mongoose.SchemaTypes.ObjectId,
         ref:'users'
     },
     profileType:{
        type:mongoose.SchemaTypes.String,
        enum:['personal','family']
 
     },
     mobileNo:{
         type:mongoose.SchemaTypes.String
     },
     homeAddress:{
         type:mongoose.SchemaTypes.String
     },
     workAddress:{
         type:mongoose.SchemaTypes.String
     },
     profilePicture:{
         type:mongoose.SchemaTypes.String 
     },
    vitalSigns:{
        type:patientVitalSignsSchema
    }
 
 
 
 })
 
 
 const  PatientProfileModel =  mongoose.model('patientProfile',patientProfileSchema)
 
 export default  PatientProfileModel