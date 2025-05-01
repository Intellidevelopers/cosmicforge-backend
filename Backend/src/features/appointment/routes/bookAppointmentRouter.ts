import express from 'express'
import userAuthenticationMiddleware from '../../../middleware/userAuthenticationMiddleware'
import { bookAppointment, getSpecificDoctorAppointments } from '../controller/bookAppointmentController'


const bookAppointmentRouter = express.Router()



/**
 * @swagger
 * /api/v1/cosmicforge/user/patient/appointment/book:
 *     post:
 *        summary: A user provides doctorId,day,month,year,meridianType,hour,minutes,appointmentType,payment fields to book appointment.
 *        tags: [Patient]
 *        requestBody:
 *                 description: User data
 *                 required: true
 *                 content:   
 *                     application/json:
 *                           schema:
 *                             type: object
 *                             properties:
 *                                     doctorId: 
 *                                       type: string
 *                                       format: string
 *                                       description: doctorId.
 *                                     day: 
 *                                       type: string
 *                                       format: string
 *                                       description: day.
 *                                     month: 
 *                                       type: string
 *                                       format: string
 *                                       description: month.
 *                                     year: 
 *                                       type: string
 *                                       format: string
 *                                       description: year.
 *                                     meridianType: 
 *                                       type: string
 *                                       format: string
 *                                       enum: [am,pm]
 *                                       description: meridianType.
 *                                     hour: 
 *                                       type: string
 *                                       format: string
 *                                       description: hour.
 *                                     minutes: 
 *                                       type: string
 *                                       format: time
 *                                       description: minutes.
 *                                     appointmentType: 
 *                                       type: string
 *                                       format: string
 *                                       description: appointmentType.
 *                                       enum: [Virtual,In-Person]
 *                                     payment: 
 *                                       type: object
 *                                       properties:
 *                                            consultationFee: 
 *                                                type: string
 *                                                format: string
 *                                                description: consultationFee.
 *                                            cardType: 
 *                                                type: string
 *                                                format: string
 *                                                enum: [individual,family]
 *                                                description: cardType.
 *                                            cardFee: 
 *                                                type: number
 *                                                format: string
 *                                                description: cardFee.
 *                                            vat: 
 *                                                type: number
 *                                                format: string
 *                                                description: vat.
 *                                            total: 
 *                                                type: number
 *                                                format: string
 *                                                description: total.   
 *                                       description: payment.
 * 
 *                                   
 *        responses:
 *                200:
 *                 description: Booked successfully.
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
 * /api/v1/cosmicforge/user/medics/appointments:
 *     get:
 *        summary: Get doctor's specific appointment.
 *        tags: [Medics]
 *           
 *        responses:
 *                200:
 *                 description: Successfully fetched.
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



bookAppointmentRouter.post('/patient/appointment/book',userAuthenticationMiddleware,bookAppointment)

bookAppointmentRouter.get('/medics/appointments',userAuthenticationMiddleware,getSpecificDoctorAppointments)


export default bookAppointmentRouter