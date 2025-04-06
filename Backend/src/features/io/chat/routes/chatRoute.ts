import express from 'express'
import userAuthenticationMiddleware from '../../../../middleware/userAuthenticationMiddleware'
import TypedResponse from '../../../../util/interface/TypedResponse'
import { ResponseBodyProps } from '../../../../util/interface/ResponseBodyProps'
import SERVER_STATUS from '../../../../util/interface/CODE'
import ChatModel from '../model/chatModel'
import TypedRequest from '../../../../util/interface/TypedRequest'

const  chatRouter =  express.Router()


chatRouter.get('/all',userAuthenticationMiddleware,async(req:TypedRequest<any>,res:TypedResponse<ResponseBodyProps>)=>{ 
    
    const userId = req.user?._id


    try {

        const chats = await  ChatModel.find({
        $or:[
           {
            'userOneID.userId':userId
           } 
           ,
           {
            'userTwoID.userId':userId
           } 
        ]
        })

         


    res.status(SERVER_STATUS.SUCCESS).json({
        title:'User Chats',
        status:SERVER_STATUS.SUCCESS,
        successful:true,
        message:'successfully fetched.',
        data:chats
    })


        
    } catch (error:any) {

        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title:'User Chats',
            status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful:false,
            message:'An error occured',
            error:error.message
        })
        
    }

 
  
})


export default chatRouter