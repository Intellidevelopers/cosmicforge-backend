import SERVER_STATUS from "../../../util/interface/CODE";
import { ResponseBodyProps } from "../../../util/interface/ResponseBodyProps";
import TypedRequest from "../../../util/interface/TypedRequest";
import TypedResponse from "../../../util/interface/TypedResponse";
import { USER_ROLES } from "../../../util/interface/UserRole";
import BookAppointmentModel from "../../appointment/model/bookAppointmentModel";
import SubscriptionDtailsModel from "../../subscription/model/SubscriptionDtailsModel";
import SubscriptionModel from "../../subscription/model/SubscriptionModel";
import WalletModel from "../model/walletModel";




export const paystackWebHookEventListener =  async (req:TypedRequest<{
   event:string,
   data:{
    reference:string,
    channel:string,
    'paid_at':string,
    'ip_address':string,
    currency:string,
    amount:number
    /** 
     * data for transfer
     */
    transfer_code:string,
      details: {
          "account_number": string,
          "account_name": string,
        }

      }
   
}>,res:TypedResponse<{}>) =>{

    res.sendStatus(200)

    let ipAddress = ['197.210.85.162']

    const body = req.body

     console.log(body)

    const {event,data} = body

    

     setTimeout(async()=>{


      try {


      const isValidIp = ipAddress.find(ip=>{
        return ip  === data.ip_address
    })

    if(event && event === "charge.success"){

    

      const appointment = await BookAppointmentModel.findOne({
        "payment.paymentReference":data.reference
      })

     

     if(appointment){

      //check subscriptionPlan and deduct money
      const plan = await SubscriptionModel.findOne({
        userId:appointment.medicalPersonelID
      })

      
      const commissionDetails =  await SubscriptionDtailsModel.find()
      
      //check if wallet already created 
      const wallet = await WalletModel.findOne({
        userId:appointment.medicalPersonelID
      })

      if(!wallet){

        let amountAfterCommission = 0

        if(commissionDetails){

          const commissionData = commissionDetails[0].doctor.find((data)=>{
             return data.name === plan?.planName
          })


          amountAfterCommission = data.amount - (data.amount * Number(commissionData?.commission?.replace('/,[a-z,A-Z]/g',''))/100)


        }
        
        const newWallet = new WalletModel({
          userId:appointment.medicalPersonelID,
          amount:amountAfterCommission ?? data.amount,
          currency:data.currency,
          histories:[{
            paymentMadeBy:appointment.patientID,
          paymentSentTo:appointment.medicalPersonelID,
          paymentDate:data.paid_at,
          paymentReferenceId:data.reference,
          paymentStatus:'success',
          paymentChannel:data.channel
          }]
        })

   
        
   await BookAppointmentModel.findOneAndUpdate({
      "payment.paymentReference":data.reference
    },{
      paymentStatus:'success'
    })

    console.log(await BookAppointmentModel.findOne({
      "payment.paymentReference":data.reference
    }))
      
    
       
      

       

        await newWallet.save()
      }else{

          //check subscriptionPlan and deduct money
      const plan = await SubscriptionModel.findOne({
        userId:appointment.medicalPersonelID
      })

      
      const commissionDetails =  await SubscriptionDtailsModel.find()

      let amountAfterCommission = 0

      if(commissionDetails){

        const commissionData = commissionDetails[0].doctor.find((data)=>{
           return data.name === plan?.planName
        })


        amountAfterCommission = data.amount - (data.amount * Number(commissionData?.commission?.replace('/,[a-z,A-Z]/g',''))/100)


      }
        
        const topUpBalance = wallet.amount + (amountAfterCommission ?? data.amount)

        const updatehistories = wallet.histories ?? []

        updatehistories.push({
          paymentMadeBy:appointment.patientID,
        paymentSentTo:appointment.medicalPersonelID,
        paymentDate:data.paid_at,
        paymentReferenceId:data.reference,
        paymentStatus:'success',
        paymentChannel:data.channel
        })


        
           

         await BookAppointmentModel.findOneAndUpdate({
          "payment.paymentReference":data.reference
        },{
         paymentStatus:'success'
        })
    
        console.log(await BookAppointmentModel.findOne({
          "payment.paymentReference":data.reference
        }))

        await wallet.updateOne({

          amount:topUpBalance,
          histories:updatehistories

        })

         
      }
        
     }else{
      

      const subscription =  await SubscriptionModel.findOne({paymentHistory:{
        $elemMatch:{
         paymentReferenceId:data.reference
        }
      }})



       if(subscription){

         const  planData =  subscription.paymentHistory.find((history)=>{
           return history.paymentReferenceId === data.reference
         })

        await subscription.updateOne({
          planName:planData?.subscriptionPlan
         })

       }
      

     }


    }



    if(event && event === "transfer.success"){

      const userWallet =  await WalletModel.findOne({
          withdrawalHistories: {
            $elemMatch: {
            withdrawalReferenceId:data.reference,
            
            }
          }
        })
      
       
  console.log(data.reference)
     
  
        if(userWallet){
  
       
  
          const oldBalance = userWallet.amount
          const newBallance = oldBalance - data.amount
  
         const updateHistories =  userWallet.withdrawalHistories.map((history)=>{
  
            if(history.withdrawalReferenceId === data.reference){
              
                return {
                  ...history.toObject(),
                  transferStatus:'success'
                }
              }else{
                return history
              }
          })

          console.log('updatedHistory')
          console.log(updateHistories)
  
          await  userWallet.updateOne({
            amount:newBallance,
            withdrawalHistories:updateHistories
  
          })
        }
  
      }
  
  
  
      if(event && event === "transfer.failed"){

        console.log('called.......')
        
        const userWallet = await WalletModel.findOne({
          withdrawalHistories:{
            $elemMatch:{
              withdrawalReferenceId:data.reference,
              transferReferenceID:data.transfer_code
            }
          }
        })
  
        if(userWallet){
  
         
  
         const updateHistories =  userWallet.withdrawalHistories.map((history)=>{
  
            if(history.withdrawalReferenceId=== data.reference && 
              history.transferReferenceID === data.transfer_code){
  
                return {
                  ...history,
                  transferStatus:'failed'
                }
              }else{
                return history
              }
          })
  
          await  userWallet.updateOne({
           
            withdrawalHistories:updateHistories
  
          })
        }
  
      }

    



        
      } catch (error) {
         console.log(error)
      }



     },30000)



     

}



export const getWalletById = async (req:TypedRequest<{}>,res:TypedResponse<ResponseBodyProps>) =>{

  try {
 
     const user = req.user
      if( user && user.role !== USER_ROLES.DOCTOR){
 
         res.status(SERVER_STATUS.UNAUTHORIZED).json({
             title:"Wallet Details",
             successful:false,
             status:SERVER_STATUS.UNAUTHORIZED,
             message:'you are not authorized'
         })
 
         return
       
      }
 
 
 
      const wallet = await WalletModel.findOne({
         userId:user?._id
      })
      
 
      res.status(SERVER_STATUS.SUCCESS).json({
         title:"Wallet Details",
         successful:false,
         status:SERVER_STATUS.SUCCESS,
         message:'successfully fetched wallet.',
         data:wallet
     })
 
 
      
     
  } catch (error:any) {
     
     res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
         title:"Wallet Details",
         successful:false,
         status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
         message:'internal server error',
         error:error.message
     })
 
 
  }
 
 
 }