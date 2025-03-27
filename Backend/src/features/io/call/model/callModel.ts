import mongoose from "mongoose";


const SessionSchema = new mongoose.Schema({
   start:{
    type:mongoose.SchemaTypes.Date
   },
   end:{
    type:mongoose.SchemaTypes.Date
   } ,
   durationOfCall:{
    type:mongoose.SchemaTypes.String
   }
})

const  CallModelSchema = new mongoose.Schema({
    session:{
        type:SessionSchema
    },

    peers:[{
            type:{
                type:mongoose.SchemaTypes.ObjectId
            }
        }]

   
})

const CallModel = mongoose.model('call_session',CallModelSchema)


export default  CallModel