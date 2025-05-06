import TypedRequest from "../../../util/interface/TypedRequest";
import TypedResponse from "../../../util/interface/TypedResponse";
import { ResponseBodyProps } from "../../../util/interface/ResponseBodyProps";
import SERVER_STATUS from "../../../util/interface/CODE";
import { USER_ROLES } from "../../../util/interface/UserRole";
import WalletModel from "../model/walletModel";
import { v4 } from "uuid";

import Paystack from "paystack";

interface CardPaymentInterface {
  name: string;
  number: string;
  cvv: string;
  expiry_month: string;
  expiry_year: string;
  pin: string;
  paymentMadeBy: string;
  paymentReceiver: string;
  amount: number;
  currency: "NGN";
  customerName: string;
  customerEmail: string;
}

const makePaymentWithCard = async (
  req: TypedRequest<CardPaymentInterface>,
  res: TypedResponse<ResponseBodyProps>
) => {
  const url = "https://api.korapay.com/merchant/api/v1/charges/card";

  const {
    cvv,
    expiry_month,
    expiry_year,
    name,
    number,
    paymentMadeBy,
    paymentReceiver,
    pin,
    amount,
    currency,
    customerName,
    customerEmail
  } = req.body;

  if (
    !cvv ||
    !expiry_month ||
    !expiry_year ||
    name ||
    !number ||
    !paymentMadeBy ||
    !paymentReceiver ||
    currency ||
    customerName ||
    customerEmail
  ) {
    res.status(SERVER_STATUS.BAD_REQUEST).json({
      title: "Card Payment Message",
      status: SERVER_STATUS.BAD_REQUEST,
      successful: false,
      message:
        "cvv,expiry_month,expiry_year,name,number,paymentMadeBy, paymentReceiver,currency, customerName and customerEmail fields are needed to continue. "
    });

    return;
  }

  const data = {
    reference: paymentMadeBy.concat(paymentReceiver), // must be at least 8 characters
    card: {
      name,
      number,
      cvv,
      expiry_month,
      expiry_year,
      pin // optional
    },
    amount: amount,
    currency: currency,
    redirect_url: "https://merchant-redirect-url.com",
    customer: {
      name: customerName,
      email: customerEmail
    }
  };
};

export const testFlow = async () => {
  const url = "https://api.korapay.com/merchant/api/v1/charges/card";

  const paystack_url = "https://api.paystack.co/transaction/initialize";

  const d = {
    reference: "test-card-payment-1", // must be at least 8 characters
    card: {
      name: "",
      number: "4084127883172787",
      cvv: "123",
      expiry_month: "09",
      expiry_year: "30",
      pin: "" // optional
    },
    amount: 1000,
    currency: "NGN",
    redirect_url: "https://webhook.site/3f09d5de-3642-4ce7-ae10-dc7579532494",
    customer: {
      name: "John Doe",
      email: "johndoe@korapay.com"
    }
  };

  const paystackData = {
    amount: Number(100 * 100).toString(),
    currency: "NGN",
    channel: ["card"],
    email: "joe@gmail.com"
  };

  try {
    fetch(paystack_url, {
      method: "Post",
      headers: {
        authorization: "Bearer"
          .concat(" ")
          .concat(process.env.paystack_secret!!),
        "Content-Type": "application/json"
      },
      body: JSON.stringify(paystackData)
    })
      .then(res => {
        return res.json();
      })
      .then(
        (result: {
          status: boolean;
          message: string;
          "data": {
            "authorization_url": string;
            "access_code": string;
            "reference": string;
          };
        }) => {
          if (result.status) {
            fetch(
              `https://api.paystack.co/transaction/verify/${result.data
                .reference}`,
              {
                method: "get",
                headers: {
                  authorization: "Bearer"
                    .concat(" ")
                    .concat(process.env.paystack_secret!!),
                  "Content-Type": "application/json"
                }
              }
            )
              .then(res => {
                return res.json();
              })
              .then(r => {
                console.log(r);
              })
              .catch(console.log);
          }
        }
      )
      .catch(console.log);

    //  const data = await encryptAES256(JSON.stringify(d))
    //console.log(data)

    /**
 *  fetch(url,{
        method:'post',
        headers:{
         Authorization:` Bearer ${process.env.kora_payment_gateway_sec}` 
        },
        
        body:"{charge_data:'jdjd'}"
    }).then(res=>{
        return res.json()
    }).then((result)=>{
        console.log(result)
    }).catch(err=>{
        console.log(err)
    })
 */

    /*const curlCommand =  `  curl --request POST \   --url https://api.korapay.com/merchant/api/v1/charges/card        --header  'Authorization:  Bearer ${process.env.kora_payment_gateway_sec}' \  --data '{ 'charge_data':'${data}' }'  `

    childProcess.exec(curlCommand,(err,stdout,stderr)=>{
        if(err){
            console.log(err)
            return
        }
        console.log(stdout)
    })*/
    /**
     * curl --request POST \
     --url https://api.korapay.com/merchant/api/v1/charges/card \
     --header 'Authorization: Bearer sk_test_hf3Kz9TLbscoR7Nwt1Log1B2xHaF5ugrUKmdwmh8' \
     --data '{
        "charge_data": c62ac600880756fa9456e812dbbaccc8:14ed28362057615390765db7eb6a9f4630f12d23c67ad462621cd7e8cc:f2197fe1911162010cefa3038a12188f}'
     */
  } catch (e) {}
};




