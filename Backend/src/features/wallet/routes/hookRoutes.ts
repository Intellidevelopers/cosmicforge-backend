
import express from 'express'
import { confirmPaymentAndSettleAccount, getWalletById } from '../webhook/paymentWebHook'
import userAuthenticationMiddleware from '../../../middleware/userAuthenticationMiddleware'


const settleAccountRoute = express.Router()



settleAccountRoute.post('/settleAccount',confirmPaymentAndSettleAccount)

settleAccountRoute.get('/details',userAuthenticationMiddleware,getWalletById)




export default settleAccountRoute