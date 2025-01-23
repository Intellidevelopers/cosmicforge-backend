import swaggerJsDoc from 'swagger-jsdoc'
 import express from 'express'
import { registerNewUser, RequestBodyProps } from '../controller/newUser'
import TypedRequest from '../../../util/interface/TypedRequest'
import TypedResponse from '../../../util/interface/TypedResponse'
import { ResponseBodyProps } from '../../../util/interface/ResponseBodyProps'

 const route = express.Router()

  const options = {
    definition:{
        swagger:'2.0',
        info:{
            title:"Cosmic Api doc",
            version:'1.0.0',
        },
        components:{
   securitySchemes:{
    bearerAuth:{
        type:'http',
        scheme:'bearer',
        bearerFormat:'JWT'
    },
   },
        },
    security:[
        {
            bearerAuth:[]
        }
    ],
    },
    path:{
        '/register-user':{
            post:{
                summary:"Register A new user.",
                responses:{
                  200:{
                    discription:"A user provide email otp sent to user."
                  }
                }
            }
        }
    },
    apis:['./src/routes/*.ts']

}

export const newUserSwaggerJsDoc = swaggerJsDoc(options)



/**
 * @swagger
 * /api/v1/cosmicforge/user/signup:
 *     post:
 *        summary: A user provide email  and he/she is sent an otp code.
 *        tags: [User]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:   
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     email: 
 *                                       type: string
 *                                       format: email
 *                                       description: A email required to send otp for verification.
 *                           required:
 *                               -email
 *        responses:
 *                200:
 *                 description: User sent otp after providing a valid email
 *        content:
 *           application/json:
 *                shema:
 *                     type: object
 *                     properties:
 *                         email:
 *                            type: string
 *                            format: email
 *                    
 * 
 *        
 *            
 *  
 * 
 */

/**
 * @swagger
 * /getData:
 *     get:
 *        summary: Receive user detail such as email and send user otp code.
 *        tags: [User]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:   
 *                     application/json:
 *                           schema:
 *                             type: object
 *                           properties:
 *                                     email: 
 *                                       type: string
 *                                       format: email
 *                                       description: A email required to send otp for verification.
 *                           required:
 *                               -email
 *                                       
 *        responses:
 *                200:
 *                 description: User sent otp after providing a valid email
 *        content:
 *         application/json:
 *                shema:
 *                   type: object
 *         items:
 *           $ref:'#/component/schemas/User/signup
 *         parameters: ['email']
 * 
 *  
 * 
 */



route.post('/signup',(req:TypedRequest<RequestBodyProps>,res:TypedResponse<ResponseBodyProps>)=>{
         registerNewUser(req,res)
})



export default route