import mongoose from "mongoose";

const MedicalPersonnelCertificationSchema = new mongoose.Schema({
  fullName: {
    type: mongoose.SchemaTypes.String
  },
  institution: {
    type: mongoose.SchemaTypes.String
  },
  certificateNo: {
    type: mongoose.SchemaTypes.String
  },
  certificateImage: {
    type: mongoose.SchemaTypes.String
  },
  date: {
    type: mongoose.SchemaTypes.String
  },
  isVerified:{
  
      type: mongoose.SchemaTypes.Boolean,
      default:false
  }
});

const MedicalPersonnelLicenceSchema = new mongoose.Schema({
  fullName: {
    type: mongoose.SchemaTypes.String
  },
  institution: {
    type: mongoose.SchemaTypes.String
  },
  licenseNo: {
    type: mongoose.SchemaTypes.String
  },
  licenseImage: {
    type: mongoose.SchemaTypes.String
  },
  date: {
    type: mongoose.SchemaTypes.String
  },
  photoWithLicence: {
    type: mongoose.SchemaTypes.String
  },
  isVerified:{
  
    type: mongoose.SchemaTypes.Boolean,
    default:false
}
});

const MedicalPersonnelCertificationAndUploadSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.ObjectId
  },

  certification: {
    type: MedicalPersonnelCertificationSchema
  },
  licence: {
    type: MedicalPersonnelLicenceSchema
  }
});

const MedicalPersonnelCertificationAndUploadModel = mongoose.model(
  "medicalPersonnelLicenceOrCertificate",
  MedicalPersonnelCertificationAndUploadSchema
);

export default MedicalPersonnelCertificationAndUploadModel;
