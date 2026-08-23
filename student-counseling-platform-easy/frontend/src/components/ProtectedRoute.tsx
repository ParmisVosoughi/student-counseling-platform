import {Navigate,Outlet} from 'react-router-dom'
import {useAuth} from '../contexts/AuthContext'
import {Spinner} from './ui'
import type {Role} from '../types'
export default function ProtectedRoute({roles}:{roles?:Role[]}){const {user,loading}=useAuth();if(loading)return <Spinner/>;if(!user)return <Navigate to="/login" replace/>;if(roles&&!roles.includes(user.role))return <Navigate to="/" replace/>;return <Outlet/>}
