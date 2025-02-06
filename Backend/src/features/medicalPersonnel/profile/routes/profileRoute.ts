import express from 'express'
import userAuthenticationMiddleware from '../../../../middleware/userAuthenticationMiddleware'
import {  updateProfile } from '../controller/profileController'

const medicalPersonnelProfileRouter =  express.Router()


/**
 * @swagger
 * /api/v1/cosmicforge/user/medics/update-profile:
 *     put:
 *        summary: A user provides email, mobileNo, professionalTitle, specialization, currentClinic, department, location, profilePicture that he/she wants to update.
 *        tags: [Medics]
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
 *                                       description: new email to update.
 *                                     mobileNo: 
 *                                       type: string
 *                                       format: phone
 *                                       pattern: '^\+234[0-9]{10}'
 *                                       description: mobile number to update.
 *                                     professionalTitle: 
 *                                       type: string
 *                                       format: string
 *                                       description: professional title.
 *                                     specialization: 
 *                                       type: string
 *                                       format: string
 *                                       description: professional.
 *                                     currentClinic: 
 *                                       type: string
 *                                       format: string
 *                                       description: currentClinic.
 *                                     department: 
 *                                       type: string
 *                                       format: string
 *                                       description: deparment.
 *                                     location: 
 *                                       type: string
 *                                       format: string
 *                                       description: location.
 *                                     profilePicture: 
 *                                       type: string
 *                                       format: string
 *                                       description: profilePicture.
 *                                   
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




medicalPersonnelProfileRouter.put('/update-profile',userAuthenticationMiddleware,updateProfile)



export default  medicalPersonnelProfileRouter