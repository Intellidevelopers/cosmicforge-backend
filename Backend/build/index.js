"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const dotenv_1 = __importDefault(require("dotenv"));
const swagger_ui_express_1 = __importDefault(require("swagger-ui-express"));
const http_1 = __importDefault(require("http"));
const socket_io_1 = __importDefault(require("socket.io"));
const socketInitialization_1 = __importDefault(require("./src/features/io/socketInitialization"));
const path_1 = __importDefault(require("path"));
const swaggersetup_1 = __importDefault(require("./src/config/api-docummentation/swaggersetup"));
const databaseConfig_1 = require("./src/config/database/databaseConfig");
const cors_1 = __importDefault(require("cors"));
const routes_1 = __importDefault(require("./src/routes/routes"));
const errorHandlerMiddleware_1 = require("./src/middleware/errorHandlerMiddleware");
dotenv_1.default.config();
const app = (0, express_1.default)();
const server = http_1.default.createServer(app);
const io = new socket_io_1.default.Server(server, {
    cors: {
        origin: '*',
        methods: ['GET', 'POST']
    }
});
(0, socketInitialization_1.default)(io);
app.use('/api-docs', swagger_ui_express_1.default.serve, swagger_ui_express_1.default.setup(swaggersetup_1.default));
app.set("view engine", 'ejs');
app.set('views', './src/views');
app.use((0, cors_1.default)());
app.use(express_1.default.json({ limit: '50mb' }));
app.use(express_1.default.urlencoded({ extended: true, limit: '50mb' }));
app.use('/api/v1/cosmicforge/', routes_1.default);
app.get('/', (req, res) => {
    res.render(path_1.default.join(__dirname, 'src', 'views', 'reset-password.ejs'), {
        data: {
            fullName: "Agwu Emmanuel",
            token: 129099
        }
    });
});
app.use(errorHandlerMiddleware_1.errorHandler);
const PORT = process.env.PORT || 3010;
(0, databaseConfig_1.connectDB)().then(res => {
    server.listen(PORT, () => {
        console.log('on port 3010 h gg dgdg gg hhh');
        /* const d = jwt.verify('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2N2ExZjliZDlkZDI4ODNiMWQ4NjRhZjYiLCJmdWxsTmFtZSI6IiBFbW1hbnVlbCIsImxhc3ROYW1lIjoiQWd3dSIsImVtYWlsIjoiYmVuYWd1NDc3QGdtYWlsLmNvbSIsInBhc3N3b3JkIjoiJDJhJDEwJEtma2xmWnJnVjB0T1B3RDM0ZUIuRHVFL2FzZzh3ZEV3cXI3SnFzZlZabDhkUWoxL2VNekdpIiwicm9sZSI6ImNsaWVudCIsIl9fdiI6MCwiaWF0IjoxNzM4ODYwNTE2LCJleHAiOjE3NDE0NTI1MTZ9.UzuBVoY2i62HMwB1lHBtJUT5awC86YqTxTdgAgDAFPg',process.env?.JWT_SECRET!! ) as AuthMiddlewareProps
       console.log(
         d._id
         )*/
        /* let buffer:any = null
       stream.on('data',(data)=>{
         console.log(data.toLocaleString())
         
         buffer = data
       }).on('end',(d:any)=>{
         console.log(d)
         console.log('ended')
     
           
       })*/
        /*const t =uploadImage.upload_stream({folder:'userOne'},(err:any,res:any)=>{
      
          
            
            
             if(err){
              console.log('error comming.')
              console.log(err)
              return
             }
             console.log(t.writable)
             stream.on('end',()=>{
              console.log('ende.....')
              stream.pipe(t).on('finish',(e:any)=>{
                console.log('dobe')
                console.log(e)
               }).on('error',()=>{
                console.log('reeror')
               })
             })
               console.log(res)
            
        }).end(stream)*/
        /*sendMail({receiver:"benagu477@gmail.com",subject:"Cosmic Tech Email verification.",message:"your otp is:3020"}).then(res=>{
          console.log(res.response.split(' ')[1] ==="2.0.0")
        }).catch(err=>{
          console.log(err)
        })*/
    });
}).catch(err => {
    console.log(err);
    process.exit();
});
