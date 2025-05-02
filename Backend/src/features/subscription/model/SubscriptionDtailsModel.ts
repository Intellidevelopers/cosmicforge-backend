import mongoose from "mongoose";



const DoctorSubscriptionDetailsSchema = new mongoose.Schema({

    name:{
        type:mongoose.SchemaTypes.String
    },

    message:{
        type:mongoose.SchemaTypes.String
    },
    price:{
        type:mongoose.SchemaTypes.String
    },
    duration:{
        type:mongoose.SchemaTypes.String
    },
    commission:{
        type:mongoose.SchemaTypes.String
    },
    offers:[{
       type:mongoose.SchemaTypes.String
    }]

})


const SubscriptionDtailsSchema = new mongoose.Schema({

    patient:{},

    doctor:{
        type:[DoctorSubscriptionDetailsSchema]
    }


    
})


export default mongoose.model('subscriptionModelDetails',SubscriptionDtailsSchema)