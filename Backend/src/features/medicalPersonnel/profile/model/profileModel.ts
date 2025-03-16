import mongoose from "mongoose";

enum workingDays  {
    'mondays-only'='mondays-only',
    'tuesdays-only'='tuesdays-only',
    'wednessdays-only'='wednessdays-only',
    'thursdays-only'='thursdays-only',
    'fridays-only'='fridays-only',
    'saturdays-only'='saturdays-only',
    'monday-tuesday'='monday-tuesday',
    'monday-wednessday'='monday-wednessday',
    'monday-thurdays'='monday-thursday',
    'monday-friday'='monday-friday',
    'monday-saturday'='monday-saturday',
    'tuesday-wednessday'='tuesday-wednessday',
    'tuesday-thursday'='tuesday-thursday',
    'tuesday-friday'='tuesday-friday',
    'tuesday-saturday'='tuesday-saturday',
    'wednessday-thursday'='wednessday-thursday',
    'wedness-friday'='wednessday-friday',
    'wednessday-saturday'='wednessday-saturday',
    'thursday-friday'='thursday-friday',
    'thursday-saturday'='thursday-saturday',
    'friday-saturday'='friday-saturday',
   

}

enum  department{
      "General Medicine",
     "Emergency Medicine",
        "Cardiology",
        "Pediatrics",
         "Nuerology",
         "OB-GYN",
         "Dentistry",
         "Otolarygngology",
          "Pschiatry",
         "Radiology",
         "Dermatology",
           "Pathology",
         "Oncology",
          "Ophthalmology",
         "Urology",
         "Physical Therapy",
          "Rheumatology",
           "Grastro Enterology",
          "Orthopedics",
          "Neonatology",
          "Nephrology",
          "Pulmonology",
          "Geonomics",
           "Hematology",
      
      
}

const workingHourSchema =  new mongoose.Schema({
    workingDays:{type:mongoose.SchemaTypes.String,
        enum:workingDays
    },
    workingTime:{type:mongoose.SchemaTypes.String}
})

const experienceSchema = new mongoose.Schema({
    hospitalName:{
        type:mongoose.SchemaTypes.String
    },
    specializationOrDepartment:{
        type:mongoose.SchemaTypes.String 
    },
    noOfPatientTreated:{
        type:mongoose.SchemaTypes.String 
    },
    date:{
        type:mongoose.SchemaTypes.String 
    },

})

const mapLocationSchema = new mongoose.Schema({
    latitude:{type:mongoose.SchemaTypes.String},
    longitude:{type:mongoose.SchemaTypes.String}
})

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
    },
     mapLocation:mapLocationSchema,
     experience:{
        type:experienceSchema
     },
     bio:{
        type:mongoose.SchemaTypes.String 
     },
     workTime:workingHourSchema,

     pricing:{
        type:mongoose.SchemaTypes.String,
        
     },
     earlistAvailability:{
        type:mongoose.SchemaTypes.Date
     }
     
     



})


const  MedicalPersonnelProfileModel =  mongoose.model('medicalPersonnelProfile',medicalPersonnelProfileSchema)

export default  MedicalPersonnelProfileModel