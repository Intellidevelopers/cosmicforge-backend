import mongoose from "mongoose";

 const PaymentHistorySchema = new mongoose.Schema({

    paymentType:{
        type:mongoose.Schema.Types.String, 
        enum:['consultation-fee'],
        default:'consultation-fee'
    },
    paymentMadeBy:{
        type:mongoose.Schema.Types.ObjectId, 
       
    },
    paymentSentTo:{
        type:mongoose.Schema.Types.ObjectId, 
       
    },
    paymentDate:{
        type:mongoose.Schema.Types.Date, 
    
    },
    paymentReferenceId:{
        type:mongoose.Schema.Types.String, 
        
    },
    paymentStatus:{
        type:mongoose.Schema.Types.String, 
        enum:['pending','success','failed']
    },
    paymentChannel:{
        type:mongoose.Schema.Types.String, 
       
    },
 })


const walletSchema =  new mongoose.Schema({

    userId:{
        type:mongoose.Schema.ObjectId,
        ref:'users'
    },
    amount:{
        type:mongoose.Schema.Types.Number,
        default:0
    },
    currency:{
        type:mongoose.Schema.Types.String, 
        enum:['NGN',"US-Dollar"]
    },
    histories:[
        {
         type:PaymentHistorySchema
        }
    ]
})


const WalletModel = mongoose.model('wallet',walletSchema)

export default WalletModel