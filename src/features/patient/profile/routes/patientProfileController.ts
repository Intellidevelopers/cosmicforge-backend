import express from 'express'
import { updatePatientProfile, updateVitalSigns } from '../controller/patientProfileController'
import userAuthenticationMiddleware from '../../../../middleware/userAuthenticationMiddleware'

const patientProfileRouter = express.Router()



/**
 * @swagger
 * /api/v1/cosmicforge/user/patient/update-profile:
 *     put:
 *        summary: A user provides email, mobileNo, homeAddress, workAddress,profilePicture that he/she wants to update.
 *        tags: [Patient]
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
 *                                     homeAddress: 
 *                                       type: string
 *                                       format: string
 *                                       description: home address.
 *                                     workAddress: 
 *                                       type: string
 *                                       format: string
 *                                       description: work address.
 *                                     profilePicture: 
 *                                       type: string
 *                                       format: string
 *                                       description: profilePicture.
 *                                   
 *        responses:
 *                200:
 *                 description: Update user profile.
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
 * /api/v1/cosmicforge/user/patient/update-vital-signs:
 *     put:
 *        summary: A user provides bloodPressure,bodyTemperature,oxygenSaturation,weight,height,profileType,dateOfBirth,gender that he/she wants to update.
 *        tags: [Patient]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:   
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     bloodPressure: 
 *                                       type: string
 *                                       format: string
 *                                       description: bloodPressure.
 *                                     bodyTemperature: 
 *                                       type: string
 *                                       format: string
 *                                       description: bodyTemperature.
 *                                     homeAddress: 
 *                                       type: string
 *                                       format: string
 *                                       description: bodyTemperature.
 *                                     oxygenSaturation: 
 *                                       type: string
 *                                       format: string
 *                                       description: oxygenSaturation.
 *                                     weight: 
 *                                       type: string
 *                                       format: string
 *                                       description: weight.
 *                                     height: 
 *                                       type: string
 *                                       format: string
 *                                       description: height.
 *                                     profileType: 
 *                                       type: string
 *                                       format: string
 *                                       description: profileType.
 *                                       enum: [personal, family]
 *                                       examples: 
 *                                          - description: family
 *                                            value: family
 *                                          - description: personal
 *                                            value: personal
 *                                       oneOf:
 *                                        - example: family
 *                                        - example: personal
 *                                     gender: 
 *                                       type: string
 *                                       format: string
 *                                       description: gender.
 *                                       enum: [male,female]
 *                                     dateOfBirth: 
 *                                       type: string
 *                                       format: string
 *                                       description: date of birth.
 * 
 *                                   
 *        responses:
 *                200:
 *                 description: Update user profile.
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



patientProfileRouter.put('/update-profile',userAuthenticationMiddleware,updatePatientProfile)

patientProfileRouter.put('/update-vital-signs',userAuthenticationMiddleware,updateVitalSigns)


export default patientProfileRouter