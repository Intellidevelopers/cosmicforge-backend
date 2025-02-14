import  Socket  from "socket.io";
import { AuthMiddlewareProps } from "../../middleware/userAuthenticationMiddleware";


export interface TypedSocket<T> extends Socket.Socket {
    user?:T
}