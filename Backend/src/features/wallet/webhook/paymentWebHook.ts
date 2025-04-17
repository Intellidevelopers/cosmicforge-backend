import TypedRequest from "../../../util/interface/TypedRequest";
import TypedResponse from "../../../util/interface/TypedResponse";
import BookAppointmentModel from "../../appointment/model/bookAppointmentModel";
import WalletModel from "../model/walletModel";




export const confirmPaymentAndSettleAccount =  async (req:TypedRequest<{
   event:string,
   data:{
    reference:string,
    channel:string,
    'paid_at':string,
    'ip_address':string,
    currency:string,
    amount:number
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

      console.log(data.reference)

      const appointment = await BookAppointmentModel.findOne({
        "payment.paymentReference":data.reference
      })

     console.log(appointment)

     if(appointment){

      //check if wallet already created 
      const wallet = await WalletModel.findOne({
        userId:appointment.medicalPersonelID
      })

      if(!wallet){
        
        const newWallet = new WalletModel({
          userId:appointment.medicalPersonelID,
          amount:data.amount,
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

     const updatePayment = {
      ...appointment.payment,
      paymentStatus:'success'
     }
         await appointment.updateOne({

          payment:updatePayment
         })

      
    
       
      

       

        await newWallet.save()
      }else{
        
        const topUpBalance = wallet.amount + data.amount

        const updatehistories = wallet.histories ?? []

        updatehistories.push({
          paymentMadeBy:appointment.patientID,
        paymentSentTo:appointment.medicalPersonelID,
        paymentDate:data.paid_at,
        paymentReferenceId:data.reference,
        paymentStatus:'success',
        paymentChannel:data.channel
        })


        const updatePayment = {
          ...appointment.payment,
          paymentStatus:'success'
         }
             await appointment.updateOne({
    
              payment:updatePayment
             })

        await wallet.updateOne({

          amount:topUpBalance,
          histories:updatehistories

        })

         
      }
        
     }


    }
        
      } catch (error) {
         console.log(error)
      }



     },30000)

}