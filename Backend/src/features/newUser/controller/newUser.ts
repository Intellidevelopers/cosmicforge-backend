import SERVER_STATUS from "../../../util/interface/CODE"
import { ResponseBodyProps } from "../../../util/interface/ResponseBodyProps"
import TypedRequest from "../../../util/interface/TypedRequest"
import TypedResponse from "../../../util/interface/TypedResponse"



import UsersModel from '../../../features/newUser/model/newUserModel'
import OTPModel from '../model/otpVerificationModel'
import generateOTP from "../../../util/otpGenerator"
import sendMail from "../../../config/mail/nodeMailer"
import passwordHasher from 'bcryptjs'
import jwt from 'jsonwebtoken'



export interface RequestBodyProps {
    email: string
}

export interface ValidateOTPRequestProps {
    email: string,
    otp: number
}

export interface CompleteRegistrationRequestProps {
    fullName: string,
    lastName: string,
    password: string,
    otp: number
}

export const registerNewUser = async (req: TypedRequest<RequestBodyProps>, res: TypedResponse<ResponseBodyProps>) => {




    try {


        const { email } = req.body

        

        if (!email) {
            return res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: "Register User Message",
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: "Email field is required to continue."

            })
        }

        console.log(await UsersModel.deleteMany())
        const isEmailAlreadyRegistered = await UsersModel.findOne({ email })

        if (isEmailAlreadyRegistered) {
            return res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: "Register User Message",
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: "Email provided already registered."
            })
        }

        // await OTPModel.deleteMany()

        const isUserAlreadySentOtp = await OTPModel.findOne({ "userDetails.email": email })

        if (isUserAlreadySentOtp) {

            return res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: "Register User Message",
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: "Already sent otp to email and verify otp and complete rigisteration."
            })

            return
        }

        //send user otp
        const otp = await generateOTP()

        const storeOTP = new OTPModel({
            userDetails: {
                email
            },
            expiringTime: new Date(Date.now() + 3 * 60 * 1000),
            otpCode: otp

        })

        await storeOTP.save()

        sendMail({
            receiver: email,
            subject: "Otp Code For Registration",
            emailData: {
                email,
                otp
            },
            template: 'send-user-otp.ejs'
        }).then(result => {
            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Register new user message',
                successful: true,
                status: SERVER_STATUS.SUCCESS,
                message: "Otp sent to user.",


            })

        }).catch(err => {
            res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
                title: 'Register new user message',
                successful: false,
                status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
                message: "An error occured.",
                error: err.message

            })
        })

    } catch (error: any) {

        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: 'Register new user message',
            successful: false,
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message

        })


    }
}

export const resendOTP = async (req: TypedRequest<RequestBodyProps>, res: TypedResponse<ResponseBodyProps>) => {

    const { email } = req.body


    try {

        const isUserAlreadySentOtp = await OTPModel.findOne({ "userDetails.email": email })

        if (!isUserAlreadySentOtp) {

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Register new user message',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "No otp sent to user.",



            })

            return
        }

        const otpExpiringTime = new Date(isUserAlreadySentOtp?.expiringTime!!).getTime()

        if (otpExpiringTime > Date.now()) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Register new user message',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "Otp already sent to this user and will expire in th next 3mins.",




            })

            return
        }

        //send user otp
        const otp = await generateOTP()

        await isUserAlreadySentOtp.updateOne({
            otpCode: otp,
            expiringTime: new Date(Date.now() + 3 * 60 * 1000)
        })



        sendMail({
            receiver: isUserAlreadySentOtp.userDetails?.email!!,
            subject: "Otp Code For Registration",
            emailData: {
                email,
                otp
            },
            template: 'send-user-otp.ejs'
        }).then(result => {
            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Register new user message',
                successful: true,
                status: SERVER_STATUS.SUCCESS,
                message: "Otp sent to user.",


            })
        }).catch(err => {
            res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
                title: 'Register new user message',
                successful: false,
                status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
                message: "An error occured.",
                error: err.message

            })
        })






    } catch (error: any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: 'Register new user message',
            successful: false,
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message

        })
    }


}


export const validateOTP = async (req: TypedRequest<ValidateOTPRequestProps>, res: TypedResponse<ResponseBodyProps>) => {



    try {

        const { email, otp } = req.body

        const isUserAlreadySentOtp = await OTPModel.findOne({ "userDetails.email": email })

        if (!isUserAlreadySentOtp) {

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Otp validation message',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "No otp sent to user.",



            })

            return
        }

        if (otp !== isUserAlreadySentOtp.otpCode) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Otp validation message',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "Invalid otp provided.",
            })

            return
        }

        await isUserAlreadySentOtp.updateOne({
            isOtpValidated: true
        })
        res.status(SERVER_STATUS.SUCCESS).json({
            title: 'Otp validation message',
            successful: false,
            status: SERVER_STATUS.SUCCESS,
            message: "Validated otp you can continuel with registration.",
            otp
        })

    } catch (error: any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: 'Register new user message',
            successful: false,
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message

        })
    }


}
export const completeRegistrationProcess = async (req: TypedRequest<CompleteRegistrationRequestProps>, res: TypedResponse<ResponseBodyProps>) => {



    try {
        const { fullName, lastName, password, otp } = req.body


        const otpData = await OTPModel.findOne({ otpCode: otp })

        if (!otpData) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Complete registration message.',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "Invalid otp provided.",


            })
            return
        }

        if (!otpData.isOtpValidated) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Complete registration message.',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "Otp not validated please validate otp.",


            })
            return
        }


        const userEmail = otpData.userDetails?.email
        const userAlreadyExistWithEmail = await UsersModel.find({
            email: userEmail
        })

        if (!userAlreadyExistWithEmail) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Complete registration message.',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "Can not register this email at this time.",


            })

            return
        }
        const salt = await passwordHasher.genSalt(10)
        const hashedPassword = await passwordHasher.hash(password, salt)

        const newUser = new UsersModel({
            fullName,
            lastName,
            email: userEmail,
            password: hashedPassword
        })

        await newUser.save()

        const token = jwt.sign({ ...newUser.toObject() }, process?.env?.JWT_SECRET!!, { expiresIn: '30d' })

        await OTPModel.deleteOne({ "userDetails.email": userEmail })

        res.status(SERVER_STATUS.SUCCESS).json({
            title: 'Complete registration message.',
            successful: false,
            status: SERVER_STATUS.SUCCESS,
            message: "Sucvessfully registered welcome on board!!!",
            data: {
                ...newUser.toObject(),
                token
            }

        })

    } catch (error: any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: 'Complete registration message.',
            successful: false,
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message

        })
    }
}


