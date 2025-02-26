import express from 'express'
import loginRouter from '../features/login/routes/loginRouter'
import signUpRouter from '../features/newUser/routes/newUserRoute'
import medicalPersonnelProfileRouter from '../features/medicalPersonnel/profile/routes/profileRoute'
import patientProfileRouter from '../features/patient/profile/routes/patientProfileController'
import rateAndReviewRouter from '../features/ratings-and-reviews/routes/ratingsAndReviewsModel'
import bookAppointmentRouter from '../features/appointment/routes/bookAppointmentRouter'
import session from 'express-session'
import { passportSetup } from '../authenticateWithProviders/google/signup_signin'
import { googleSignUpSignInAuthcontroller } from '../authenticateWithProviders/google/signup_signinController'
import TypedRequest from '../util/interface/TypedRequest'
import SERVER_STATUS from '../util/interface/CODE'
import { userTempRoleModel } from '../authenticateWithProviders/model/tempRoleModel'
import TypedResponse from '../util/interface/TypedResponse'
const mainRouter =  express.Router()

mainRouter.use(session({
  secret:'cosmicforge',
  resave:true,
  saveUninitialized:true,
  cookie:{
    secure:false
  },
  store:new session.MemoryStore()
 }))

mainRouter.use('/user',signUpRouter)

mainRouter.use('/user',loginRouter)

mainRouter.use('/user/medics',medicalPersonnelProfileRouter)

mainRouter.use('/user/patient',patientProfileRouter)

mainRouter.use('/user/patient',rateAndReviewRouter)

mainRouter.use('/user',bookAppointmentRouter)

mainRouter.use(passportSetup.initialize())
mainRouter.use(passportSetup.session())

mainRouter.get('/auth/google',passportSetup.authenticate('google',{
    scope:['profile','email'],
    
}))

/*mainRouter.post('/auth/google/userRole',async(req:TypedRequest<any>,res:TypedResponse<any>)=>{
  const {userRole} =  req.body
  await  userTempRoleModel.deleteMany()
  
 

   await new userTempRoleModel({
    userRole,
   }).save()


   res.sendStatus(SERVER_STATUS.SUCCESS)
})*/

mainRouter.get('/auth/google/callback',passportSetup.authenticate('google',{
  
}),googleSignUpSignInAuthcontroller)


export default mainRouter