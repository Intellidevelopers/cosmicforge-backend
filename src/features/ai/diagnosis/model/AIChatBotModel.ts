
import mongoose from "mongoose";


 const AIChatBotSchema = new mongoose.Schema({
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


 const AIChatbotModel = mongoose.model('ai-chatbot',AIChatBotSchema)


 export default AIChatbotModel