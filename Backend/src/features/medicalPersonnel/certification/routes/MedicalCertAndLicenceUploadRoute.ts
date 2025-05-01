
import express from 'express'
import userAuthenticationMiddleware from '../../../../middleware/userAuthenticationMiddleware'
import { getupdloadCertificateOrLicense, updloadCertificateOrLicense } from '../controller/MedicalPersonnelCertCertController'

const medicalPersonnelCertificationAndUploadRouter = express.Router()


medicalPersonnelCertificationAndUploadRouter.post('/upload',userAuthenticationMiddleware,updloadCertificateOrLicense)

medicalPersonnelCertificationAndUploadRouter.get('/all',userAuthenticationMiddleware,getupdloadCertificateOrLicense)


export default medicalPersonnelCertificationAndUploadRouter
