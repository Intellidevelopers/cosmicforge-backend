import SERVER_STATUS from "../../../util/interface/CODE"
import { ResponseBodyProps } from "../../../util/interface/ResponseBodyProps"
import TypedRequest from "../../../util/interface/TypedRequest"
import TypedResponse from "../../../util/interface/TypedResponse"
import jwt from 'jsonwebtoken'
import passwordChecker from 'bcryptjs'
import sendMail from "../../../config/mail/nodeMailer"
import newUserModel from "../../newUser/model/newUserModel"
import generateOTP from "../../../util/otpGenerator"
import resetPasswordModel from "../../newUser/model/resetPasswordModel"
import passwordHasher from 'bcryptjs'

export interface LoginRequestBodyProps {
    email: string,
    password: string
}

export interface ResetPasswordProps {
    email: string,
    otp?: number,
    password?: string
}


export const loginUser = async (req: TypedRequest<LoginRequestBodyProps>, res: TypedResponse<ResponseBodyProps>) => {

    try {

       // console.log(await newUserModel.find())
        const { email, password } = req.body

        if (!email || !password) {

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: "Login Message",
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: "email and password fields are required to continue.",
            })
            return
        }

        const userAccount = await newUserModel.findOne({ email })

        if (!userAccount) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: "Login Message",
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: "Invalid account detials provided.",
            })
            return
        }

        const passwordValid = await passwordChecker.compare(password, userAccount?.password!!)

        if (!passwordValid) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: "Login Message",
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: "Invalid account detials provided.",
            })
            return
        }

        const token = jwt.sign({ ...userAccount.toObject() }, process.env.JWT_SECRET!!, { expiresIn: '30d' })

        await sendMail({
            receiver: userAccount.email, subject: "Successfull Login.", emailData: {
                fullName: `${userAccount.fullName} ${userAccount.lastName}`
            }, template: "login-success.ejs"
        })

        res.status(SERVER_STATUS.SUCCESS).json({
            title: "Login Message",
            status: SERVER_STATUS.SUCCESS,
            successful: true,
            message: "Welcome back to cosmic",
            data: {
                ...userAccount.toObject(),
                token
            }
        })

    } catch (error: any) {

        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: "Login Message",
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "An error occured.",
            error: error.message
        })

    }


}


export const sendOtpToResetPassword = async (req: TypedRequest<ResetPasswordProps>, res: TypedResponse<ResponseBodyProps>) => {

    try {
        const { email } = req.body

        if (!email) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Password Message',
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: "Email is needed to continue."

            })

            return
        }

        const userAccount = await newUserModel.findOne({ email })
        const cachedOTP = await resetPasswordModel.findOne({ "userDetails.email": email })

        if (cachedOTP) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Password Message',
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: "User already on the process please use resend otp to get new otp if not gotten."

            })

            return
        }


        if (!userAccount) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Password Message',
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: "Invalid email provided."

            })

            return
        }

        const token = await generateOTP()

        //send otp to email
        await sendMail({
            receiver: email, emailData: {
                fullName: `${userAccount.fullName} ${userAccount.lastName}`,
                token: token
            }, subject: "Reset Password", template: "reset-password.ejs"
        })


        const cacheOTP = new resetPasswordModel({
            userDetails: {
                email,
                fullName: `${userAccount.fullName} ${userAccount.lastName}`
            },
            otpCode: token,
            expiringTime: new Date(Date.now() + 5 * 60 * 1000),

        })

        await cacheOTP.save()


        res.status(SERVER_STATUS.SUCCESS).json({
            title: 'Reset Password  Message',
            status: SERVER_STATUS.SUCCESS,
            successful: true,
            message: "Otp sent to user email"

        })




    } catch (error: any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: 'Reset Password  Message',
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful: false,
            message: "An error occured.",
            error: error.message

        })
    }

}

