import mongoose from "mongoose";


const SessionSchema = new mongoose.Schema({
   start:{
    type:mongoose.SchemaTypes.String
   },
   end:{
    type:mongoose.SchemaTypes.String
   } ,
   durationOfCall:{
    type:mongoose.SchemaTypes.String
   }
})

const  CallModelSchema = new mongoose.Schema({
    session:{
        type:SessionSchema
    },

    userCalling:{
        type:mongoose.SchemaTypes.ObjectId
    },
    userToCall:{
        type:mongoose.SchemaTypes.ObjectId
    }
})