
import express from 'express'
import userAuthenticationMiddleware from '../../../../middleware/userAuthenticationMiddleware'
import { getDepartments, getDepartmentsForLadingPage } from '../controller/doctorDeparmentController'

const doctorDepartmentRouter = express.Router()


doctorDepartmentRouter.get('/doctor/departments',userAuthenticationMiddleware,getDepartments)

doctorDepartmentRouter.get('/doctor/departments',userAuthenticationMiddleware,getDepartments)

doctorDepartmentRouter.get('/doctor/departments/all',getDepartmentsForLadingPage)



export default doctorDepartmentRouter