export const resendOtpToResetPassword = async (req: TypedRequest<ResetPasswordProps>, res: TypedResponse<ResponseBodyProps>) => {

    const { email } = req.body


    try {

        const isUserAlreadySentOtp = await resetPasswordModel.findOne({ "userDetails.email": email })

        if (!isUserAlreadySentOtp) {

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "No otp sent to user.",



            })

            return
        }

        const otpExpiringTime = new Date(isUserAlreadySentOtp?.expiringTime!!).getTime()

        if (otpExpiringTime > Date.now()) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Pasword Message',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "Otp already sent to this user and will expire in th next 5mins.",




            })

            return
        }

        //send user otp
        const otp = await generateOTP()

        await isUserAlreadySentOtp.updateOne({
            otpCode: otp,
            expiringTime: new Date(Date.now() + 5 * 60 * 1000)
        })



        sendMail({
            receiver: isUserAlreadySentOtp.userDetails?.email!!,
            subject: "Reset Password Otp",
            emailData: {
                fullName: isUserAlreadySentOtp.userDetails?.fullName,
                token: otp

            },
            template: 'reset-password.ejs'
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
            title: 'Reset Password Message',
            successful: false,
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message

        })
    }


}


export const validateResetPasswordOTP = async (req: TypedRequest<ResetPasswordProps>, res: TypedResponse<ResponseBodyProps>) => {



    try {

        const { email, otp } = req.body

        if (!email || !otp) {

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "email and otp field are needed to continue.",



            })

            return

        }
        const isUserAlreadySentOtp = await resetPasswordModel.findOne({ "userDetails.email": email })

        if (!isUserAlreadySentOtp) {

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Pssword Message.',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "No otp sent to user.",



            })

            return
        }

        if (otp !== isUserAlreadySentOtp.otpCode) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Password Mssage',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "Invalid otp provided.",
            })

            return
        }

        const otpExpiringTime = new Date(isUserAlreadySentOtp?.expiringTime!!).getTime()

        if (otpExpiringTime < Date.now()) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Password Mssage',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "Cannot validate an expired otp.",




            })

            return
        }

        await isUserAlreadySentOtp.updateOne({
            isOtpValidated: true
        })
        res.status(SERVER_STATUS.SUCCESS).json({
            title: 'Reset Password Message',
            successful: false,
            status: SERVER_STATUS.SUCCESS,
            message: "Validated otp you can continue with password reset.",
            otp
        })

    } catch (error: any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: 'Reset Password Message',
            successful: false,
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message

        })
    }


}

export const resetPassword = async (req: TypedRequest<ResetPasswordProps>, res: TypedResponse<ResponseBodyProps>) => {
    try {

        const { password, otp } = req.body

        if (!password || !otp) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "password and otp  field are needed to continue.",



            })

            return
        }

        //check if otp is validated
        const cachedOTP = await resetPasswordModel.findOne({ otpCode: otp })
        if (!cachedOTP) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "User otp not valid.",



            })

            return
        }

        //check if otp is  validated
        if (!cachedOTP.isOtpValidated) {
            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "User otp not valid.",



            })

            return
        }

        const strongPasswordPattern = /^(?=.*[A-Za-z])(?=.*[A-Z a-z\d ])(?=.*[@$!*#?.&])[A-Za-z\d@$!*.#?&]{10,}$/


        if (!strongPasswordPattern.test(password)) {

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Reset Password Message',
                successful: false,
                status: SERVER_STATUS.BAD_REQUEST,
                message: "Password must contain words, characters and numbers.",



            })
            return
        }


        const salt = await passwordHasher.genSalt(10)
        const newHashedPassword = await passwordHasher.hash(password, salt)

        await newUserModel.findOneAndUpdate({ email: cachedOTP.userDetails?.email }, {
            password: newHashedPassword
        })


        await resetPasswordModel.deleteOne({ otpCode: otp })

        res.status(SERVER_STATUS.SUCCESS).json({
            title: 'Reset Password Message',
            successful: true,
            status: SERVER_STATUS.SUCCESS,
            message: "Password successfully changed.",



        })





    } catch (error: any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: 'Reset Password Message',
            successful: false,
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            message: "An error occured.",
            error: error.message


        })

    }

}




