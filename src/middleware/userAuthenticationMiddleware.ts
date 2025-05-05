import express from "express";
import TypedResponse from "../util/interface/TypedResponse";
import { ResponseBodyProps } from "../util/interface/ResponseBodyProps";
import SERVER_STATUS from "../util/interface/CODE";
import jwt  from 'jsonwebtoken'
import newUserModel from "../features/newUser/model/newUserModel";
import TypedRequest from "../util/interface/TypedRequest";


export interface  AuthMiddlewareProps{
    _id:string,
    email:string,
    fullName: string,
    lastName: string,
    password: string,
    role:string
}


 export default async  (req:TypedRequest<{}>,res:TypedResponse<ResponseBodyProps>,next:express.NextFunction) =>{
 
    try{
    const authHeader = req.headers.authorization 

    if(!authHeader){

        res.status(SERVER_STATUS.UNAUTHORIZED).json({
            title:"Aunthentication Message",
            status:SERVER_STATUS.UNAUTHORIZED,
            successful:false,
            message:"Authorization header is needed to continue."
            
        })

        return
    }
  
    const token  =  authHeader?.split(' ')[1]

    if(!token){
        res.status(SERVER_STATUS.BAD_REQUEST).json({
            title:"Aunthentication Message",
            status:SERVER_STATUS.BAD_REQUEST,
            successful:false,
            message:"Invalid token provided."
            
        })
    }

     
     const validToken = jwt.verify(token,process.env?.JWT_SECRET!!) as AuthMiddlewareProps
  const isUserValid = await newUserModel.findOne({_id:validToken._id})

   if(!isUserValid){
    res.status(SERVER_STATUS.Forbidden).json({
        title:"Aunthentication Message",
        status:SERVER_STATUS.Forbidden,
        successful:false,
        message:"Invalid token provided.",
       
    })
    return
   }
 
    req.user = validToken
    next()
}catch(error:any){
    res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
        title:"Aunthentication Message",
        status:SERVER_STATUS.INTERNAL_SERVER_ERROR,
        successful:false,
        message:"An error occured.",
         error:error.message
    })
}
 }