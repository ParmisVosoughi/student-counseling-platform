import {useState} from 'react'
import {NavLink,Outlet} from 'react-router-dom'
import {useAuth} from '../contexts/AuthContext'
import {roleLabel} from '../utils/format'

const admin=[['/','داشبورد'],['/users','کاربران'],['/supervisors','ناظران'],['/advisors','مشاوران'],['/students','دانش‌آموزان'],['/reports','گزارش‌ها']]
const supervisor=[['/','داشبورد'],['/advisors','مشاوران'],['/students','دانش‌آموزان'],['/program-reviews','بررسی منطق برنامه'],['/challenges','مشکلات دانش‌آموزان'],['/assessments','نتایج ارزیابی‌ها'],['/reports','گزارش‌ها']]
const advisor=[['/','داشبورد'],['/students','دانش‌آموزان'],['/weekly','عملکرد هفتگی'],['/assessments','نتایج ارزیابی‌ها'],['/challenges','مشکلات و چالش‌ها'],['/program-reviews','بازخورد ناظر']]
export default function AppLayout(){const {user,logout}=useAuth();const [open,setOpen]=useState(false);const items=user?.role==='ADMIN'?admin:user?.role==='SUPERVISOR'?supervisor:advisor
 return <div className="min-h-screen bg-slate-50">
   <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 lg:hidden"><button className="btn-secondary px-3" onClick={()=>setOpen(true)}>منو</button><div className="font-bold">سامانه مدیریت مشاوره</div></header>
   {open&&<div className="fixed inset-0 z-40 bg-slate-950/50 lg:hidden" onClick={()=>setOpen(false)}/>} 
   <aside className={`fixed inset-y-0 right-0 z-50 flex w-72 flex-col border-l border-slate-200 bg-white transition-transform lg:translate-x-0 ${open?'translate-x-0':'translate-x-full lg:translate-x-0'}`}>
      <div className="border-b border-slate-200 p-5"><div className="text-lg font-bold text-slate-900">سامانه مدیریت مشاوره</div><div className="mt-1 text-xs text-slate-500">مدیریت عملکرد و نظارت آموزشی</div></div>
      <nav className="flex-1 space-y-1 overflow-y-auto p-3">{items.map(([to,label])=><NavLink key={to} to={to} end={to==='/'} onClick={()=>setOpen(false)} className={({isActive})=>`block rounded-lg px-3 py-2.5 text-sm font-medium ${isActive?'bg-slate-900 text-white':'text-slate-600 hover:bg-slate-100'}`}>{label}</NavLink>)}</nav>
      <div className="border-t border-slate-200 p-4"><div className="text-sm font-semibold">{user?.full_name||user?.username}</div><div className="mt-0.5 text-xs text-slate-500">{user?roleLabel(user.role):''}</div><button className="mt-3 text-sm font-medium text-red-600" onClick={()=>logout()}>خروج از حساب</button></div>
   </aside>
   <main className="min-w-0 lg:mr-72"><div className="mx-auto max-w-[1600px] p-4 sm:p-6 lg:p-8"><Outlet/></div></main>
 </div>}
