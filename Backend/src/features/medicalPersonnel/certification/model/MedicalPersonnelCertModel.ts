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
  certificate: {
    type: mongoose.SchemaTypes.String
  },
  date: {
    type: mongoose.SchemaTypes.String
  },
  country: {
    type: mongoose.SchemaTypes.String
  },
  docummentType:{
    type: mongoose.SchemaTypes.String
  },
  documentId:{
    type: mongoose.SchemaTypes.String
  },
  documentHoldName:{
    type: mongoose.SchemaTypes.String
  },
  documentImage:{
    type: mongoose.SchemaTypes.String
  },
  pictureWithDocument:{
    type: mongoose.SchemaTypes.String
  },
  doctorImage:{
    type: mongoose.SchemaTypes.String
  },
  photoWithCertification:{
    type: mongoose.SchemaTypes.String
  },
  isVerified: {
    type: mongoose.SchemaTypes.Boolean,
    default: false
  }

});

const MedicalPersonnelLicenceSchema = new mongoose.Schema({
  fullName: {
    type: mongoose.SchemaTypes.String
  },
  license: {
    type: mongoose.SchemaTypes.String
  },
  LicenseNumber: {
    type: mongoose.SchemaTypes.String
  },
  expiration: {
    type: mongoose.SchemaTypes.String
  },
  country: {
    type: mongoose.SchemaTypes.String
  },
  documentId: {
    type: mongoose.SchemaTypes.String
  },
  documentHoldName: {
    type: mongoose.SchemaTypes.String
  },
  pictureWithDocument: {
    type: mongoose.SchemaTypes.String
  },
  docummentType: {
    type: mongoose.SchemaTypes.String
  },
  documentImage: {
    type: mongoose.SchemaTypes.String
  },
  photoWithLicence: {
    type: mongoose.SchemaTypes.String
  },
  doctorImage: {
    type: mongoose.SchemaTypes.String
  },
  isVerified: {
    type: mongoose.SchemaTypes.Boolean,
    default: false
  }
});

const MedicalPersonnelCertificationAndUploadSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.ObjectId
  },

  certificationDetails: {
    type: MedicalPersonnelCertificationSchema
  },
  licenseDetails: {
    type: MedicalPersonnelLicenceSchema
  }
});

const MedicalPersonnelCertificationAndUploadModel = mongoose.model(
  "medicalPersonnelLicenceOrCertificate",
  MedicalPersonnelCertificationAndUploadSchema
);

export default MedicalPersonnelCertificationAndUploadModel;
