
import express from 'express'
import userAuthenticationMiddleware from '../../../../middleware/userAuthenticationMiddleware'
import { getDepartments, getDepartmentsForLadingPage, getDoctorsBySpecificDepartment } from '../controller/doctorDeparmentController'

const doctorDepartmentRouter = express.Router()


doctorDepartmentRouter.get('/doctor/departments',userAuthenticationMiddleware,getDepartments)

doctorDepartmentRouter.get('/doctor/departments',userAuthenticationMiddleware,getDepartments)

doctorDepartmentRouter.get('/doctor/departments/all',getDepartmentsForLadingPage)

doctorDepartmentRouter.post('/doctor/department/all',userAuthenticationMiddleware,getDoctorsBySpecificDepartment)


export default doctorDepartmentRouter