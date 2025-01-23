import { Send } from "express-serve-static-core";
 import express from "express";

 
export default interface TypedResponse<ResBody> extends express.Response {
    json: Send<ResBody,this>
}