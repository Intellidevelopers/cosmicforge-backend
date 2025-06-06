import mongoose from "mongoose";
import { AuthMiddlewareProps } from "../../../../middleware/userAuthenticationMiddleware";
import { TypedSocket } from "../../../../util/interface/TypedSocket";
import Socket  from "socket.io";
import ChatModel from "../model/chatModel";
import newUserModel from "../../../newUser/model/newUserModel";
import UserConnectionsModel from "../../model/UserConnections";
import { USER_ROLES } from "../../../../util/interface/UserRole";
import PatientProfileModel from "../../../patient/profile/model/patientProfileModel";
import MedicalPersonnelProfileModel from "../../../medicalPersonnel/profile/model/profileModel";
import uploader from "../../../../config/cloudinary/cloudinary";

export const USER_CHAT = async (socketIO:Socket.Server,socket:TypedSocket<AuthMiddlewareProps>) =>{

    socket.on('send_message',(data:{
        senderId:string,
        receiverId:string,
        messageType:string,
        message:string,
        timeStamp:string
    })=>{
 
         sendMessage(socketIO,socket,data)
    })


}



const sendMessage = async (socketIO:Socket.Server,socket:TypedSocket<AuthMiddlewareProps>,data:{
    senderId:string,
    receiverId:string,
    messageType:string,
    message:string,
    timeStamp:string
}) =>{


    try {

        if(!mongoose.Types.ObjectId.isValid(data.senderId) || !mongoose.Types.ObjectId.isValid(data.receiverId)){
              socket.emit('send_message_failed',{
                message:'invalid id provided.'
              })

              return
        }

        const  isSenderValid = await newUserModel.findOne({
            _id:data.senderId
        })
        const  isReceiverValid = await newUserModel.findOne({
            _id:data.receiverId
        })

        if(!isSenderValid || !isReceiverValid){
            socket.emit('send_message_failed',{
                message:'invalid id provided.'
              })

              return 
        }

        const chats = await ChatModel.findOne({
            $or:[
                {
                chatID:data.senderId.concat(data.receiverId)
                },
                {
                 chatID:data.receiverId.concat(data.senderId)
                }
            ]
        }) 

        if(chats){

            const oldChats = chats.messages
            
            if(oldChats && data.messageType === "text"){
               let updateChat = oldChats
               updateChat.push({messageType:data.messageType,message:data.message,
                    timeStamp:data.timeStamp,
                    sender:data.senderId,
                    receiver:data.receiverId
                })

                await chats.updateOne({
                    messages:updateChat
                })


                

                const newChats =   await ChatModel.findOne({
            $or:[
                {
                chatID:data.senderId.concat(data.receiverId)
                },
                {
                 chatID:data.receiverId.concat(data.senderId)
                }
            ]
        })

        

            const receiverSocket = await UserConnectionsModel.findOne({
                userId:data.receiverId
            })



             socket.emit('update_chat',newChats)
             
            socketIO.to(receiverSocket?.connectionId!!).emit('update_chat',newChats)

            
            return


            }


console.log(data.message)

            if(oldChats && data.messageType === "audio" && data.message){


                  const audioUrl =  await new   Promise<string | null>(async (resolve,reject)=>{

                      const regex = /^data:audio\/(wav);base64,/i;
                             
                                  if(!regex.test(data.message)){
                             
                                    socket.emit('send_message_failed',{
                                        message:'invalid id invalid audio format.'
                                      })

                                      return
                             
                                  }


                                uploader.upload(data.message,{
                                        resource_type:'video',
                                                       folder:data.senderId.concat('/messages/audio')
                                                    },(error,uploadedResult)=>{
                                                       
                                                       if(error){
                                                        console.log(uploadedResult)
                                                           reject(error.message)
                                                       }

                                                       console.log(uploadedResult)
                               
                                                       resolve(uploadedResult?.secure_url!!)
                                               
                                                     
                                                    })


                      
                  })


                  console.log(audioUrl)

                let updateChat = oldChats


                updateChat.push({
                    messageType:data.messageType,
                    message:audioUrl,
                     timeStamp:data.timeStamp,
                     sender:data.senderId,
                     receiver:data.receiverId
                 })
 
                 await chats.updateOne({
                     messages:updateChat
                 })
 
 
                 
 
                 const newChats =   await ChatModel.findOne({
             $or:[
                 {
                 chatID:data.senderId.concat(data.receiverId)
                 },
                 {
                  chatID:data.receiverId.concat(data.senderId)
                 }
             ]
         })
 
         
 
             const receiverSocket = await UserConnectionsModel.findOne({
                 userId:data.receiverId
             })
 
 
 
             // socket.emit('update_chat',newChats)
              
             socketIO.to(receiverSocket?.connectionId!!).emit('update_chat',newChats)
 
             
             return
 
 
             }






        }else{

            let receiverProfile:{} | null = {} 

            let senderProfile:{} | null = {} 



           if(isReceiverValid.role === USER_ROLES.CLIENT.toString()){

                receiverProfile = await  PatientProfileModel.findOne({
                userId:isReceiverValid._id
               })



           }else{


            receiverProfile = await  MedicalPersonnelProfileModel.findOne({
                userId:isReceiverValid._id
               })
           }



           if(isSenderValid.role === USER_ROLES.CLIENT.toString()){


            senderProfile = await  PatientProfileModel.findOne({
                userId:isSenderValid._id
               })

           }else{


            senderProfile = await  MedicalPersonnelProfileModel.findOne({
                userId:isSenderValid._id
               })

           }



           if(data.messageType === "audio" && data.message){

            const audioUrl =  await new   Promise<string | null>(async (resolve,reject)=>{

                const regex = /^data:audio\/(wav);base64,/i;
                       
                            if(!regex.test(data.message)){
                       
                              socket.emit('send_message_failed',{
                                  message:'invalid id invalid audio format.'
                                })

                                return
                       
                            }


                          uploader.upload(data.message,{
                                                 folder:data.senderId.concat('/messages/audio')
                                              },(error,uploadedResult)=>{
                                                 
                                                 if(error){
                                                     reject(error.message)
                                                 }
                         
                                                 resolve(uploadedResult?.secure_url!!)
                                         
                                               
                                              })


                
            })




            if(audioUrl?.includes('https')){


                const newChats =   await ChatModel.findOne({
                    $or:[
                        {
                        chatID:data.senderId.concat(data.receiverId)
                        },
                        {
                         chatID:data.receiverId.concat(data.senderId)
                        }
                    ]
                })
             
                
             
             
                const newChat = new ChatModel({
                 chatID:data.senderId.concat(data.receiverId),
                 userOneID:{
                     userId:data.senderId,
                     userName:isSenderValid.lastName.concat(' ').concat(isSenderValid.fullName),
                     userProfile:senderProfile
                 },
                 userTwoID:{
                     userId:data.receiverId,
                     userName:isReceiverValid.lastName.concat(' ').concat(isReceiverValid.fullName),
                     userProfile:receiverProfile
                 },
                 messages:[{messageType:data.messageType,
                     message:audioUrl,
                     timeStamp:data.timeStamp,
                     sender:data.senderId,
                     receiver:data.receiverId
                 }]
             })
             
             await newChat.save()
             
             
              const receiverSocket = await UserConnectionsModel.findOne({
                 userId:data.receiverId
             })
             
             
             
             // socket.emit('new_message',newChat)
             socketIO.to(receiverSocket?.connectionId!!).emit('new_message',newChat)


  return
            }
           

    

       
       return


       }





           

            const newChat = new ChatModel({
                chatID:data.senderId.concat(data.receiverId),
                userOneID:{
                    userId:data.senderId,
                    userName:isSenderValid.lastName.concat(' ').concat(isSenderValid.fullName),
                    userProfile:senderProfile
                },
                userTwoID:{
                    userId:data.receiverId,
                    userName:isReceiverValid.lastName.concat(' ').concat(isReceiverValid.fullName),
                    userProfile:receiverProfile
                },
                messages:[{messageType:data.messageType,message:data.message,
                    timeStamp:data.timeStamp,
                    sender:data.senderId,
                    receiver:data.receiverId
                }]
            })

            await newChat.save()


             const receiverSocket = await UserConnectionsModel.findOne({
                userId:data.receiverId
            })



             socket.emit('new_message',newChat)
            socketIO.to(receiverSocket?.connectionId!!).emit('new_message',newChat)
        }




        
    } catch (error:any) {
       
             socket.emit('send_message_failed',{
                message:error.message
             }) 

             console.log(error.message)
    }



}

