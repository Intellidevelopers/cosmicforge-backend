import SERVER_STATUS from "../../../../util/interface/CODE"
import { ResponseBodyProps } from "../../../../util/interface/ResponseBodyProps"
import TypedRequest from "../../../../util/interface/TypedRequest"
import TypedResponse from "../../../../util/interface/TypedResponse"
import newUserModel from "../../../newUser/model/newUserModel"
import jwt from 'jsonwebtoken'
import MedicalPersonnelProfileModel from "../model/profileModel"
import { USER_ROLES } from "../../../../util/interface/UserRole"


export interface MedicalPersonnelRequestProps {
    email?: string,
    mobileNo?: string,
    professionalTitle?: string,
    specialization?: string,
    currentClinic?: string,
    department?: string,
    location?: string,
    profilePicture?: string,

}

export const updateProfile = async (req: TypedRequest<MedicalPersonnelRequestProps>, res: TypedResponse<ResponseBodyProps>) => {
   
    try {
        const user = req.user!!



        if (!user._id || user._id === undefined || user._id === "") {

            res.status(SERVER_STATUS.Forbidden).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.Forbidden,
                successful: false,
                message: 'You not authorized to continue.'
            })
            return
        }

        if (user.role != USER_ROLES.DOCTOR) {
            res.status(SERVER_STATUS.Forbidden).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.Forbidden,
                successful: false,
                message: 'You not authorized to continue.'
            })
            return
        }


        const { email, mobileNo, professionalTitle, specialization, currentClinic, department, location, profilePicture } = req.body

        if (!email && !mobileNo && !professionalTitle && !specialization && !currentClinic && !location && !profilePicture && !department) {

            res.status(SERVER_STATUS.BAD_REQUEST).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.BAD_REQUEST,
                successful: false,
                message: 'Either email,mobileNo,professionalTitle,specialization,currentClinic,department,location,profilePicture field is needed to continue.'
            })

            return
        }

        //update token if email is channged
        let token = null

        if (email && email !== user.email) {
            await newUserModel.findOneAndUpdate({ _id: user._id }, {
                email
            })

            const updatedTokenObject = {
                _id: user._id,
                email,
                password: user.password,
                fullName: user.fullName,
                lastName: user.lastName,
                role: user.role


            }

            token = jwt.sign(updatedTokenObject, process.env?.JWT_SECRET!!, { expiresIn: '30d' })


        }

        let userProfile = await MedicalPersonnelProfileModel.findOne({ _id: user._id })
        const userAccount = await newUserModel.findOne({ _id: user._id })

        if (userProfile) {

            userProfile.updateOne({
                profilePicture: profilePicture ?? userProfile.profilePicture,
                professionalTitle: professionalTitle ?? userProfile.professionalTitle,
                mobileNo: mobileNo ?? userProfile.mobileNo,
                specializationTitle: specialization ?? userProfile.specializationTitle,
                currentClinic: currentClinic ?? userProfile.currentClinic,
                department: department ?? userProfile.department,
                location: location ?? userProfile.location

            }, {
                returnOriginal: false
            })




            if (token) {

                const updatedProfile = {
                    ...userAccount,
                    profile: userProfile,
                    token
                }

                res.status(SERVER_STATUS.SUCCESS).json({
                    title: 'Update Profile Message',
                    status: SERVER_STATUS.SUCCESS,
                    successful: true,
                    message: 'Successfully Updated Profile',
                    data: updatedProfile

                })


                return


            }


            const convertToObject = userProfile?.toObject()

            const updatedProfile = {
                ...userAccount?.toObject(),
                profile: convertToObject



            }

            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.SUCCESS,
                successful: true,
                message: 'Successfully Updated Profile',
                data: updatedProfile

            })



            return
        }


        let createProfileforUser = new MedicalPersonnelProfileModel({
            userId: user._id,
            profilePicture,
            mobileNo,
            professionalTitle,
            specialization,
            currentClinic,
            department,
            location

        })

        await createProfileforUser.save()

        if (token) {

            const updatedProfile = {
                ...userAccount,
                profile: createProfileforUser,
                token
            }

            res.status(SERVER_STATUS.SUCCESS).json({
                title: 'Update Profile Message',
                status: SERVER_STATUS.SUCCESS,
                successful: true,
                message: 'Successfully Updated Profile',
                data: updatedProfile

            })


            return


        }




        const updatedProfile = {
            ...userAccount?.toObject(),
            profile: createProfileforUser



        }

        res.status(SERVER_STATUS.SUCCESS).json({
            title: 'Update Profile Message',
            status: SERVER_STATUS.SUCCESS,
            successful: true,
            message: 'Successfully Updated Profile',
            data: updatedProfile

        })













    } catch (error: any) {
        res.status(SERVER_STATUS.INTERNAL_SERVER_ERROR).json({
            title: 'Update Profile Message',
            status: SERVER_STATUS.INTERNAL_SERVER_ERROR,
            successful: true,
            message: 'An error occured.',
            error: error.message


        })
    }
}