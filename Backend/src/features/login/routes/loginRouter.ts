import express from 'express'
import { LoginRequestBodyProps, loginUser, resendOtpToResetPassword, resetPassword, sendOtpToResetPassword, validateResetPasswordOTP } from '../controller/login'
import TypedRequest from '../../../util/interface/TypedRequest'
import TypedResponse from '../../../util/interface/TypedResponse'
import { ResponseBodyProps } from '../../../util/interface/ResponseBodyProps'



/**
 * @swagger
 * /api/v1/cosmicforge/user/login:
 *     post:
 *        summary: Complete the registration process with validated otp.
 *        tags: [Login]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:   
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     email: 
 *                                       type: email
 *                                       description: fullName required.
 *                                    
 *                                     password: 
 *                                       type: string
 *                                       description: password required .
 *                                    
 *                             required:
 *                               -email
 *                               -password
 *                              
 *        responses:
 *                200:
 *                 description: Login user after providing valid details.
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
 * /api/v1/cosmicforge/user/reset-password-otp:
 *     post:
 *        summary: A user provide email  and he/she is sent an otp code.
 *        tags: [Forgot Password]
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
 *                                       description: A email required to send otp for reseting password.
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
 * /api/v1/cosmicforge/user/resend-reset-password-otp:
 *     post:
 *        summary: This will resend otp to user.
 *        tags: [Forgot Password]
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
 *                                       description: A email required to send otp for reseting password.
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
 * /api/v1/cosmicforge/user/validate-reset-password-otp:
 *     post:
 *        summary: This will validate the otp for reserting user password.
 *        tags: [Forgot Password]
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
 *                                     otp: 
 *                                       type: number
 *                                       format: password
 *                                       description: Otp needed to continue.
 *                          
 *                             required:
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
 * /api/v1/cosmicforge/user/reset-password:
 *     post:
 *        summary: Reset usr password when valid otp is provided.
 *        tags: [Forgot Password]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:   
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     password: 
 *                                       type: string
 *                                       description: password required .
 *                                     otp:
 *                                       type: number
 *                                       description: otp validated otp
 *                             required:
 *                               -password
 *                               -otp
 *        responses:
 *                200:
 *                 description: User sent a successful response message.
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




const loginRouter =  express.Router()


loginRouter.post("/login",(req:TypedRequest<LoginRequestBodyProps>,res:TypedResponse<ResponseBodyProps>)=>{
    loginUser(req,res)
})

loginRouter.post('/reset-password-otp',sendOtpToResetPassword)

loginRouter.post('/resend-reset-password-otp',resendOtpToResetPassword)

loginRouter.post('/validate-reset-password-otp',validateResetPasswordOTP)

loginRouter.post('/reset-password',resetPassword)




export default loginRouter