
import express from 'express'
import {getWalletById, paystackWebHookEventListener } from '../webhook/paymentWebHook'
import userAuthenticationMiddleware from '../../../middleware/userAuthenticationMiddleware'
import { getListedBanks, verifyAccountNumber, withdrawBallance } from '../controller/walletController'


const settleAccountRoute = express.Router()



settleAccountRoute.post('/settleAccount',paystackWebHookEventListener)

settleAccountRoute.get('/details',userAuthenticationMiddleware,getWalletById)

settleAccountRoute.get('/banks',userAuthenticationMiddleware,getListedBanks)

settleAccountRoute.get('/verifyAccount',userAuthenticationMiddleware,verifyAccountNumber)

settleAccountRoute.post('/withdraw',userAuthenticationMiddleware,withdrawBallance)


export default settleAccountRoute