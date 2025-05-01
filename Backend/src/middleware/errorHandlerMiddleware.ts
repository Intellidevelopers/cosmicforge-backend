  import express from 'express'
import TypedResponse from '../util/interface/TypedResponse'
import { ResponseBodyProps } from '../util/interface/ResponseBodyProps'
import SERVER_STATUS from '../util/interface/CODE'


 export const errorHandler = (err:Error,req:express.Request,res:TypedResponse<ResponseBodyProps>,next:express.NextFunction) =>{
    res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
        title:"Server Error",
        status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
        successful:false,
        message:'An error occurred.',
        error:err.message
    })

  next()  
}