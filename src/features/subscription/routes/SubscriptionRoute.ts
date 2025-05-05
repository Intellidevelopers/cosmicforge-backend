import express from 'express'
import userAuthenticationMiddleware from '../../../middleware/userAuthenticationMiddleware'
import { getSubscription, updateSubscription } from '../controller/SubscriptionController'

const subscriptionRouter =   express.Router()


subscriptionRouter.get('',userAuthenticationMiddleware,getSubscription)

subscriptionRouter.post('/update',userAuthenticationMiddleware,updateSubscription)

export default subscriptionRouter