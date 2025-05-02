import SERVER_STATUS from "../../../util/interface/CODE";
import { ResponseBodyProps } from "../../../util/interface/ResponseBodyProps";
import TypedRequest from "../../../util/interface/TypedRequest";
import TypedResponse from "../../../util/interface/TypedResponse";
import { USER_ROLES } from "../../../util/interface/UserRole";
import SubscriptionDtailsModel from "../model/SubscriptionDtailsModel";
import SubscriptionModel from "../model/SubscriptionModel";


 export const getSubscription = async (req:TypedRequest<{}>,res:TypedResponse<ResponseBodyProps>) =>{
 
     const user = req.user

     const userSubscription = await  SubscriptionModel.findOne({
        userId:user?._id
     })

      const generalSubscriptionDetails = await SubscriptionDtailsModel.find()
    
     if(generalSubscriptionDetails && generalSubscriptionDetails.length>0 ){

       if(user?.role === USER_ROLES.DOCTOR){
      
       res.status(SERVER_STATUS.SUCCESS).json({
        title:"Subcription Mssage",
        status:SERVER_STATUS.SUCCESS,
        successful:true,
        message:"Successfully fetched.",
        data:{
            ...userSubscription?.toObject(),
            generalSubscriptionDetails:generalSubscriptionDetails[0].doctor
        }
       })

       }

     }


    
}



export const updateSubscription = async (req:TypedRequest<{referenceID:string,plan:string}>,res:TypedResponse<ResponseBodyProps>) =>{
 
    const user = req.user

   
try {

    const {referenceID,plan} = req.body

  console.log(plan)
    if(!referenceID || !plan){
        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Subcription Mssage",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"referenceID and plan fields are required to continue.",
           
           })

           return
        
    }


    const userSubscription = await  SubscriptionModel.findOne({
       userId:user?._id
    })



    if(userSubscription){

  let updatedHistory = userSubscription.paymentHistory

  updatedHistory.push({
    paymentReferenceId:referenceID,
    subscriptionPlan:plan,
    date:Date.now().toLocaleString()
    
  })

        await userSubscription.updateOne({paymentHistory:updatedHistory})

        const updatedSubscription = await  SubscriptionModel.findOne({
            userId:user?._id
         })

        res.status(SERVER_STATUS.SUCCESS).json({
            title:"Subcription Message",
            status:SERVER_STATUS.SUCCESS,
            successful:true,
            message:"Successfull.",
            data:updatedSubscription
           
           })
    }

    
   
    
} catch (error:any) {
 res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
        title:"Subcription Mssage",
        status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
        successful:false,
        message:"Internal server error.",
        error:error.message
       
       })

}

 
   


   
}

