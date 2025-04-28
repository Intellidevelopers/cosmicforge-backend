import mongoose from "mongoose";

const PaymentHistorySchema = new mongoose.Schema({
  paymentType: {
    type: mongoose.Schema.Types.String,
    enum: ["consultation-fee"],
    default: "consultation-fee"
  },
  paymentMadeBy: {
    type: mongoose.Schema.Types.ObjectId
  },
  paymentSentTo: {
    type: mongoose.Schema.Types.ObjectId
  },
  paymentDate: {
    type: mongoose.Schema.Types.Date
  },
  paymentReferenceId: {
    type: mongoose.Schema.Types.String
  },
  paymentStatus: {
    type: mongoose.Schema.Types.String,
    enum: ["pending", "success", "failed"]
  },
  paymentChannel: {
    type: mongoose.Schema.Types.String
  }
});

const withdrawalHistoriesSchema = new mongoose.Schema({
  date: {
    type: mongoose.Schema.Types.Date
  },
  withdrawalReferenceId: {
    type: mongoose.Schema.Types.String
  },
  transferStatus: {
    type: mongoose.Schema.Types.String,
    enum: ["pending", "success", "failed"],
    default:'pending'
  },
  transferReferenceID: {
    type: mongoose.Schema.Types.String
  },
  withdrawAmount: {
    type: mongoose.Schema.Types.String
  },
  currency: {
    type: mongoose.Schema.Types.String,
    enum: ["NGN", "USD"],
    default: "NGN"
  },
  accountName: {
    type: mongoose.Schema.Types.String
  },
  accountNumber: {
    type: mongoose.Schema.Types.String
  }
});


const walletSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.ObjectId,
    ref: "users"
  },
  amount: {
    type: mongoose.Schema.Types.Number,
    default: 0
  },
  currency: {
    type: mongoose.Schema.Types.String,
    enum: ["NGN", "US-Dollar"]
  },
  histories: [
    {
      type: PaymentHistorySchema
    }
  ],

  withdrawalHistories: 
    {
      type: [withdrawalHistoriesSchema]
    }
  
});

const WalletModel = mongoose.model("wallet", walletSchema);

export default WalletModel;
