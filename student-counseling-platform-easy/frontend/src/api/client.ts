import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
const baseURL=import.meta.env.VITE_API_BASE_URL || '/api'
export const api=axios.create({baseURL,withCredentials:true,headers:{'Content-Type':'application/json'}})
let accessToken:string|null=null
let refreshPromise:Promise<string|null>|null=null
let authFailureHandler:(()=>void)|null=null
export const setAuthFailureHandler=(handler:(()=>void)|null)=>{authFailureHandler=handler}
export const setAccessToken=(token:string|null)=>{accessToken=token}
api.interceptors.request.use((config:InternalAxiosRequestConfig)=>{if(accessToken) config.headers.Authorization=`Bearer ${accessToken}`; return config})
api.interceptors.response.use(r=>r,async(error:AxiosError)=>{
  const original:any=error.config
  if(error.response?.status===401 && original && !original._retry && !String(original.url).includes('/auth/')){
    original._retry=true
    try{
      if(!refreshPromise) refreshPromise=axios.post(`${baseURL}/auth/refresh/`,{}, {withCredentials:true}).then(r=>{setAccessToken(r.data.access);return r.data.access}).catch(()=>{setAccessToken(null);return null}).finally(()=>{refreshPromise=null})
      const token=await refreshPromise
      if(token){original.headers={...(original.headers||{}),Authorization:`Bearer ${token}`}; return api(original)}
      if(!token) authFailureHandler?.()
    }catch{authFailureHandler?.()}
  }
  return Promise.reject(error)
})