export const withdrawBallance = async (
  req: TypedRequest<{
    type: string;
    name: string;
    account_number: string;
    bank_code: string;
    currency: string;
    amount: string;
  }>,
  res: TypedResponse<ResponseBodyProps>
) => {
  try {
    const secretKey = process.env.paystack_secret_current;

    const url = "https://api.paystack.co/transferrecipient";

    const user = req.user;

    if (!user) {
      res.status(SERVER_STATUS.Forbidden).json({
        title: "Wallet  Message",
        status: SERVER_STATUS.Forbidden,
        successful: false,
        message: "Forbidden to access this feature."
      });

      return;
    }

    if (user && user.role !== USER_ROLES.DOCTOR) {
      res.status(SERVER_STATUS.UNAUTHORIZED).json({
        title: "Wallet  Message",
        status: SERVER_STATUS.UNAUTHORIZED,
        successful: false,
        message: "Forbidden to access this feature."
      });

      return;
    }

    const {
      type,
      name,
      account_number,
      bank_code,
      currency,
      amount
    } = req.body;


    // console.log(name)
    if (
      !type ||
      !name ||
      !account_number ||
      !bank_code ||
      !currency ||
      !amount
    ) {
      res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Withdraw Wallet",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message:
          "type,name,account_number,bank_code,currency and amount fields are required to continue."
      });

      return;
    }

    const response = await fetch(url, {
      method: "POST",
      headers: {
        authorization: "Bearer".concat(" ").concat(secretKey!!)
      },
      body: JSON.stringify({ type, name, account_number, bank_code, currency })
    });

    const refResponse = await response.json();

    const transferURL = "https://api.paystack.co/transfer";

    const referencId = `CPO${v4()}`;

    const transfer = await fetch(transferURL, {
      method: "POST",
      headers: {
        authorization: "Bearer".concat(" ").concat(secretKey!!)
      },
      body: JSON.stringify({
        source: "balance",
        reference: referencId,
        recipient: refResponse.data.recipient_code,
        amount,
        reason: "tranfer to other bank account"
      })
    });

    const transferResponse = await transfer.json();


   // console.log(transferResponse)

    if (transferResponse.status) {
      const userWallet = await WalletModel.findOne({
        userId: user._id
      });

      if (userWallet) {
        await userWallet.updateOne({
          withdrawalHistories: [
            ...userWallet.withdrawalHistories,
            {
              date: Date.now(),
              withdrawalReferenceId: referencId,
              withdrawAmount: amount,
              transferReferenceID: transferResponse.data.transfer_code,
              accountName: name,
              accountNumber: account_number
            }
          ]
        });

        const updatedWallet = await WalletModel.findOne({
          userId: user._id
        });

        const d = await WalletModel.findOne({
          withdrawalHistories: {
            $elemMatch: {
              withdrawalReferenceId: referencId,
             
            }
          }
        });

       console.log("update....");
        console.log(d);

        res.status(SERVER_STATUS.SUCCESS).json({
          title: "Wallet  Message",
          status: SERVER_STATUS.SUCCESS,
          successful: true,
          message: "Succesfully fetched.",
          data: updatedWallet
        });
      } else {
        res.status(SERVER_STATUS.Forbidden).json({
          title: "Wallet  Message",
          status: SERVER_STATUS.Forbidden,
          successful: false,
          message: "Forbidden to access this feature."
        });
      }
    } else {


      res.status(SERVER_STATUS.BAD_REQUEST).json({
        title: "Wallet  Message",
        status: SERVER_STATUS.BAD_REQUEST,
        successful: false,
        message: "Internal server error try again."
      });
    }
  } catch (error:any) {
    console.log(error.message)
    res.status(SERVER_STATUS.BAD_REQUEST).json({
      title: "Wallet  Message",
      status: SERVER_STATUS.BAD_REQUEST,
      successful: false,
      message: "Internal server error try again."
    });
  }

  // paystack.transaction.
};

