import  Socket  from "socket.io";
import { AuthMiddlewareProps } from "../../../middleware/userAuthenticationMiddleware";
import { TypedSocket } from "../../../util/interface/TypedSocket";
import newUserModel from "../../newUser/model/newUserModel";
import diagnosisController from "./diagnosisController";
import AIDiagnosisModel from "./model/AIDiagnosisModel";


  

export default async (socketIO:Socket.Server,socket:TypedSocket<AuthMiddlewareProps>) => {
     const  userDiagnosisChat = await AIDiagnosisModel.findOne({userID:socket.user?._id})
   if(userDiagnosisChat){
   
    socket.emit('all-diagnosis',userDiagnosisChat)
   }
     socket.on('perform-diagnosis',(data)=>{
           runDiagnosis(socketIO,socket,data)
     })
}



const runDiagnosis = async (socketIO:Socket.Server,socket:TypedSocket<AuthMiddlewareProps>,data:any) =>{
   
    const symptoms = data
 
    try {
        const user = socket.user!!
    
        const isUserValid = await newUserModel.findOne({_id:user._id})

        if(isUserValid && symptoms){

            let userChat = await AIDiagnosisModel.findOne({userID:user._id})
           

           const result =  await diagnosisController(symptoms)


           console.log(result)

           if(!result){
            socket.emit('diagnosis-failed',"something went wrong try again.")
            return
           }

 

         if(userChat){
            const messages = userChat.messages
            messages.push({sender:'user',message:symptoms,timeStamp:Date.now()})
            messages.push({sender:'bot',message:result,timeStamp:Date.now()})
            await userChat.updateOne({messages})
            userChat = await AIDiagnosisModel.findOne({userID:user._id})
            socket.emit('diagnosis',userChat)
         }else{

              
            
                const message =  await new AIDiagnosisModel({
                     userID:user._id,
                     messages:[{sender:'user',message:symptoms,timeStamp:Date.now()},{sender:'bot',message:result,timeStamp:Date.now()}]
                 }).save()
 
                 socket.emit('diagnosis',message)

                 return
             
         }

          

        }

    } catch (error) {
        socket.emit('diagnosis-failed','Something went wrong try again.')
    }
}