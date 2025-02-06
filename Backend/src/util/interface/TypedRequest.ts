import {Request} from "express";
import { AuthMiddlewareProps } from "../../middleware/userAuthenticationMiddleware";



export default interface TypedRequest<T>  extends  Request   {

    body:T,
    user?:AuthMiddlewareProps
    
  
}  



