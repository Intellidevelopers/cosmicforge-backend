import  Socket  from "socket.io";
import { AuthMiddlewareProps } from "../../middleware/userAuthenticationMiddleware";


export interface TypedSocket<T> extends Socket.Socket {
    user?:T,
    on<K extends string>(event:K | 'message'|'perform-diagnosis',callback:(data:any)=>void):this,
    emit<J extends string>(event:J | 'message'|'diagnosis'|'diagnosis-failed'|'all-diagnisis',data:any):boolean
}