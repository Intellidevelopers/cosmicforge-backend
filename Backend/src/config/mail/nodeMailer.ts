import nodemailer from "nodemailer";
import path from "path";
import ejs from "ejs";

interface MailProps {
  receiver: string;
  subject: string;
  emailData: {};
  template: string;
}
const nodeMail = nodemailer.createTransport({
  host: "mail.cosmicforgehealthnet.com",
  port: 465,
  secure: true,
  auth: {
    user: "noreply@cosmicforgehealthnet.com",
    pass: "Aevy4BlOMxbp"
  }
});

//adeagbojosiah1@gmail.com
//bvvmpoeglluldhwj

const sendMail = async (data: MailProps) => {
  const emailTemplatePath = path.join(
    path.resolve(__dirname, "../../"),
    "views",
    data.template
  );

  const htmltoSend = await ejs.renderFile(emailTemplatePath, {
    data: data.emailData
  });

  return nodeMail.sendMail({
    sender: "noreply@cosmicforgehealthnet.com",
    to: data.receiver,
    subject: data.subject,
    from: "noreply@cosmicforgehealthnet.com",
     headers:{
      'Auto-Submitted':'auto-generated'
     },
    html: htmltoSend
  });
};

export default sendMail;
