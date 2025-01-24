import swaggerJsDoc from 'swagger-jsdoc'

  const options = {
    definition:{
        openapi:'3.0.0',
        info:{
            title:"Cosmic Api Doc",
            version:'1.0.0',
        },
        components:{
   securitySchemes:{
    bearerAuth:{
        type:'http',
        scheme:'bearer',
        bearerFormat:'JWT'
    },
   },
        },
    security:[
        {
            bearerAuth:[]
        }
    ],
    },
    apis:['./src/swagger-api/*.ts','./src/features/newUser/routes/newUserRoute.ts']
}

export default swaggerJsDoc(options)