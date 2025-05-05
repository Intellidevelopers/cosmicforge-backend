import  Socket  from "socket.io";
import { AuthMiddlewareProps } from "../../../middleware/userAuthenticationMiddleware";
import { TypedSocket } from "../../../util/interface/TypedSocket";
import newUserModel from "../../newUser/model/newUserModel";
import diagnosisController from "./diagnosisController";
import AIDiagnosisModel from "./model/AIDiagnosisModel";
import OpenAI from "openai";
import AIChatbotModel from "./model/AIChatBotModel";


  

export default async (socketIO:Socket.Server,socket:TypedSocket<AuthMiddlewareProps>) => {
     const  userDiagnosisChat = await AIDiagnosisModel.findOne({userID:socket.user?._id})
     const  userChatBot = await AIChatbotModel.findOne({userID:socket.user?._id})

   if(userDiagnosisChat){
   
    socket.emit('all-diagnosis',userDiagnosisChat)
   }

   if(userChatBot){
   
    socket.emit('all-chatBot',userChatBot)
   }


     socket.on('perform-diagnosis',(data)=>{
           runDiagnosis(socketIO,socket,data)
     })

     socket.on('ai-chat',(data)=>{
        aiChatBot(socketIO,socket,data)
  })

     
}



const runDiagnosis = async (socketIO:Socket.Server,socket:TypedSocket<AuthMiddlewareProps>,data:any) =>{
   
    const symptoms = data
 console.log(symptoms)
    try {
        const user = socket.user!!
    
        const isUserValid = await newUserModel.findOne({_id:user._id})

        if(isUserValid && symptoms){

            let userChat = await AIDiagnosisModel.findOne({userID:user._id})
           


            const openAI = new OpenAI({
                apiKey:'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'
            })

           let result = await openAI.responses.create({
            model:"gpt-4o-mini",
            instructions:"You are a medical expert only answer questions related to health and give suggested diagnosis through signs and symptoms provided and add some recommended drugs and home remedies that can be taken to subdue such sign and symptom if severe, always tell then to book appointment with a doctor at cosmicforge to to be addressed. Please give suggested diagnosis and never say you are not a doctor. Remove astericks and other irrelevant signs and symbols. At the end alway tell them to book appointment with a doctor at cosmicforge after you provide the suggestions. If lifestyle modication will be required please provide as well as excercise needed, foods,fruits needed to improve the health.Alway remove signs like ** in the output text.",
            input:symptoms,
            temperature:0.5
            
          })

          // const result =  await diagnosisController(symptoms)


           console.log(result.output_text)

          

           if(!result.output_text){
            socket.emit('diagnosis-failed',"something went wrong try again.")
            return
           }

 

         if(userChat){
            const messages = userChat.messages
            messages.push({sender:'user',message:symptoms,timeStamp:Date.now()})
            messages.push({sender:'bot',message:result.output_text,timeStamp:Date.now()})
            await userChat.updateOne({messages})
            userChat = await AIDiagnosisModel.findOne({userID:user._id})
            socket.emit('diagnosis',userChat)
         }else{

              
            
                const message =  await new AIDiagnosisModel({
                     userID:user._id,
                     messages:[{sender:'user',message:symptoms,timeStamp:Date.now()},{sender:'bot',message:result.output_text,timeStamp:Date.now()}]
                 }).save()
 
                 socket.emit('diagnosis',message)

                 return
             
         }

          

        }

    } catch (error) {
        socket.emit('diagnosis-failed','Something went wrong try again.')
    }
}




const aiChatBot = async (socketIO:Socket.Server,socket:TypedSocket<AuthMiddlewareProps>,data:any) => {

    const symptoms = data
 
    try {
        const user = socket.user!!
    
        const isUserValid = await newUserModel.findOne({_id:user._id})

        if(isUserValid && symptoms){

            let userChat = await AIChatbotModel.findOne({userID:user._id})
           


            const openAI = new OpenAI({
                apiKey:'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'
            })
        
           let result = await openAI.responses.create({
            model:"gpt-4o-mini",
            instructions:"You are a medical AI chat bot. Provide only information related to medical profession. Chat friendly with user as if you a real doctor reviewing a patient. End all conversation with booking an appointment with a doctor on cosmicforge for more infomation.Always remove signs like  ** in the output text. Please remove all astericks",
            input:data,
            temperature:0.5
            
          })
            

          // const result =  await diagnosisController(symptoms)


           console.log(result.output_text)

          

           if(!result.output_text){
            socket.emit('aiChat-failed',"something went wrong try again.")
            return
           }

 

         if(userChat){
            const messages = userChat.messages
            messages.push({sender:'user',message:symptoms,timeStamp:Date.now()})
            messages.push({sender:'bot',message:result.output_text,timeStamp:Date.now()})
            await userChat.updateOne({messages})
            userChat = await AIChatbotModel.findOne({userID:user._id})
            socket.emit('ai-chatbot',userChat)
         }else{

              
            
                const message =  await new AIChatbotModel({
                     userID:user._id,
                     messages:[{sender:'user',message:symptoms,timeStamp:Date.now()},{sender:'bot',message:result.output_text,timeStamp:Date.now()}]
                 }).save()
 
                 socket.emit('ai-chatbot',message)

                 return
             
         }

          

        }

    } catch (error) {
        socket.emit('diagnosis-failed','Something went wrong try again.')
    }



}