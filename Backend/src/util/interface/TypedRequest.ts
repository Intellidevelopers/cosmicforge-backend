import express from "express";



export default interface TypedRequest<T>  extends  express.Request{

    body:T,
  
}