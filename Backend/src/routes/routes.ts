import express from 'express'
import loginRouter from '../features/login/routes/loginRouter'
import signUpRouter from '../features/newUser/routes/newUserRoute'
import medicalPersonnelProfileRouter from '../features/medicalPersonnel/profile/routes/profileRoute'
import patientProfileRouter from '../features/patient/profile/routes/patientProfileController'
import rateAndReviewRouter from '../features/ratings-and-reviews/routes/ratingsAndReviewsModel'
import bookAppointmentRouter from '../features/appointment/routes/bookAppointmentRouter'

const mainRouter =  express.Router()

mainRouter.use('/user',signUpRouter)

mainRouter.use('/user',loginRouter)

mainRouter.use('/user/medics',medicalPersonnelProfileRouter)

mainRouter.use('/user/patient',patientProfileRouter)

mainRouter.use('/user/patient',rateAndReviewRouter)

mainRouter.use('/user',bookAppointmentRouter)


export default mainRouter