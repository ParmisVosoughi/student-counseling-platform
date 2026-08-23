import {createContext,useContext,useEffect,useMemo,useState,ReactNode} from 'react'
import {api,setAccessToken,setAuthFailureHandler} from '../api/client'
import type {User} from '../types'
interface AuthValue{user:User|null;loading:boolean;login:(username:string,password:string)=>Promise<User>;logout:()=>Promise<void>}
const AuthContext=createContext<AuthValue|null>(null)
export function AuthProvider({children}:{children:ReactNode}){
  const [user,setUser]=useState<User|null>(null); const [loading,setLoading]=useState(true)
  useEffect(()=>{setAuthFailureHandler(()=>{setAccessToken(null);setUser(null)});api.post('/auth/refresh/').then(r=>{setAccessToken(r.data.access);setUser(r.data.user)}).catch(()=>{setAccessToken(null);setUser(null)}).finally(()=>setLoading(false));return()=>setAuthFailureHandler(null)},[])
  const login=async(username:string,password:string)=>{const r=await api.post('/auth/login/',{username,password});setAccessToken(r.data.access);setUser(r.data.user);return r.data.user as User}
  const logout=async()=>{try{await api.post('/auth/logout/')}finally{setAccessToken(null);setUser(null)}}
  const value=useMemo(()=>({user,loading,login,logout}),[user,loading])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
export function useAuth(){const c=useContext(AuthContext);if(!c) throw new Error('useAuth must be inside AuthProvider');return c}
