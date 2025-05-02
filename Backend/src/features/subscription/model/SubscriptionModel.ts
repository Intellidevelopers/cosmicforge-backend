import mongoose from "mongoose";

const SubscriptionSchema = new mongoose.Schema({

    userId:{
        type:mongoose.SchemaTypes.ObjectId
    },
    planName:{
       type:mongoose.SchemaTypes.String,
        enum:['Free','Basic','Professional','Premium'],
        default:'Free'
    },

    paymentHistory:[{
        subscriptionPlan:{
            type:mongoose.SchemaTypes.String,
            enum:['Basic','Professional','Premium']
        },

        date:{
            type:mongoose.SchemaTypes.String,
            
        },
        paymentReferenceId:{
            type:mongoose.SchemaTypes.String,
         
        },
       
    }]



})

export default  mongoose.model('subscription',SubscriptionSchema)