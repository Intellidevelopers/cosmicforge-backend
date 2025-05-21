
import express from 'express'
import userAuthenticationMiddleware from '../../../../middleware/userAuthenticationMiddleware'
import { approveDoctorLicenseVerification, getupdloadCertificateOrLicense, updloadCertificateOrLicense } from '../controller/MedicalPersonnelCertCertController'

const medicalPersonnelCertificationAndUploadRouter = express.Router()


medicalPersonnelCertificationAndUploadRouter.post('/upload',userAuthenticationMiddleware,updloadCertificateOrLicense)

medicalPersonnelCertificationAndUploadRouter.get('/all',userAuthenticationMiddleware,getupdloadCertificateOrLicense)

medicalPersonnelCertificationAndUploadRouter.get('/verification',approveDoctorLicenseVerification)

export default medicalPersonnelCertificationAndUploadRouter
