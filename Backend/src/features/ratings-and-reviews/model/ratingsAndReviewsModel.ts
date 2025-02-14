import mongoose from "mongoose";


const RatingsAndReviewsSchema =  new mongoose.Schema({

     doctorReviewed:{
        type:mongoose.SchemaTypes.ObjectId,
        ref:'users'
     },

     patientReviewing:{
        type:mongoose.SchemaTypes.ObjectId,
        ref:'users'
     },
    patientProfile:{
        type:mongoose.SchemaTypes.String,  
    },
    patienFullName:{
        type:mongoose.SchemaTypes.String,  
    },
    rating:{
        type:mongoose.SchemaTypes.Number,
        min:[0,'ratings can not be lesser than 0'],
        max:[5,'ratings can not be greater than 5'],
        required:[true,'rating is needed.']
    },
    rewiew:{
        type:mongoose.SchemaTypes.String,  
    },
    createdAt:{
        type:mongoose.SchemaTypes.Date,
        default:Date.now()
    }
})


export const RatingsAndReviewsModel = mongoose.model('ratings-and-reviews',RatingsAndReviewsSchema)