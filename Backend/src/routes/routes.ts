import express from 'express'
import loginRouter from '../features/login/routes/loginRouter'
import signUpRouter from '../features/newUser/routes/newUserRoute'

const mainRouter =  express.Router()

mainRouter.use('/user',signUpRouter)

mainRouter.use('/user',loginRouter)


export default mainRouter