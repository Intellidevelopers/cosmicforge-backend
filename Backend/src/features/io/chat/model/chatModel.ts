import mongoose from "mongoose";

 
const userDetailsSchema = new mongoose.Schema({

     userId:{
        type:mongoose.SchemaTypes.String
     },
     userName:{
        type:mongoose.SchemaTypes.String
     },
     userProfile:{
        type:{}
     }

})



const chatSchema = new mongoose.Schema({
    chatID:{
        type:mongoose.SchemaTypes.String
    },
    userOneID:{
       type:userDetailsSchema
    },
    userTwoID:{
        type:userDetailsSchema
    },

    messages:[{
        messageType:{
            type:mongoose.SchemaTypes.String,
            enum:['text','file']
        },

        message:{
            type:mongoose.SchemaTypes.String
        },

      timeStamp:{
            type:mongoose.SchemaTypes.String
        },
        sender:{
            type:mongoose.SchemaTypes.ObjectId,
                 ref:'users'
        },
       receiver:{
            type:mongoose.SchemaTypes.ObjectId,
                 ref:'users'
        },

        
    }]
})


const  ChatModel = mongoose.model('chats',chatSchema)

export default ChatModel