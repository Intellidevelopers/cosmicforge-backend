import express from 'express'
import loginRouter from '../features/login/routes/loginRouter'
import signUpRouter from '../features/newUser/routes/newUserRoute'
import medicalPersonnelProfileRouter from '../features/medicalPersonnel/profile/routes/profileRoute'
import patientProfileRouter from '../features/patient/profile/routes/patientProfileController'
import rateAndReviewRouter from '../features/ratings-and-reviews/routes/ratingsAndReviewsModel'
import bookAppointmentRouter from '../features/appointment/routes/bookAppointmentRouter'
import session from 'express-session'
import { passportSetup } from '../authenticateWithProviders/google/signup_signin'
import { getGoogleAuthUserDetails, googleSignUpSignInAuthcontroller } from '../authenticateWithProviders/google/signup_signinController'
import TypedRequest from '../util/interface/TypedRequest'
import SERVER_STATUS from '../util/interface/CODE'
import { userTempRoleModel } from '../authenticateWithProviders/model/tempRoleModel'
import TypedResponse from '../util/interface/TypedResponse'
const mainRouter =  express.Router()
import {v4} from 'uuid'
import { validateUserSession } from '../features/login/controller/login'
import doctorDepartmentRouter from '../features/medicalPersonnel/department/routes/doctorDepartmentRoute'
import chatRouter from '../features/io/chat/routes/chatRoute'
import settleAccountRoute from '../features/wallet/routes/hookRoutes'
import medicalPersonnelCertificationAndUploadRouter from '../features/medicalPersonnel/certification/routes/MedicalCertAndLicenceUploadRoute'
import subscriptionRouter from '../features/subscription/routes/SubscriptionRoute'

mainRouter.use(session({
  secret:'cosmicforge',
  resave:true,
  saveUninitialized:true,
  cookie:{
    secure:false
  },

 }))

mainRouter.use('/user',signUpRouter)

mainRouter.use('/user',loginRouter)

mainRouter.use('/user/medics',medicalPersonnelProfileRouter)

mainRouter.use('/user/medics/certification',medicalPersonnelCertificationAndUploadRouter)

mainRouter.use('/user/subscription',subscriptionRouter)

mainRouter.use('/user/patient',patientProfileRouter)

mainRouter.use('/user/patient',rateAndReviewRouter)

mainRouter.use('/user',bookAppointmentRouter)

mainRouter.use('/medics/',doctorDepartmentRouter)

mainRouter.use('/user/chat',chatRouter)



mainRouter.use('/wallet',settleAccountRoute)






mainRouter.use(passportSetup.initialize())
mainRouter.use(passportSetup.session())

mainRouter.get('/auth/google',passportSetup.authenticate('google',{
    scope:['profile','email'],
    
}))

mainRouter.post('/auth/google/userRole',async(req:TypedRequest<any>,res:TypedResponse<any>)=>{
  const {userRole,authType} =  req.body
   
    await userTempRoleModel.deleteMany()
 
    const token = v4()

   await new userTempRoleModel({
    userRole,
    token,
    authType
   
   }).save()


   res.status(SERVER_STATUS.SUCCESS).json({
    data:token
   })
})

mainRouter.get('/auth/google/callback',passportSetup.authenticate('google',{
  
}),googleSignUpSignInAuthcontroller)

mainRouter.post('/auth/google/validate-user',getGoogleAuthUserDetails)


mainRouter.post('/validate-user-session',validateUserSession)


export default mainRouter