export const getListedBanks = async (
  req: TypedRequest<any>,
  res: TypedResponse<ResponseBodyProps>
) => {
  try {
    const user = req.user;

    if (!user) {
      res.status(SERVER_STATUS.Forbidden).json({
        title: "Wallet  Message",
        status: SERVER_STATUS.Forbidden,
        successful: false,
        message: "Forbidden to access this feature."
      });

      return;
    }

    if (user && user.role !== USER_ROLES.DOCTOR) {
      res.status(SERVER_STATUS.UNAUTHORIZED).json({
        title: "Wallet  Message",
        status: SERVER_STATUS.UNAUTHORIZED,
        successful: false,
        message: "Forbidden to access this feature."
      });

      return;
    }

    const secretKey = process.env.paystack_secret_current;

    const bankUrl = "https://api.paystack.co/bank";

    const response = await fetch(bankUrl, {
      method: "GET",
      headers: {
        authorization: "Authorization:".concat(" ").concat(secretKey!!)
      }
    });

    const banks: {
      data: [
        {
          id: number;
          name: string;
          slug: string;
          code: string;
          longcode: string;
          gateway: any;
          pay_with_bank: boolean;
          supports_transfer: boolean;
          active: boolean;
          country: string;
          currency: string;
          type: string;
          is_deleted: boolean;
        }
      ];
    } = await response.json();

    res.status(SERVER_STATUS.SUCCESS).json({
      title: "Wallet  Message",
      status: SERVER_STATUS.SUCCESS,
      successful: true,
      message: "Succesfully fetched.",
      data: banks
    });
  } catch (error) {}
};

export const verifyAccountNumber = async (
  req: TypedRequest<any>,
  res: TypedResponse<ResponseBodyProps>
) => {
  try {
    const user = req.user;

    if (!user) {
      res.status(SERVER_STATUS.Forbidden).json({
        title: "Wallet  Message",
        status: SERVER_STATUS.Forbidden,
        successful: false,
        message: "Forbidden to access this feature."
      });

      return;
    }

    if (user && user.role !== USER_ROLES.DOCTOR) {
      res.status(SERVER_STATUS.UNAUTHORIZED).json({
        title: "Wallet  Message",
        status: SERVER_STATUS.UNAUTHORIZED,
        successful: false,
        message: "Forbidden to access this feature."
      });

      return;
    }

    const secretKey = process.env.paystack_secret_current;

    console.log(req.query);

    const bankUrl = `https://api.paystack.co/bank/resolve?account_number=${req
      .query.account_number}&bank_code=${req.query.bank_code}`;

    const response = await fetch(bankUrl, {
      method: "GET",
      headers: {
        authorization: "Bearer".concat(" ").concat(secretKey!!)
      }
    });

    const account = await response.json();

    res.status(SERVER_STATUS.SUCCESS).json({
      title: "Wallet  Message",
      status: SERVER_STATUS.SUCCESS,
      successful: true,
      message: "Succesfully fetched.",
      data: account
    });
  } catch (error) {}
};



