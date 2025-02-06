import express from 'express'
import loginRouter from '../features/login/routes/loginRouter'
import signUpRouter from '../features/newUser/routes/newUserRoute'
import medicalPersonnelProfileRouter from '../features/medicalPersonnel/profile/routes/profileRoute'

const mainRouter =  express.Router()

mainRouter.use('/user',signUpRouter)

mainRouter.use('/user',loginRouter)

mainRouter.use('/user/medics',medicalPersonnelProfileRouter)


export default mainRouter