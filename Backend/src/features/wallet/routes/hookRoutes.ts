
import express from 'express'
import { confirmPaymentAndSettleAccount } from '../webhook/paymentWebHook'


const settleAccountRoute = express.Router()



settleAccountRoute.post('/settleAccount',confirmPaymentAndSettleAccount)




export default settleAccountRoute